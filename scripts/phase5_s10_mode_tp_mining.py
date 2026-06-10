from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from qq_research.s10_mode_tp_mining import (
    add_s10_exit_modes,
    build_s10_mode_tp_report,
    compute_final_mode_oracle_events,
    compute_mode_first_cross_events,
    mine_s10_mode_tp_thresholds,
)

OUTPUTS = PROJECT / "outputs"
LIFECYCLE = OUTPUTS / "basket_minute_lifecycle.parquet"
THRESHOLDS_CSV = OUTPUTS / "s10_mode_tp_thresholds.csv"
EVENTS_CSV = OUTPUTS / "s10_mode_tp_first_cross_events.csv"
SUMMARY_CSV = OUTPUTS / "s10_mode_tp_first_cross_summary.csv"
REPORT_MD = OUTPUTS / "s10_mode_tp_report.md"


def summarize_variant(events: pd.DataFrame, variant: str) -> dict[str, float | int | str]:
    found = events[events["cross_found"]]
    return {
        "variant": variant,
        "basket_count": int(len(events)),
        "cross_found_count": int(len(found)),
        "cross_found_pct": len(found) / len(events) * 100 if len(events) else 0.0,
        "within_1m_pct": found["lag_minutes"].le(1).mean() * 100 if len(found) else 0.0,
        "within_5m_pct": found["lag_minutes"].le(5).mean() * 100 if len(found) else 0.0,
        "lag_median": float(found["lag_minutes"].median()) if len(found) else float("nan"),
        "lag_q75": float(found["lag_minutes"].quantile(0.75)) if len(found) else float("nan"),
        "lag_q90": float(found["lag_minutes"].quantile(0.90)) if len(found) else float("nan"),
    }


def main() -> None:
    lifecycle = pd.read_parquet(LIFECYCLE)
    s10 = add_s10_exit_modes(lifecycle[lifecycle["strategy"].eq("T5/S10")])
    thresholds = mine_s10_mode_tp_thresholds(s10, min_positives=2)
    thresholds.to_csv(THRESHOLDS_CSV, index=False)
    event_frames = []
    summary_rows = []
    report_parts = [
        "# T5/S10 Mode-Conditioned TP Report",
        "",
        "Modes are based on current M1 broker session and minutes since initial basket entry.",
        "",
        "## Variant Summary",
        "",
        "| Variant | Baskets | Cross found % | Within 1m % | Within 5m % | Lag median | Lag q75 | Lag q90 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    variant_reports = []
    for threshold_col in ["tp_q25", "tp_median", "tp_q75", "tp_q90"]:
        events = compute_mode_first_cross_events(s10, thresholds, threshold_col=threshold_col)
        events["variant"] = threshold_col
        event_frames.append(events)
        summary = summarize_variant(events, threshold_col)
        summary_rows.append(summary)
        report_parts.append(
            f"| `{threshold_col}` | {summary['basket_count']} | {summary['cross_found_pct']:.1f} | {summary['within_1m_pct']:.1f} | {summary['within_5m_pct']:.1f} | {summary['lag_median']:.1f} | {summary['lag_q75']:.1f} | {summary['lag_q90']:.1f} |"
        )
        variant_reports.append(build_s10_mode_tp_report(thresholds, events, threshold_col))
        oracle_events = compute_final_mode_oracle_events(s10, thresholds, threshold_col=threshold_col)
        oracle_events["variant"] = f"oracle_final_mode_{threshold_col}"
        event_frames.append(oracle_events)
        oracle_summary = summarize_variant(oracle_events, f"oracle_final_mode_{threshold_col}")
        summary_rows.append(oracle_summary)
        report_parts.append(
            f"| `oracle_final_mode_{threshold_col}` | {oracle_summary['basket_count']} | {oracle_summary['cross_found_pct']:.1f} | {oracle_summary['within_1m_pct']:.1f} | {oracle_summary['within_5m_pct']:.1f} | {oracle_summary['lag_median']:.1f} | {oracle_summary['lag_q75']:.1f} | {oracle_summary['lag_q90']:.1f} |"
        )
    all_events = pd.concat(event_frames, ignore_index=True)
    summary_frame = pd.DataFrame(summary_rows)
    all_events.to_csv(EVENTS_CSV, index=False)
    summary_frame.to_csv(SUMMARY_CSV, index=False)
    report_parts.extend(["", "## Detailed Variant Reports", "", *variant_reports])
    REPORT_MD.write_text("\n".join(report_parts), encoding="utf-8")
    print("Wrote outputs/s10_mode_tp_thresholds.csv")
    print("Wrote outputs/s10_mode_tp_first_cross_events.csv")
    print("Wrote outputs/s10_mode_tp_first_cross_summary.csv")
    print("Wrote outputs/s10_mode_tp_report.md")


if __name__ == "__main__":
    main()
