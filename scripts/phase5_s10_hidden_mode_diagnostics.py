from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from qq_research.s10_hidden_mode_diagnostics import (
    build_s10_basket_feature_frame,
    build_s10_hidden_mode_report,
    label_s10_target_modes,
    score_s10_mode_feature_rules,
    score_s10_mode_features,
)

OUTPUTS = PROJECT / "outputs"
LIFECYCLE = OUTPUTS / "basket_minute_lifecycle.parquet"
S10_DIAGNOSTICS = OUTPUTS / "s10_exit_path_diagnostics.csv"
FEATURES_CSV = OUTPUTS / "s10_hidden_mode_features.csv"
SCORES_CSV = OUTPUTS / "s10_hidden_mode_feature_scores.csv"
RULES_CSV = OUTPUTS / "s10_hidden_mode_feature_rules.csv"
REPORT_MD = OUTPUTS / "s10_hidden_mode_diagnostics.md"


def main() -> None:
    lifecycle = pd.read_parquet(LIFECYCLE)
    diagnostics = pd.read_csv(S10_DIAGNOSTICS, parse_dates=["entry_time", "exit_time", "time_of_max"])
    labeled = label_s10_target_modes(diagnostics)
    features = build_s10_basket_feature_frame(lifecycle, labeled)
    candidate_features = [
        "entry_hour",
        "entry_minute",
        "mfe_5m",
        "mae_5m",
        "mfe_30m",
        "mae_30m",
        "add_ons_30m",
        "max_layers_30m",
        "early_adverse_max",
        "observed_minutes",
        "path_mfe",
        "path_mae",
    ]
    scores = score_s10_mode_features(features, candidate_features)
    early_rule_features = ["entry_hour", "entry_minute", "mfe_5m", "mae_5m", "mfe_30m", "mae_30m", "early_adverse_max"]
    rules = score_s10_mode_feature_rules(features, early_rule_features)
    features.to_csv(FEATURES_CSV, index=False)
    scores.to_csv(SCORES_CSV, index=False)
    rules.to_csv(RULES_CSV, index=False)
    REPORT_MD.write_text(build_s10_hidden_mode_report(features, scores, rules), encoding="utf-8")
    print("Wrote outputs/s10_hidden_mode_features.csv")
    print("Wrote outputs/s10_hidden_mode_feature_scores.csv")
    print("Wrote outputs/s10_hidden_mode_feature_rules.csv")
    print("Wrote outputs/s10_hidden_mode_diagnostics.md")


if __name__ == "__main__":
    main()
