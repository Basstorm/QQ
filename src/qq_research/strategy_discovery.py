from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score, silhouette_score
from sklearn.preprocessing import StandardScaler

EXCLUDED_EXACT_FEATURES = {
    "basket_id",
    "position_id",
    "initial_position_id",
    "entry_deal",
    "exit_deal",
    "entry_order",
    "exit_order",
    "T",
    "S",
    "pnl_est",
    "exit_profit_reported",
}


def select_clustering_features(df: pd.DataFrame) -> list[str]:
    numeric = df.select_dtypes(include=["number", "bool"]).columns
    selected = []
    for column in numeric:
        if should_exclude_feature(str(column)):
            continue
        values = pd.to_numeric(df[column], errors="coerce").replace([np.inf, -np.inf], np.nan)
        if values.notna().sum() == 0 or values.nunique(dropna=True) <= 1:
            continue
        selected.append(str(column))
    return selected


def should_exclude_feature(column: str) -> bool:
    if column in EXCLUDED_EXACT_FEATURES:
        return True
    if is_absolute_price_level(column):
        return True
    if "pnl" in column or "profit" in column:
        return True
    if column.endswith("_id") and column not in {"S", "T"}:
        return True
    if column.startswith("broker_exit_") or column.startswith("utc_exit_"):
        return True
    return False


def is_absolute_price_level(column: str) -> bool:
    absolute_price_columns = {
        "entry_price",
        "exit_price",
        "initial_entry_price",
        "final_exit_price",
        "m1_path_high_max",
        "m1_path_low_min",
        "m1_path_close_last",
    }
    if column in absolute_price_columns:
        return True
    if column in {"m15_open", "m15_high", "m15_low", "m15_close"}:
        return True
    if column.startswith("m15_recent_high_") or column.startswith("m15_recent_low_"):
        return True
    if column.startswith("m15_ema_") and "_slope_" not in column:
        return True
    return False


def prepare_clustering_matrix(df: pd.DataFrame, feature_columns: list[str]) -> np.ndarray:
    matrix = df[feature_columns].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    imputed = SimpleImputer(strategy="median").fit_transform(matrix)
    low = np.nanpercentile(imputed, 1, axis=0)
    high = np.nanpercentile(imputed, 99, axis=0)
    clipped = np.clip(imputed, low, high)
    return StandardScaler().fit_transform(clipped)


def run_kmeans_sweep(
    df: pd.DataFrame,
    feature_columns: list[str],
    k_values: range = range(2, 13),
    random_state: int = 42,
) -> tuple[pd.DataFrame, dict[int, np.ndarray]]:
    x = prepare_clustering_matrix(df, feature_columns)
    labels_by_k: dict[int, np.ndarray] = {}
    rows = []
    for k in k_values:
        if k >= len(df):
            continue
        labels = KMeans(n_clusters=k, random_state=random_state, n_init=20, init="random", algorithm="lloyd").fit_predict(x)
        labels_by_k[k] = labels
        rows.append(
            {
                "k": k,
                "silhouette": float(silhouette_score(x, labels, metric="manhattan")),
                "silhouette_metric": "manhattan",
                "cluster_count": int(len(set(labels))),
                "min_cluster_size": int(pd.Series(labels).value_counts().min()),
                "max_cluster_size": int(pd.Series(labels).value_counts().max()),
            }
        )
    return pd.DataFrame(rows), labels_by_k


def choose_best_k(diagnostics: pd.DataFrame) -> int:
    ranked = diagnostics.sort_values(["silhouette", "k"], ascending=[False, True])
    return int(ranked.iloc[0]["k"])


def cluster_strategy_overlap(assignments: pd.DataFrame, cluster_col: str) -> pd.DataFrame:
    rows = []
    for cluster, group in assignments.groupby(cluster_col, sort=True):
        counts = group["strategy"].value_counts()
        dominant = counts.index[0]
        rows.append(
            {
                "cluster": int(cluster),
                "rows": int(len(group)),
                "dominant_strategy": dominant,
                "dominant_strategy_rows": int(counts.iloc[0]),
                "dominant_strategy_share": float(counts.iloc[0] / len(group)),
                "strategy_mix": ", ".join(f"{strategy}:{count}" for strategy, count in counts.items()),
            }
        )
    return pd.DataFrame(rows)


def cluster_feature_summary(df: pd.DataFrame, cluster_col: str, feature_columns: list[str], top_n: int = 8) -> pd.DataFrame:
    overall = df[feature_columns].median(numeric_only=True)
    rows = []
    for cluster, group in df.groupby(cluster_col, sort=True):
        medians = group[feature_columns].median(numeric_only=True)
        deltas = (medians - overall).abs().sort_values(ascending=False).head(top_n)
        rows.append(
            {
                "cluster": int(cluster),
                "rows": int(len(group)),
                "top_shifted_features": ", ".join(f"{feature}={medians[feature]:.3f}" for feature in deltas.index),
            }
        )
    return pd.DataFrame(rows)


