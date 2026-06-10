from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from qq_research.add_on_trigger_mining import build_add_on_cooldown_report, build_add_on_trigger_frame, mine_add_on_cooldown_rules

OUTPUTS = PROJECT / "outputs"
LIFECYCLE = OUTPUTS / "basket_minute_lifecycle.parquet"
RULES_CSV = OUTPUTS / "add_on_cooldown_rules.csv"
REPORT_MD = OUTPUTS / "add_on_cooldown_rules.md"


def main() -> None:
    lifecycle = pd.read_parquet(LIFECYCLE)
    trigger_frame = build_add_on_trigger_frame(lifecycle)
    rules = mine_add_on_cooldown_rules(trigger_frame, min_positives=8)
    rules.to_csv(RULES_CSV, index=False)
    REPORT_MD.write_text(build_add_on_cooldown_report(rules), encoding="utf-8")
    print("Wrote outputs/add_on_cooldown_rules.csv")
    print("Wrote outputs/add_on_cooldown_rules.md")


if __name__ == "__main__":
    main()
