from __future__ import annotations

import numpy as np
import pandas as pd


def label_s10_target_modes(diagnostics: pd.DataFrame) -> pd.DataFrame:
    frame = diagnostics.copy()
    frame["exit_time"] = pd.to_datetime(frame["exit_time"])
    exit_hour = frame["exit_time"].dt.hour
    labels = np.select(
        [
            frame["exit_move"].le(0),
            exit_hour.between(21, 23) & frame["holding_min"].le(120),
            exit_hour.between(1, 4),
            frame["exit_move"].ge(3),
        ],
        ["timeout_loss", "quick_low", "overnight_medium", "late_high"],
        default="mixed_other",
    )
    frame["target_mode"] = labels
    return frame


def build_s10_basket_feature_frame(lifecycle: pd.DataFrame, labeled: pd.DataFrame) -> pd.DataFrame:
    rows = []
    s10 = lifecycle[lifecycle["strategy"].eq("T5/S10")].sort_values(["basket_id", "time"])
    label_map = labeled.set_index("basket_id")["target_mode"].to_dict()
    for basket_id, group in s10.groupby("basket_id", sort=True):
        if basket_id not in label_map:
            continue
        entry_time = pd.Timestamp(group["time"].min())
        move = group["close_move_from_open_vwap_points"]
        first_5m = group[group["minutes_since_initial_entry"].le(5)]
        first_30m = group[group["minutes_since_initial_entry"].le(30)]
        rows.append(
            {
                "basket_id": basket_id,
                "target_mode": label_map[basket_id],
                "entry_hour": entry_time.hour,
                "entry_minute": entry_time.minute,
                "mfe_5m": float(first_5m["close_move_from_open_vwap_points"].max()) if len(first_5m) else np.nan,
                "mae_5m": float(first_5m["close_move_from_open_vwap_points"].min()) if len(first_5m) else np.nan,
                "mfe_30m": float(first_30m["close_move_from_open_vwap_points"].max()) if len(first_30m) else np.nan,
                "mae_30m": float(first_30m["close_move_from_open_vwap_points"].min()) if len(first_30m) else np.nan,
                "add_ons_30m": int(first_30m["is_add_on_minute"].sum()) if "is_add_on_minute" in first_30m else 0,
                "max_layers_30m": int(first_30m["open_layer_count"].max()) if len(first_30m) else 0,
                "early_adverse_max": float(first_30m["adverse_from_pre_last_entry_points"].max()) if "adverse_from_pre_last_entry_points" in first_30m else np.nan,
                "path_mfe": float(move.max()),
                "path_mae": float(move.min()),
                "observed_minutes": float(group["minutes_since_initial_entry"].max()),
            }
        )
    return pd.DataFrame(rows)


def score_s10_mode_features(features: pd.DataFrame, candidate_features: list[str]) -> pd.DataFrame:
    rows = []
    overall_modes = features["target_mode"]
    for feature in candidate_features:
        data = features[[feature, "target_mode"]].dropna()
        if data.empty or data[feature].nunique() < 2 or overall_modes.nunique() < 2:
            continue
        overall_mean = data[feature].mean()
        ss_between = sum(len(group) * (group[feature].mean() - overall_mean) ** 2 for _, group in data.groupby("target_mode"))
        ss_total = ((data[feature] - overall_mean) ** 2).sum()
        eta_squared = ss_between / ss_total if ss_total else 0.0
        mode_medians = data.groupby("target_mode")[feature].median().to_dict()
        rows.append(
            {
                "feature": feature,
                "eta_squared": float(eta_squared),
                "non_null": int(len(data)),
                "mode_medians": "; ".join(f"{mode}={value:.3f}" for mode, value in sorted(mode_medians.items())),
            }
        )
    return pd.DataFrame(rows).sort_values(["eta_squared", "non_null"], ascending=[False, False]).reset_index(drop=True)


def score_s10_mode_feature_rules(features: pd.DataFrame, candidate_features: list[str]) -> pd.DataFrame:
    rows = []
    for target_mode in sorted(features["target_mode"].dropna().unique()):
        positives = features["target_mode"].eq(target_mode)
        for feature in candidate_features:
            values = features[feature].dropna()
            if values.nunique() < 2:
                continue
            for quantile in [0.25, 0.50, 0.75]:
                threshold = float(values.quantile(quantile))
                for operator in [">=", "<="]:
                    matched = features[feature].ge(threshold) if operator == ">=" else features[feature].le(threshold)
                    true_positive = int((matched & positives).sum())
                    matched_count = int(matched.sum())
                    total_positive = int(positives.sum())
                    precision = true_positive / matched_count if matched_count else 0.0
                    recall = true_positive / total_positive if total_positive else 0.0
                    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
                    rows.append(
                        {
                            "target_mode": target_mode,
                            "feature": feature,
                            "operator": operator,
                            "threshold": threshold,
                            "matched": matched_count,
                            "precision": precision,
                            "recall": recall,
                            "f1": f1,
                        }
                    )
    return pd.DataFrame(rows).sort_values(["f1", "precision", "recall"], ascending=False).reset_index(drop=True)


def build_s10_hidden_mode_report(features: pd.DataFrame, scores: pd.DataFrame, rules: pd.DataFrame | None = None) -> str:
    mode_counts = features["target_mode"].value_counts().sort_index()
    lines = [
        "# T5/S10 Hidden Target Mode Diagnostics",
        "",
        "## Target Mode Counts",
        "",
        "| Target mode | Baskets |",
        "|---|---:|",
    ]
    for mode, count in mode_counts.items():
        lines.append(f"| `{mode}` | {int(count)} |")
    lines.extend(["", "## Feature Separation Scores", "", "| Feature | Eta squared | Non-null | Mode medians |", "|---|---:|---:|---|"])
    for row in scores.head(20).itertuples(index=False):
        lines.append(f"| `{row.feature}` | {row.eta_squared:.3f} | {int(row.non_null)} | {row.mode_medians} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `path_mfe`, `path_mae`, and `observed_minutes` are post-entry/full-path diagnostics and should not be used as live entry-time selectors.",
            "- The strongest practical early-path separator is `quick_low` via favorable movement in the first 5-30 minutes.",
            "- Other S10 target modes remain weakly separated by entry/early-path single features.",
        ]
    )
    if rules is not None and not rules.empty:
        lines.extend(["", "## Best One-Feature Early Rules", "", "| Target mode | Rule | Matched | Precision | Recall | F1 |", "|---|---|---:|---:|---:|---:|"])
        for row in rules.head(20).itertuples(index=False):
            lines.append(
                f"| `{row.target_mode}` | `{row.feature} {row.operator} {row.threshold:.3f}` | {int(row.matched)} | {row.precision:.3f} | {row.recall:.3f} | {row.f1:.3f} |"
            )
    return "\n".join(lines) + "\n"
