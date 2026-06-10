from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from qq_research.rule_inference import build_strategy_profiles_report

OUTPUTS = PROJECT / "outputs"
DEAL_FEATURES = OUTPUTS / "deal_features.parquet"
BASKET_FEATURES = OUTPUTS / "basket_features.parquet"
STRATEGY_PROFILES = OUTPUTS / "strategy_profiles.md"


def main() -> None:
    deal_features = pd.read_parquet(DEAL_FEATURES)
    basket_features = pd.read_parquet(BASKET_FEATURES)
    report = build_strategy_profiles_report(deal_features, basket_features)
    STRATEGY_PROFILES.write_text(report, encoding="utf-8")
    print("Wrote outputs/strategy_profiles.md")


if __name__ == "__main__":
    main()
