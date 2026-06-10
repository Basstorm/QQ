from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from qq_research.exit_first_cross import build_first_cross_report, compute_first_cross_events, summarize_first_cross_lags

OUTPUTS = PROJECT / "outputs"
LIFECYCLE = OUTPUTS / "basket_minute_lifecycle.parquet"
THRESHOLDS = OUTPUTS / "exit_trigger_thresholds.csv"


def run_variant(lifecycle: pd.DataFrame, thresholds: pd.DataFrame, variant: str, move_col: str, threshold_col: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    events = compute_first_cross_events(lifecycle, thresholds, threshold_col=threshold_col, move_col=move_col)
    summary = summarize_first_cross_lags(events)
    events["variant"] = variant
    summary["variant"] = variant
    return events, summary


def main() -> None:
    lifecycle = pd.read_parquet(LIFECYCLE)
    thresholds = pd.read_csv(THRESHOLDS)
    variants = [
        ("close_q25", "close_move_from_open_vwap_points", "move_q25"),
        ("close_median", "close_move_from_open_vwap_points", "move_median"),
        ("touch_q25", "touch_move_from_open_vwap_points", "move_q25"),
        ("touch_median", "touch_move_from_open_vwap_points", "move_median"),
    ]
    event_frames = []
    summary_frames = []
    report_parts = [
        "# Exit First-Cross / First-Touch Analysis",
        "",
        "## Scope",
        "",
        "- Compares first M1 TP eligibility to the actual QQ basket exit minute.",
        "- `close_*` variants use M1 close relative to active basket VWAP.",
        "- `touch_*` variants use intrabar favorable high/low relative to active basket VWAP.",
        "- Thresholds come from `exit_trigger_thresholds.csv` per strategy and open layer count.",
        "",
    ]
    for variant, move_col, threshold_col in variants:
        events, summary = run_variant(lifecycle, thresholds, variant, move_col, threshold_col)
        event_frames.append(events)
        summary_frames.append(summary)
        report_parts.append(build_first_cross_report(summary, variant))
    all_events = pd.concat(event_frames, ignore_index=True)
    all_summary = pd.concat(summary_frames, ignore_index=True)
    all_events.to_csv(OUTPUTS / "exit_first_cross_events.csv", index=False)
    all_summary.to_csv(OUTPUTS / "exit_first_cross_summary.csv", index=False)
    (OUTPUTS / "exit_first_cross_report.md").write_text("\n".join(report_parts), encoding="utf-8")
    print("Wrote outputs/exit_first_cross_events.csv")
    print("Wrote outputs/exit_first_cross_summary.csv")
    print("Wrote outputs/exit_first_cross_report.md")


if __name__ == "__main__":
    main()
