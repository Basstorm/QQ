from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from qq_research.reconstruction import assign_baskets, load_mt5_report, reconstruct_positions_fifo

REPORT_XLSX = PROJECT / "QuantumQueen_backtest_report.xlsx"
M1_CSV = PROJECT / "xauusd_m1_2016_2026.csv"
OUTPUTS = PROJECT / "outputs"


def attach_m1_alignment(deals: pd.DataFrame) -> pd.DataFrame:
    m1 = pd.read_csv(M1_CSV, usecols=["time", "open", "high", "low", "close", "spread"])
    m1["broker_minute"] = pd.to_datetime(m1["time"], utc=True).dt.tz_localize(None)
    m1 = m1.drop(columns=["time"]).set_index("broker_minute").sort_index()
    rows = deals.copy()
    rows["broker_minute"] = rows["time"].dt.floor("min")
    rows = rows.join(m1.add_prefix("m1_"), on="broker_minute")
    rows["m1_available"] = rows["m1_high"].notna()
    distance = np.maximum(rows["m1_low"] - rows["price"], rows["price"] - rows["m1_high"])
    rows["m1_range_distance"] = np.where(rows["m1_available"], np.maximum(distance, 0), np.nan)
    for tolerance in [0.05, 0.10, 0.25, 0.50]:
        safe = str(tolerance).replace(".", "_")
        rows[f"m1_match_tol_{safe}"] = rows["m1_available"] & (rows["price"] >= rows["m1_low"] - tolerance) & (rows["price"] <= rows["m1_high"] + tolerance)
    return rows


def value_counts_table(series: pd.Series) -> str:
    counts = series.value_counts(dropna=False).sort_index()
    return "\n".join(f"| {idx} | {int(value)} |" for idx, value in counts.items())


def grouped_count_table(df: pd.DataFrame, group_col: str, value_col: str = "position_id") -> str:
    counts = df.groupby(group_col, dropna=False)[value_col].count().sort_index()
    return "\n".join(f"| {idx} | {int(value)} |" for idx, value in counts.items())


def strategy_summary_table(positions: pd.DataFrame, baskets: pd.DataFrame) -> str:
    pos = positions.groupby("strategy", dropna=False).agg(
        positions=("position_id", "count"),
        volume=("volume", "sum"),
        pnl=("pnl_est", "sum"),
        avg_hold_min=("holding_seconds", lambda s: s.mean() / 60),
    )
    bas = baskets.groupby("strategy", dropna=False).agg(
        baskets=("basket_id", "count"),
        avg_positions=("position_count", "mean"),
        max_layers_p95=("max_layers", lambda s: s.quantile(0.95)),
    )
    table = pos.join(bas, how="outer").sort_index()
    rows = []
    for strategy, row in table.iterrows():
        rows.append(
            f"| {strategy} | {int(row['positions'])} | {int(row['baskets'])} | {row['volume']:.2f} | {row['pnl']:.2f} | {row['avg_hold_min']:.2f} | {row['avg_positions']:.2f} | {row['max_layers_p95']:.1f} |"
        )
    return "\n".join(rows)


def m15_distribution_table(deals: pd.DataFrame, baskets: pd.DataFrame) -> str:
    entries = deals[deals["entry"].eq("in")].copy()
    rows = [
        "### All entry deals: broker minute modulo 15",
        "",
        "| minute % 15 | count |",
        "|---:|---:|",
        value_counts_table(entries["time"].dt.minute % 15),
        "",
        "### Basket first entries: broker minute modulo 15",
        "",
        "| minute % 15 | count |",
        "|---:|---:|",
        value_counts_table(baskets["first_entry_time"].dt.minute % 15),
    ]
    return "\n".join(rows)


