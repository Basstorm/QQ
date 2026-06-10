from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from qq_research.expanded_indicator_discovery import build_entry_label_frame
from qq_research.rule_mining import build_candidate_rules_report, mine_candidate_rules

OUTPUTS = PROJECT / "outputs"
BASKET_FEATURES = OUTPUTS / "basket_features.parquet"
FEATURE_MATRIX = OUTPUTS / "expanded_indicator_feature_matrix.parquet"
SCORES_CSV = OUTPUTS / "expanded_indicator_scores.csv"
RULES_CSV = OUTPUTS / "candidate_rule_combinations.csv"
REPORT_MD = OUTPUTS / "candidate_rule_combinations.md"


def main() -> None:
    feature_frame = pd.read_parquet(FEATURE_MATRIX)
    scores = pd.read_csv(SCORES_CSV)
    basket_features = pd.read_parquet(BASKET_FEATURES)
    labels = build_entry_label_frame(feature_frame["time"], basket_features)
    rules = mine_candidate_rules(
        feature_frame,
        labels,
        scores,
        top_features=8,
        max_rule_size=3,
        min_precision=0.01,
        min_recall=0.05,
        top_n=20,
    )
    rules.to_csv(RULES_CSV, index=False)
    REPORT_MD.write_text(build_candidate_rules_report(rules), encoding="utf-8")
    print("Wrote outputs/candidate_rule_combinations.csv")
    print("Wrote outputs/candidate_rule_combinations.md")


if __name__ == "__main__":
    main()
