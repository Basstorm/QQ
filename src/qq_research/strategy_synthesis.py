from __future__ import annotations

import pandas as pd


def select_best_temporal_rule(validation: pd.DataFrame, strategy: str, mode: str) -> dict[str, object] | None:
    rows = validation[validation["strategy"].eq(strategy) & validation["mode"].eq(mode)]
    if rows.empty:
        return None
    ranked = rows.sort_values(["test_precision_lift_vs_base", "test_recall", "test_matched"], ascending=[False, False, False])
    return ranked.iloc[0].to_dict()


def classify_rule_confidence(rule: dict[str, object] | None) -> str:
    if not rule:
        return "weak"
    lift = float(rule.get("test_precision_lift_vs_base", 0.0))
    recall = float(rule.get("test_recall", 0.0))
    matched = int(rule.get("test_matched", 0))
    if matched < 10 or recall < 0.08:
        return "sparse_hint"
    if lift >= 15 and recall >= 0.25 and matched >= 100:
        return "robust"
    if lift >= 8 and recall >= 0.20 and matched >= 50:
        return "moderate"
    return "tentative"


def synthesize_strategy_rows(profiles: pd.DataFrame, validation: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for profile in profiles.to_dict(orient="records"):
        strategy = profile["strategy"]
        all_rule = select_best_temporal_rule(validation, strategy, "all_background")
        matched_rule = select_best_temporal_rule(validation, strategy, "matched_hour_weekday")
        all_conf = classify_rule_confidence(all_rule)
        matched_conf = classify_rule_confidence(matched_rule)
        rows.append(
            {
                "strategy": strategy,
                "candidate_family": profile.get("candidate_family", "n/a"),
                "compact_confidence": profile.get("confidence", "n/a"),
                "overall_confidence": combine_confidence(all_conf, matched_conf),
                "all_background_confidence": all_conf,
                "matched_confidence": matched_conf,
                "best_all_background_rule": format_selected_rule(all_rule),
                "best_matched_rule": format_selected_rule(matched_rule),
                "all_background_test_lift": float(all_rule.get("test_precision_lift_vs_base", 0.0)) if all_rule else 0.0,
                "all_background_test_recall": float(all_rule.get("test_recall", 0.0)) if all_rule else 0.0,
                "matched_test_lift": float(matched_rule.get("test_precision_lift_vs_base", 0.0)) if matched_rule else 0.0,
                "matched_test_recall": float(matched_rule.get("test_recall", 0.0)) if matched_rule else 0.0,
                "matched_test_precision": float(matched_rule.get("test_precision", 0.0)) if matched_rule else 0.0,
                "matched_test_count": int(matched_rule.get("test_matched", 0)) if matched_rule else 0,
            }
        )
    return pd.DataFrame(rows)


def combine_confidence(all_confidence: str, matched_confidence: str) -> str:
    order = {"weak": 0, "sparse_hint": 1, "tentative": 2, "moderate": 3, "robust": 4}
    best = max([all_confidence, matched_confidence], key=lambda value: order.get(value, 0))
    return best


def format_selected_rule(rule: dict[str, object] | None) -> str:
    if not rule:
        return "n/a"
    return str(rule.get("rule", "n/a"))


def build_synthesis_report(rows: pd.DataFrame) -> str:
    lines = [
        "# Final Approximate Strategy Rule Synthesis",
        "",
        "## Scope",
        "",
        "- This is not source-code recovery. It is a ranked synthesis of observed backtest behavior, expanded indicator discovery, candidate rules, and temporal validation.",
        "- Temporal validation has the highest weight; full-sample rules without temporal support should be treated as weak hypotheses.",
        "- `sparse_hint` means a rule has high lift but too few test matches or too little recall to trust as a robust rule.",
        "",
        "## Summary Table",
        "",
        "| Strategy | Candidate family | Overall confidence | All-background rule | Matched-context rule |",
        "|---|---|---|---|---|",
    ]
    for row in rows.sort_values("strategy").itertuples(index=False):
        lines.append(
            f"| `{row.strategy}` | {row.candidate_family} | **{row.overall_confidence}** | `{row.best_all_background_rule}` | `{row.best_matched_rule}` |"
        )
    lines.extend(["", "## Per-Strategy Detail", ""])
    for row in rows.sort_values("strategy").itertuples(index=False):
        all_confidence = getattr(row, "all_background_confidence", "n/a")
        matched_confidence = getattr(row, "matched_confidence", "n/a")
        all_lift = getattr(row, "all_background_test_lift", 0.0)
        all_recall = getattr(row, "all_background_test_recall", 0.0)
        matched_lift = getattr(row, "matched_test_lift", 0.0)
        matched_recall = getattr(row, "matched_test_recall", 0.0)
        matched_precision = getattr(row, "matched_test_precision", 0.0)
        matched_count = getattr(row, "matched_test_count", 0)
        lines.extend(
            [
                f"### {row.strategy}",
                "",
                f"- Candidate family: {row.candidate_family}.",
                f"- Overall confidence: **{row.overall_confidence}**.",
                f"- All-background: {all_confidence}; test lift `{all_lift:.1f}x`, test recall `{all_recall:.3f}`.",
                f"- Matched-context: {matched_confidence}; test lift `{matched_lift:.1f}x`, test recall `{matched_recall:.3f}`, test precision `{matched_precision:.4f}`, matched rows `{matched_count}`.",
                f"- Best all-background rule: `{row.best_all_background_rule}`.",
                f"- Best matched-context rule: `{row.best_matched_rule}`.",
                "",
            ]
        )
    return "\n".join(lines) + "\n"
