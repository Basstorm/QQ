from __future__ import annotations

import numpy as np
import pandas as pd


def _session_label(hour: int) -> str:
    if 1 <= hour <= 4:
        return "01-04"
    if 5 <= hour <= 8:
        return "05-08"
    if 9 <= hour <= 12:
        return "09-12"
    if 13 <= hour <= 16:
        return "13-16"
    if 17 <= hour <= 20:
        return "17-20"
    if 21 <= hour <= 23:
        return "21-23"
    return "00"


def _holding_bucket(minutes: float) -> str:
    if minutes <= 30:
        return "<=30m"
    if minutes <= 120:
        return "30-120m"
    if minutes <= 360:
        return "120-360m"
    if minutes <= 1440:
        return "360-1440m"
    return ">1440m"


def add_s10_exit_modes(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["time"] = pd.to_datetime(result["time"])
    result["s10_session"] = result["time"].dt.hour.map(_session_label)
    result["s10_holding_bucket"] = result["minutes_since_initial_entry"].map(_holding_bucket)
    result["s10_mode"] = result["s10_session"] + "|" + result["s10_holding_bucket"]
    return result


def mine_s10_mode_tp_thresholds(frame: pd.DataFrame, min_positives: int = 3) -> pd.DataFrame:
    rows = []
    for mode, group in frame.groupby("s10_mode", sort=True):
        positives = group[group["is_final_exit_minute"]]
        if len(positives) < min_positives:
            continue
        moves = positives["close_move_from_open_vwap_points"]
        rows.append(
            {
                "s10_mode": mode,
                "positive_count": int(len(positives)),
                "candidate_count": int(len(group)),
                "tp_q25": float(moves.quantile(0.25)),
                "tp_median": float(moves.quantile(0.50)),
                "tp_q75": float(moves.quantile(0.75)),
                "tp_q90": float(moves.quantile(0.90)),
            }
        )
    return pd.DataFrame(rows)


def compute_mode_first_cross_events(lifecycle: pd.DataFrame, thresholds: pd.DataFrame, threshold_col: str) -> pd.DataFrame:
    threshold_map = thresholds.set_index("s10_mode")[threshold_col].to_dict()
    rows = []
    ordered = lifecycle.sort_values(["basket_id", "time"])
    for basket_id, group in ordered.groupby("basket_id", sort=True):
        exit_rows = group[group["is_final_exit_minute"]]
        if exit_rows.empty:
            continue
        actual_exit_time = pd.Timestamp(exit_rows["time"].max())
        exit_row = exit_rows.sort_values("time").iloc[-1]
        row_thresholds = group["s10_mode"].map(threshold_map).fillna(np.inf)
        signals = group["close_move_from_open_vwap_points"].ge(row_thresholds)
        signal_frame = group[signals]
        first_cross_time = pd.Timestamp(signal_frame["time"].iloc[0]) if not signal_frame.empty else pd.NaT
        rows.append(
            {
                "basket_id": basket_id,
                "strategy": exit_row["strategy"],
                "mode_at_exit": exit_row["s10_mode"],
                "actual_exit_time": actual_exit_time,
                "first_cross_time": first_cross_time,
                "lag_minutes": (actual_exit_time - first_cross_time).total_seconds() / 60 if pd.notna(first_cross_time) else np.nan,
                "cross_found": pd.notna(first_cross_time),
            }
        )
    return pd.DataFrame(rows)


def compute_final_mode_oracle_events(lifecycle: pd.DataFrame, thresholds: pd.DataFrame, threshold_col: str) -> pd.DataFrame:
    threshold_map = thresholds.set_index("s10_mode")[threshold_col].to_dict()
    rows = []
    ordered = lifecycle.sort_values(["basket_id", "time"])
    for basket_id, group in ordered.groupby("basket_id", sort=True):
        exit_rows = group[group["is_final_exit_minute"]]
        if exit_rows.empty:
            continue
        exit_row = exit_rows.sort_values("time").iloc[-1]
        final_mode = exit_row["s10_mode"]
        threshold = threshold_map.get(final_mode, np.inf)
        eligible = group[group["s10_mode"].eq(final_mode)]
        signal_frame = eligible[eligible["close_move_from_open_vwap_points"].ge(threshold)]
        first_cross_time = pd.Timestamp(signal_frame["time"].iloc[0]) if not signal_frame.empty else pd.NaT
        actual_exit_time = pd.Timestamp(exit_row["time"])
        rows.append(
            {
                "basket_id": basket_id,
                "strategy": exit_row["strategy"],
                "mode_at_exit": final_mode,
                "actual_exit_time": actual_exit_time,
                "first_cross_time": first_cross_time,
                "lag_minutes": (actual_exit_time - first_cross_time).total_seconds() / 60 if pd.notna(first_cross_time) else np.nan,
                "cross_found": pd.notna(first_cross_time),
            }
        )
    return pd.DataFrame(rows)


def build_s10_mode_tp_report(thresholds: pd.DataFrame, events: pd.DataFrame, threshold_col: str) -> str:
    found = events[events["cross_found"]]
    lines = [
        "# T5/S10 Mode-Conditioned TP Mining",
        "",
        f"Threshold column: `{threshold_col}`",
        "",
        "## First-Cross Timing Summary",
        "",
        f"- Baskets: {len(events)}",
        f"- Cross found: {len(found)} ({len(found) / len(events) * 100:.1f}%)" if len(events) else "- Cross found: 0 (0.0%)",
        f"- Within 1m of actual exit: {found['lag_minutes'].le(1).mean() * 100:.1f}%" if len(found) else "- Within 1m of actual exit: 0.0%",
        f"- Median lag: {found['lag_minutes'].median():.1f}m" if len(found) else "- Median lag: nan",
        "",
        "## TP by S10 Mode",
        "",
        "| S10 mode | Positives | TP q25 | TP median | TP q75 | TP q90 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in thresholds.sort_values("s10_mode").itertuples(index=False):
        positive_count = getattr(row, "positive_count", 0)
        tp_q25 = getattr(row, "tp_q25", np.nan)
        tp_q75 = getattr(row, "tp_q75", np.nan)
        tp_q90 = getattr(row, "tp_q90", np.nan)
        lines.append(
            f"| `{row.s10_mode}` | {int(positive_count)} | {tp_q25:.2f} | {row.tp_median:.2f} | {tp_q75:.2f} | {tp_q90:.2f} |"
        )
    return "\n".join(lines) + "\n"
