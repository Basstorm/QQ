from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from qq_research.s10_exit_diagnostics import build_s10_exit_report, build_s10_path_diagnostics, summarize_s10_path_diagnostics

OUTPUTS = PROJECT / "outputs"
LIFECYCLE = OUTPUTS / "basket_minute_lifecycle.parquet"
DIAGNOSTICS_CSV = OUTPUTS / "s10_exit_path_diagnostics.csv"
SUMMARY_CSV = OUTPUTS / "s10_exit_path_summary.csv"
REPORT_MD = OUTPUTS / "s10_exit_path_diagnostics.md"


def main() -> None:
    lifecycle = pd.read_parquet(LIFECYCLE)
    diagnostics = build_s10_path_diagnostics(lifecycle)
    summary = summarize_s10_path_diagnostics(diagnostics)
    diagnostics.to_csv(DIAGNOSTICS_CSV, index=False)
    summary.to_csv(SUMMARY_CSV, index=False)
    REPORT_MD.write_text(build_s10_exit_report(diagnostics, summary), encoding="utf-8")
    print("Wrote outputs/s10_exit_path_diagnostics.csv")
    print("Wrote outputs/s10_exit_path_summary.csv")
    print("Wrote outputs/s10_exit_path_diagnostics.md")


if __name__ == "__main__":
    main()
