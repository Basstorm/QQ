from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from qq_research.lifecycle_management import build_add_on_events, build_exit_events, build_minute_lifecycle

OUTPUTS = PROJECT / "outputs"
POSITIONS = OUTPUTS / "positions.parquet"
M1_CSV = PROJECT / "xauusd_m1_2016_2026.csv"
ADD_ON_EVENTS = OUTPUTS / "lifecycle_add_on_events.parquet"
EXIT_EVENTS = OUTPUTS / "lifecycle_exit_events.parquet"
MINUTE_LIFECYCLE = OUTPUTS / "basket_minute_lifecycle.parquet"
REPORT_MD = OUTPUTS / "lifecycle_management_report.md"


def quantile_table(frame: pd.DataFrame, group_col: str, value_col: str) -> pd.DataFrame:
    table = frame.groupby(group_col)[value_col].quantile([0.1, 0.25, 0.5, 0.75, 0.9]).unstack()
    table.columns = [f"q{int(column * 100)}" for column in table.columns]
    return table.reset_index()


def build_report(add_ons: pd.DataFrame, exits: pd.DataFrame, lifecycle: pd.DataFrame) -> str:
    delayed_add_ons = add_ons[~add_ons["same_minute_as_prev_entry"]] if not add_ons.empty else add_ons
    lines = [
        "# Phase 5 Basket Lifecycle Management Diagnostics",
        "",
        "## Scope",
        "",
        "- This phase studies Quantum Queen's observed basket management, not the initial-entry filter.",
        "- Add-on events measure spacing from previous and initial entries in direction-aware adverse points.",
        "- Exit events measure final basket close price relative to volume-weighted entry price.",
        "- The M1 lifecycle panel has one row per active basket-minute and is intended for later per-minute add-on/exit classifier mining.",
        "- `pre_open_*` lifecycle fields describe the basket state before any add-on opened in that minute, which is the correct state for add-on trigger inference.",
        "",
        "## Dataset Sizes",
        "",
        f"- Add-on events: `{len(add_ons):,}`",
        f"- Delayed/grid add-on events: `{len(delayed_add_ons):,}`",
        f"- Exit events / baskets: `{len(exits):,}`",
        f"- Active basket-minute rows: `{len(lifecycle):,}`",
        "",
        "## Strategy-Level Counts",
        "",
        "| Strategy | Baskets | Same-minute add-ons | Delayed add-ons | Active M1 rows | Basket win rate % | Median basket PnL |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    counts = exits.groupby("strategy").agg(baskets=("basket_id", "count"), win_rate=("pnl_est", lambda s: (s > 0).mean() * 100), median_pnl=("pnl_est", "median"))
    same_minute_counts = add_ons[add_ons["same_minute_as_prev_entry"]].groupby("strategy").size() if not add_ons.empty else pd.Series(dtype=int)
    delayed_counts = delayed_add_ons.groupby("strategy").size() if not delayed_add_ons.empty else pd.Series(dtype=int)
    minute_counts = lifecycle.groupby("strategy").size()
    for strategy, row in counts.sort_index().iterrows():
        lines.append(
            f"| `{strategy}` | {int(row.baskets)} | {int(same_minute_counts.get(strategy, 0))} | {int(delayed_counts.get(strategy, 0))} | {int(minute_counts.get(strategy, 0))} | {row.win_rate:.2f} | {row.median_pnl:.2f} |"
        )
    lines.extend(["", "## Delayed/Grid Add-on Adverse Spacing From Previous Entry", "", "| Strategy | q10 | q25 | median | q75 | q90 |", "|---|---:|---:|---:|---:|---:|"])
    spacing = quantile_table(delayed_add_ons, "strategy", "adverse_from_prev_entry_points") if not delayed_add_ons.empty else pd.DataFrame()
    for row in spacing.sort_values("strategy").itertuples(index=False):
        lines.append(f"| `{row.strategy}` | {row.q10:.2f} | {row.q25:.2f} | {row.q50:.2f} | {row.q75:.2f} | {row.q90:.2f} |")
    lines.extend(["", "## Delayed/Grid Add-on Minutes Since Previous Entry", "", "| Strategy | q10 | q25 | median | q75 | q90 |", "|---|---:|---:|---:|---:|---:|"])
    spacing_minutes = quantile_table(delayed_add_ons, "strategy", "minutes_since_prev_entry") if not delayed_add_ons.empty else pd.DataFrame()
    for row in spacing_minutes.sort_values("strategy").itertuples(index=False):
        lines.append(f"| `{row.strategy}` | {row.q10:.1f} | {row.q25:.1f} | {row.q50:.1f} | {row.q75:.1f} | {row.q90:.1f} |")
    lines.extend(["", "## Exit Move From Basket Entry VWAP", "", "| Strategy | q10 | q25 | median | q75 | q90 |", "|---|---:|---:|---:|---:|---:|"])
    exit_moves = quantile_table(exits, "strategy", "exit_move_from_entry_vwap_points") if not exits.empty else pd.DataFrame()
    for row in exit_moves.sort_values("strategy").itertuples(index=False):
        lines.append(f"| `{row.strategy}` | {row.q10:.2f} | {row.q25:.2f} | {row.q50:.2f} | {row.q75:.2f} | {row.q90:.2f} |")
    lines.extend(
        [
            "",
            "## Initial Interpretation",
            "",
            "- High basket win rates confirm that management/exit behavior is central to QQ's edge.",
            "- Add-on spacing should next be modeled as a per-minute classification problem using `basket_minute_lifecycle.parquet` negatives and `lifecycle_add_on_events.parquet` positives.",
            "- Exit detection should next test whether final exits occur at fixed basket PnL, fixed points above/below entry VWAP, or layer-dependent TP thresholds.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    positions = pd.read_parquet(POSITIONS)
    m1 = pd.read_csv(M1_CSV, usecols=["time", "high", "low", "close"])
    add_ons = build_add_on_events(positions)
    exits = build_exit_events(positions)
    lifecycle = build_minute_lifecycle(positions, m1)
    add_ons.to_parquet(ADD_ON_EVENTS, index=False)
    exits.to_parquet(EXIT_EVENTS, index=False)
    lifecycle.to_parquet(MINUTE_LIFECYCLE, index=False)
    REPORT_MD.write_text(build_report(add_ons, exits, lifecycle), encoding="utf-8")
    print("Wrote outputs/lifecycle_add_on_events.parquet")
    print("Wrote outputs/lifecycle_exit_events.parquet")
    print("Wrote outputs/basket_minute_lifecycle.parquet")
    print("Wrote outputs/lifecycle_management_report.md")


if __name__ == "__main__":
    main()