def explicit_strategy_metrics(assignments: pd.DataFrame, cluster_col: str) -> dict[str, float]:
    return {
        "adjusted_rand_index": float(adjusted_rand_score(assignments["strategy"], assignments[cluster_col])),
        "normalized_mutual_info": float(normalized_mutual_info_score(assignments["strategy"], assignments[cluster_col])),
    }


def add_cluster_assignments(baskets: pd.DataFrame, labels_by_k: dict[int, np.ndarray], best_k: int) -> pd.DataFrame:
    assignments = baskets[
        [
            "basket_id",
            "strategy",
            "T",
            "S",
            "direction",
            "position_count",
            "pnl_est",
            "first_entry_time",
            "last_exit_time",
            "add_on_count",
            "holding_minutes",
        ]
    ].copy()
    assignments["cluster_best"] = labels_by_k[best_k]
    for k, labels in labels_by_k.items():
        assignments[f"cluster_k{k}"] = labels
    return assignments


def build_cluster_report(
    assignments: pd.DataFrame,
    diagnostics: pd.DataFrame,
    overlap: pd.DataFrame,
    best_k: int,
    feature_columns: list[str],
    feature_summary: pd.DataFrame | None = None,
) -> str:
    active_strategies = sorted(assignments["strategy"].dropna().unique())
    forced12 = "cluster_k12" in assignments.columns
    metrics = explicit_strategy_metrics(assignments, "cluster_best") if "cluster_best" in assignments else {}
    lines = [
        "# Phase 3 Strategy Candidate Discovery Report",
        "",
        "## Executive Summary",
        "",
        f"- Active explicit strategies: `{len(active_strategies)}` — {', '.join(active_strategies)}.",
        f"- Basket rows clustered: `{len(assignments)}`.",
        f"- Feature columns used for clustering: `{len(feature_columns)}`.",
        f"- Natural KMeans candidate selected by silhouette: `k={best_k}`.",
        f"- Forced 12-cluster view generated: `{forced12}`.",
        f"- Best-cluster adjusted Rand index vs explicit `T/S` strategy tags: `{metrics.get('adjusted_rand_index', float('nan')):.4f}`.",
        f"- Best-cluster normalized mutual information vs explicit `T/S` strategy tags: `{metrics.get('normalized_mutual_info', float('nan')):.4f}`.",
        "",
        "## Interpretation",
        "",
        "- Explicit `T/S` tags remain the strongest strategy identifiers; clustering is used as a behavioral cross-check, not as proof of hidden exact EA rules.",
        "- The forced 12-cluster view is diagnostic only. This backtest contains 8 active explicit strategy IDs, so 12 clusters should not be interpreted as evidence that all marketed strategies traded.",
        "- Basket-level clustering mixes entry context and management behavior. Use Phase 4 rule inference to separate initial-entry hypotheses from grid/add-on and close management.",
        "",
        "## KMeans Diagnostics",
        "",
        "- Silhouette scores use Manhattan distance on median-imputed, clipped, standardized features to avoid sklearn Euclidean pairwise-distance warnings on this environment.",
        "",
        "| k | silhouette | min size | max size |",
        "|---:|---:|---:|---:|",
        *diagnostics_table(diagnostics),
        "",
        "## Best-Cluster Strategy Overlap",
        "",
        "| Cluster | Rows | Dominant strategy | Dominant share | Strategy mix |",
        "|---:|---:|---|---:|---|",
        *overlap_table(overlap),
        "",
        "## Feature Columns Used",
        "",
        ", ".join(f"`{column}`" for column in feature_columns),
    ]
    if feature_summary is not None and not feature_summary.empty:
        lines.extend(
            [
                "",
                "## Best-Cluster Shifted Feature Summary",
                "",
                "| Cluster | Rows | Top shifted median features |",
                "|---:|---:|---|",
                *feature_summary_table(feature_summary),
            ]
        )
    return "\n".join(lines) + "\n"


def diagnostics_table(diagnostics: pd.DataFrame) -> list[str]:
    rows = []
    for row in diagnostics.to_dict(orient="records"):
        min_size = row.get("min_cluster_size", "")
        max_size = row.get("max_cluster_size", "")
        rows.append(f"| {int(row['k'])} | {row['silhouette']:.4f} | {min_size} | {max_size} |")
    return rows


def overlap_table(overlap: pd.DataFrame) -> list[str]:
    return [
        f"| {int(row.cluster)} | {int(row.rows)} | {row.dominant_strategy} | {row.dominant_strategy_share:.3f} | {row.strategy_mix if hasattr(row, 'strategy_mix') else ''} |"
        for row in overlap.itertuples()
    ]


def feature_summary_table(feature_summary: pd.DataFrame) -> list[str]:
    return [f"| {int(row.cluster)} | {int(row.rows)} | {row.top_shifted_features} |" for row in feature_summary.itertuples()]
