from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from qq_research.expanded_indicator_discovery import build_entry_label_frame, score_features_for_strategy
from qq_research.temporal_validation import matched_context_mask, temporal_split_masks, validate_train_rules_on_test

OUTPUTS = PROJECT / "outputs"
BASKET_FEATURES = OUTPUTS / "basket_features.parquet"
FEATURE_MATRIX = OUTPUTS / "expanded_indicator_feature_matrix.parquet"
VALIDATION_CSV = OUTPUTS / "temporal_rule_validation.csv"
FEATURE_SCORES_CSV = OUTPUTS / "temporal_train_feature_scores.csv"
REPORT_MD = OUTPUTS / "temporal_rule_validation.md"
SPLIT_TIME = "2021-01-01"


def build_train_scores(feature_frame: pd.DataFrame, labels: pd.DataFrame, split_time: str, mode: str) -> pd.DataFrame:
    train_mask, _ = temporal_split_masks(feature_frame, split_time)
    rows = []
    for strategy in [column for column in labels.columns if column != "time"]:
        context = train_mask.copy()
        if mode == "matched_hour_weekday":
            context &= matched_context_mask(feature_frame.loc[train_mask, "time"], labels.loc[train_mask, strategy]).reindex(feature_frame.index, fill_value=False)
        scores = score_features_for_strategy(
            feature_frame.loc[context].reset_index(drop=True),
            labels.loc[context, strategy].reset_index(drop=True),
            strategy,
            top_n=40,
            min_valid=50,
        )
        if not scores.empty:
            scores.insert(0, "mode", mode)
            rows.append(scores)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def build_validation_report(validation: pd.DataFrame, labels: pd.DataFrame, split_time: str) -> str:
    lines = [
        "# Temporal and Matched-Negative Rule Validation",
        "",
        "## Scope",
        "",
        f"- Split time: `{split_time}`. Rules are mined only on rows before the split and evaluated on rows at/after the split.",
        "- Two modes are reported: all M15 background bars, and negatives matched to the strategy's positive entry bars by broker weekday + hour.",
        "- This validates whether candidate indicator rules survive time separation; it still does not prove EA source rules.",
        "",
        "## Positive sample counts",
        "",
        "| Strategy | Train positives | Test positives |",
        "|---|---:|---:|",
    ]
    split = pd.Timestamp(split_time)
    for strategy in [column for column in labels.columns if column != "time"]:
        train_pos = int(labels.loc[labels["time"] < split, strategy].sum())
        test_pos = int(labels.loc[labels["time"] >= split, strategy].sum())
        lines.append(f"| `{strategy}` | {train_pos} | {test_pos} |")
    lines.extend(["", "## Top validated rules", ""])
    if validation.empty:
        lines.append("No rules met configured thresholds.")
        return "\n".join(lines) + "\n"
    for (mode, strategy), group in validation.groupby(["mode", "strategy"], sort=True):
        top = group.sort_values(["test_precision_lift_vs_base", "test_recall", "test_precision"], ascending=[False, False, False]).head(5)
        lines.extend(
            [
                f"### {strategy} — {mode}",
                "",
                "| Rule | Train lift | Test lift | Train recall | Test recall | Test precision | Test matched |",
                "|---|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in top.itertuples(index=False):
            lines.append(
                f"| `{row.rule}` | {row.train_precision_lift_vs_base:.1f}x | {row.test_precision_lift_vs_base:.1f}x | {row.train_recall:.3f} | {row.test_recall:.3f} | {row.test_precision:.4f} | {int(row.test_matched)} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Interpretation guide",
            "",
            "- Rules with both train and test lift above baseline are more credible than full-sample rules.",
            "- Rules with high train lift but weak test lift are likely overfit or regime-specific.",
            "- Matched mode is stricter because it compares entries against non-entry bars from similar weekday/hour contexts.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    feature_frame = pd.read_parquet(FEATURE_MATRIX)
    basket_features = pd.read_parquet(BASKET_FEATURES)
    labels = build_entry_label_frame(feature_frame["time"], basket_features)
    all_validations = []
    all_scores = []
    for mode in ["all_background", "matched_hour_weekday"]:
        scores = build_train_scores(feature_frame, labels, SPLIT_TIME, mode)
        if scores.empty:
            continue
        all_scores.append(scores)
        validation = validate_train_rules_on_test(
            feature_frame,
            labels,
            scores,
            SPLIT_TIME,
            mode=mode,
            top_features=8,
            max_rule_size=3,
            min_precision=0.005,
            min_recall=0.05,
            top_n=20,
        )
        all_validations.append(validation)
    validation = pd.concat(all_validations, ignore_index=True) if all_validations else pd.DataFrame()
    scores = pd.concat(all_scores, ignore_index=True) if all_scores else pd.DataFrame()
    validation.to_csv(VALIDATION_CSV, index=False)
    scores.to_csv(FEATURE_SCORES_CSV, index=False)
    REPORT_MD.write_text(build_validation_report(validation, labels, SPLIT_TIME), encoding="utf-8")
    print("Wrote outputs/temporal_rule_validation.csv")
    print("Wrote outputs/temporal_train_feature_scores.csv")
    print("Wrote outputs/temporal_rule_validation.md")


if __name__ == "__main__":
    main()
