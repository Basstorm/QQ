from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from qq_research.rule_inference import strategy_profile
from qq_research.strategy_synthesis import build_synthesis_report, synthesize_strategy_rows

OUTPUTS = PROJECT / "outputs"
DEAL_FEATURES = OUTPUTS / "deal_features.parquet"
BASKET_FEATURES = OUTPUTS / "basket_features.parquet"
TEMPORAL_VALIDATION = OUTPUTS / "temporal_rule_validation.csv"
SYNTHESIS_CSV = OUTPUTS / "strategy_rule_synthesis.csv"
SYNTHESIS_MD = OUTPUTS / "strategy_rule_synthesis.md"


def build_profile_frame(deal_features: pd.DataFrame, basket_features: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for strategy in sorted(basket_features["strategy"].dropna().unique()):
        profile = strategy_profile(strategy, deal_features, basket_features)
        rows.append(
            {
                "strategy": strategy,
                "candidate_family": profile["candidate_family"],
                "confidence": profile["confidence"],
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    deal_features = pd.read_parquet(DEAL_FEATURES)
    basket_features = pd.read_parquet(BASKET_FEATURES)
    validation = pd.read_csv(TEMPORAL_VALIDATION)
    profiles = build_profile_frame(deal_features, basket_features)
    synthesis = synthesize_strategy_rows(profiles, validation)
    synthesis.to_csv(SYNTHESIS_CSV, index=False)
    SYNTHESIS_MD.write_text(build_synthesis_report(synthesis), encoding="utf-8")
    print("Wrote outputs/strategy_rule_synthesis.csv")
    print("Wrote outputs/strategy_rule_synthesis.md")


if __name__ == "__main__":
    main()