def build_report(deals: pd.DataFrame, positions: pd.DataFrame, baskets: pd.DataFrame) -> str:
    exits = deals[deals["entry"].eq("out")]
    entries = deals[deals["entry"].eq("in")]
    pnl_diff = positions["pnl_est"].sum() - exits["profit"].sum()
    match_025 = deals["m1_match_tol_0_25"].mean()
    entry_match_025 = entries["m1_match_tol_0_25"].mean()
    entry_on_m15 = (entries["time"].dt.minute % 15 == 0).mean()
    basket_on_m15 = (baskets["first_entry_time"].dt.minute % 15 == 0).mean()
    exit_seconds = exits["time"].dt.second
    entry_seconds = entries["time"].dt.second
    lines = [
        "# Phase 1 Trade Reconstruction and Time Alignment Report",
        "",
        "## Executive Summary",
        "",
        f"- Normalized XAUUSD deals: `{len(deals)}`.",
        f"- Entry deals: `{len(entries)}`; exit deals: `{len(exits)}`.",
        f"- Reconstructed position fragments: `{len(positions)}`.",
        f"- Reconstructed baskets: `{len(baskets)}`.",
        f"- Position PnL estimate: `{positions['pnl_est'].sum():.2f}`.",
        f"- Reported exit-deal profit sum: `{exits['profit'].sum():.2f}`.",
        f"- PnL reconstruction difference: `{pnl_diff:.8f}`.",
        f"- M1 match rate at tolerance 0.25, all deals: `{match_025:.4f}`.",
        f"- M1 match rate at tolerance 0.25, entry deals: `{entry_match_025:.4f}`.",
        "- FIFO reconstruction is consistent with the report PnL, so blank exit comments can be assigned back to entry strategies through directional FIFO matching.",
        "",
        "## Strategy-Level Reconstruction Summary",
        "",
        "| Strategy | Positions | Baskets | Volume | PnL est | Avg hold min | Avg positions/basket | P95 max layers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        strategy_summary_table(positions, baskets),
        "",
        "## M15 Timing Diagnostics",
        "",
        f"- Share of all entry deals at broker minute `% 15 == 0`: `{entry_on_m15:.4f}`.",
        f"- Share of basket first entries at broker minute `% 15 == 0`: `{basket_on_m15:.4f}`.",
        "- This does not yet prove or disprove the user's M15-entry model. Entry deals include both initial entries and add-ons. Basket construction is interval-based and may split/merge differently from the EA's internal cycle IDs. Phase 2 should identify initial signal entries more carefully before drawing final conclusions about M15 gating.",
        "",
        m15_distribution_table(deals, baskets),
        "",
        "## Seconds Diagnostics",
        "",
        "### Entry deal second values",
        "",
        "| second | count |",
        "|---:|---:|",
        value_counts_table(entry_seconds.rename_axis("second")),
        "",
        "### Exit deal second values",
        "",
        "| second | count |",
        "|---:|---:|",
        value_counts_table(exit_seconds.rename_axis("second")),
        "",
        "## Output Files",
        "",
        "- `outputs/trades_normalized.parquet`",
        "- `outputs/positions.parquet`",
        "- `outputs/baskets.parquet`",
        "- `outputs/time_alignment_report.md`",
        "",
        "## Phase 2 Notes",
        "",
        "1. Use `strategy` from reconstructed positions for per-strategy behavior profiling.",
        "2. Preserve `broker_time` semantics for candle joins; use `utc_time_est = broker_time - 3h` for session labeling experiments.",
        "3. Initial-entry detection needs refinement beyond interval baskets because add-on entries are represented as normal `in` deals.",
        "4. Basket IDs are reconstructed analytical cycle IDs, not native EA IDs.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    OUTPUTS.mkdir(exist_ok=True)
    _, _, _, deals = load_mt5_report(REPORT_XLSX)
    deals = attach_m1_alignment(deals)
    positions = reconstruct_positions_fifo(deals)
    positions, baskets = assign_baskets(positions)
    deals.to_parquet(OUTPUTS / "trades_normalized.parquet", index=False)
    positions.to_parquet(OUTPUTS / "positions.parquet", index=False)
    baskets.to_parquet(OUTPUTS / "baskets.parquet", index=False)
    (OUTPUTS / "time_alignment_report.md").write_text(build_report(deals, positions, baskets), encoding="utf-8")
    print("Wrote outputs/trades_normalized.parquet")
    print("Wrote outputs/positions.parquet")
    print("Wrote outputs/baskets.parquet")
    print("Wrote outputs/time_alignment_report.md")


if __name__ == "__main__":
    main()
