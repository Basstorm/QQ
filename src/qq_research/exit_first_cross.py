from __future__ import annotations

import numpy as np
import pandas as pd


def compute_first_cross_events(lifecycle: pd.DataFrame, thresholds: pd.DataFrame, threshold_col: str, move_col: str) -> pd.DataFrame:
    threshold_map = thresholds.set_index(["strategy", "open_layer_count"])[threshold_col].to_dict()
    rows = []
    ordered = lifecycle.sort_values(["basket_id", "time"])
    for basket_id, group in ordered.groupby("basket_id", sort=True):
        exit_rows = group[group["is_final_exit_minute"]]
        if exit_rows.empty:
            continue
        actual_exit_time = pd.Timestamp(exit_rows["time"].max())
        exit_row = exit_rows.sort_values("time").iloc[-1]
        signals = []
        for row in group.itertuples(index=False):
            threshold = threshold_map.get((row.strategy, int(row.open_layer_count)))
            if threshold is None:
                signals.append(False)
                continue
            signals.append(getattr(row, move_col) >= threshold)
        signal_frame = group.loc[signals]
        first_cross_time = pd.Timestamp(signal_frame["time"].iloc[0]) if not signal_frame.empty else pd.NaT
        lag_minutes = (actual_exit_time - first_cross_time).total_seconds() / 60 if pd.notna(first_cross_time) else np.nan
        rows.append(
            {
                "basket_id": basket_id,
                "strategy": exit_row["strategy"],
                "actual_exit_time": actual_exit_time,
                "open_layer_count_at_exit": int(exit_row["open_layer_count"]),
                "threshold_at_exit": threshold_map.get((exit_row["strategy"], int(exit_row["open_layer_count"]))),
                "first_cross_time": first_cross_time,
                "lag_minutes": lag_minutes,
                "cross_found": pd.notna(first_cross_time),
            }
        )
    return pd.DataFrame(rows)


def summarize_first_cross_lags(events: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (strategy, layer), group in events.groupby(["strategy", "open_layer_count_at_exit"], sort=True):
        cross_found = group["cross_found"] if "cross_found" in group else group["lag_minutes"].notna()
        found = group[cross_found]
        lags = found["lag_minutes"]
        rows.append(
            {
                "strategy": strategy,
                "open_layer_count_at_exit": int(layer),
                "basket_count": int(len(group)),
                "cross_found_count": int(len(found)),
                "cross_found_pct": len(found) / len(group) * 100 if len(group) else 0.0,
                "within_0m_pct": (lags.eq(0).mean() * 100) if len(found) else 0.0,
                "within_1m_pct": (lags.le(1).mean() * 100) if len(found) else 0.0,
                "within_5m_pct": (lags.le(5).mean() * 100) if len(found) else 0.0,
                "lag_median": float(lags.median()) if len(found) else np.nan,
                "lag_q75": float(lags.quantile(0.75)) if len(found) else np.nan,
                "lag_q90": float(lags.quantile(0.90)) if len(found) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_first_cross_report(summary: pd.DataFrame, variant: str) -> str:
    lines = [
        f"# Exit First-Cross Analysis ({variant})",
        "",
        "| Strategy | Exit layers | Baskets | Cross found % | Within 0m % | Within 1m % | Within 5m % | Lag median | Lag q75 | Lag q90 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary.sort_values(["strategy", "open_layer_count_at_exit"]).itertuples(index=False):
        lines.append(
            f"| `{row.strategy}` | {int(row.open_layer_count_at_exit)} | {int(row.basket_count)} | {row.cross_found_pct:.1f} | {row.within_0m_pct:.1f} | {row.within_1m_pct:.1f} | {row.within_5m_pct:.1f} | {row.lag_median:.1f} | {row.lag_q75:.1f} | {row.lag_q90:.1f} |"
        )
    return "\n".join(lines) + "\n"
