from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from qq_research.add_on_trigger_mining import build_add_on_threshold_report, build_add_on_trigger_frame, mine_add_on_thresholds

OUTPUTS = PROJECT / "outputs"
LIFECYCLE = OUTPUTS / "basket_minute_lifecycle.parquet"
THRESHOLDS_CSV = OUTPUTS / "add_on_trigger_thresholds.csv"
REPORT_MD = OUTPUTS / "add_on_trigger_thresholds.md"


def main() -> None:
    lifecycle = pd.read_parquet(LIFECYCLE)
    trigger_frame = build_add_on_trigger_frame(lifecycle)
    thresholds = mine_add_on_thresholds(trigger_frame, min_positives=8)
    thresholds.to_csv(THRESHOLDS_CSV, index=False)
    REPORT_MD.write_text(build_add_on_threshold_report(thresholds), encoding="utf-8")
    print("Wrote outputs/add_on_trigger_thresholds.csv")
    print("Wrote outputs/add_on_trigger_thresholds.md")


if __name__ == "__main__":
    main()
