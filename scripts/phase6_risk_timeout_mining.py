from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from qq_research.risk_timeout_mining import build_risk_timeout_report, build_strategy_risk_frame, mine_timeout_candidates

OUTPUTS = PROJECT / "outputs"
LIFECYCLE = OUTPUTS / "basket_minute_lifecycle.parquet"
RISK_FRAME_CSV = OUTPUTS / "risk_timeout_basket_frame.csv"
CANDIDATES_CSV = OUTPUTS / "risk_timeout_candidates.csv"
REPORT_MD = OUTPUTS / "risk_timeout_mining.md"
TARGET_STRATEGIES = {"T3/S06", "T6/S12"}


def main() -> None:
    lifecycle = pd.read_parquet(LIFECYCLE)
    risk = build_strategy_risk_frame(lifecycle)
    risk = risk[risk["strategy"].isin(TARGET_STRATEGIES)]
    candidates = mine_timeout_candidates(risk)
    risk.to_csv(RISK_FRAME_CSV, index=False)
    candidates.to_csv(CANDIDATES_CSV, index=False)
    REPORT_MD.write_text(build_risk_timeout_report(candidates), encoding="utf-8")
    print("Wrote outputs/risk_timeout_basket_frame.csv")
    print("Wrote outputs/risk_timeout_candidates.csv")
    print("Wrote outputs/risk_timeout_mining.md")


if __name__ == "__main__":
    main()
