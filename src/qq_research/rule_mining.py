from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd


def build_single_feature_conditions(scores: pd.DataFrame, strategy: str, top_n: int = 10) -> list[dict[str, object]]:
    rows = scores[scores["strategy"].eq(strategy)].sort_values(["auc_lift", "feature"], ascending=[False, True]).head(top_n)
    conditions = []
    for row in rows.itertuples(index=False):
        conditions.append(
            {
                "feature": row.feature,
                "operator": ">=" if row.direction == "high" else "<=",
                "threshold": float(row.positive_median),
                "auc_lift": float(row.auc_lift),
            }
        )
    return conditions


def evaluate_and_rule(feature_frame: pd.DataFrame, labels: pd.Series, rule: list[dict[str, object]]) -> dict[str, float | int]:
    mask = pd.Series(True, index=feature_frame.index)
    for condition in rule:
        values = pd.to_numeric(feature_frame[condition["feature"]], errors="coerce").replace([np.inf, -np.inf], np.nan)
        if condition["operator"] == ">=":
            mask &= values >= float(condition["threshold"])
        else:
            mask &= values <= float(condition["threshold"])
    y = labels.astype(bool)
    valid = mask.notna() & y.notna()
    matched = mask[valid]
    true_positive = int((matched & y[valid]).sum())
    false_positive = int((matched & ~y[valid]).sum())
    total_positive = int(y[valid].sum())
    base_rate = total_positive / int(valid.sum()) if int(valid.sum()) else 0.0
    matched_count = int(matched.sum())
    precision = true_positive / matched_count if matched_count else 0.0
    return {
        "matched": matched_count,
        "true_positive": true_positive,
        "false_positive": false_positive,
        "precision": precision,
        "recall": true_positive / total_positive if total_positive else 0.0,
        "total_positive": total_positive,
        "base_rate": base_rate,
        "precision_lift_vs_base": precision / base_rate if base_rate else 0.0,
    }


def mine_candidate_rules(
    feature_frame: pd.DataFrame,
    labels: pd.DataFrame,
    scores: pd.DataFrame,
    top_features: int = 8,
    max_rule_size: int = 3,
    min_precision: float = 0.05,
    min_recall: float = 0.05,
    top_n: int = 20,
) -> pd.DataFrame:
    rows = []
    for strategy in [column for column in labels.columns if column != "time"]:
        conditions = build_single_feature_conditions(scores, strategy, top_n=top_features)
        for size in range(1, max_rule_size + 1):
            for combo in combinations(conditions, size):
                metrics = evaluate_and_rule(feature_frame, labels[strategy], list(combo))
                if metrics["precision"] < min_precision or metrics["recall"] < min_recall:
                    continue
                rows.append(
                    {
                        "strategy": strategy,
                        "rule_size": size,
                        "rule": format_rule(combo),
                        **metrics,
                    }
                )
    if not rows:
        return pd.DataFrame()
    return (
        pd.DataFrame(rows)
        .assign(score=lambda df: df["precision"] * df["recall"])
        .sort_values(["strategy", "score", "precision", "recall", "rule_size"], ascending=[True, False, False, False, True])
        .groupby("strategy", as_index=False)
        .head(top_n)
        .reset_index(drop=True)
    )


def format_rule(rule: list[dict[str, object]] | tuple[dict[str, object], ...]) -> str:
    return " AND ".join(f"{condition['feature']} {condition['operator']} {float(condition['threshold']):.4f}" for condition in rule)


def build_candidate_rules_report(rules: pd.DataFrame) -> str:
    lines = [
        "# Candidate Multi-Condition Strategy Rules",
        "",
        "## Scope",
        "",
        "- These rules are hypotheses mined from expanded indicator features, not confirmed EA source rules.",
        "- Thresholds use positive-bar medians from the single-feature discovery pass, then evaluate AND-combinations against M15 background bars.",
        "- Prefer rules with both useful precision and recall; high precision with tiny recall may only describe a narrow subset.",
        "",
    ]
    if rules.empty:
        return "\n".join(lines + ["No candidate rules met the configured thresholds.", ""]) + "\n"
    for strategy in sorted(rules["strategy"].unique()):
        strategy_rules = rules[rules["strategy"].eq(strategy)].head(10)
        lines.extend(
            [
                f"## {strategy}",
                "",
                "| Rule | Size | Precision | Lift vs base | Recall | Matched | TP | FP |",
                "|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in strategy_rules.itertuples(index=False):
            rule_size = getattr(row, "rule_size", str(row.rule).count(" AND ") + 1)
            lift = getattr(row, "precision_lift_vs_base", 0.0)
            lines.append(
                f"| `{row.rule}` | {int(rule_size)} | {row.precision:.4f} | {lift:.1f}x | {row.recall:.4f} | {int(row.matched)} | {int(row.true_positive)} | {int(row.false_positive)} |"
            )
        lines.append("")
    return "\n".join(lines) + "\n"
