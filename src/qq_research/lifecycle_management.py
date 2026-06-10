from __future__ import annotations

import numpy as np
import pandas as pd


def directional_move(direction: str, start_price: float, end_price: float) -> float:
    if direction == "short":
        return start_price - end_price
    return end_price - start_price


def build_add_on_events(positions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for basket_id, group in positions.sort_values(["basket_id", "entry_time", "position_id"]).groupby("basket_id", sort=True):
        ordered = group.reset_index(drop=True)
        if len(ordered) <= 1:
            continue
        initial = ordered.iloc[0]
        for idx in range(1, len(ordered)):
            row = ordered.iloc[idx]
            prev = ordered.iloc[idx - 1]
            direction = str(row["direction"])
            rows.append(
                {
                    "basket_id": basket_id,
                    "strategy": row["strategy"],
                    "direction": direction,
                    "layer_index": idx + 1,
                    "entry_time": row["entry_time"],
                    "entry_price": float(row["entry_price"]),
                    "prev_entry_time": prev["entry_time"],
                    "prev_entry_price": float(prev["entry_price"]),
                    "initial_entry_price": float(initial["entry_price"]),
                    "minutes_since_prev_entry": (row["entry_time"] - prev["entry_time"]).total_seconds() / 60,
                    "same_minute_as_prev_entry": row["entry_time"].floor("min") == prev["entry_time"].floor("min"),
                    "adverse_from_prev_entry_points": -directional_move(direction, float(prev["entry_price"]), float(row["entry_price"])),
                    "adverse_from_initial_entry_points": -directional_move(direction, float(initial["entry_price"]), float(row["entry_price"])),
                    "volume": float(row["volume"]),
                    "prev_volume": float(prev["volume"]),
                    "initial_volume": float(initial["volume"]),
                    "volume_multiplier_vs_prev": float(row["volume"]) / float(prev["volume"]) if float(prev["volume"]) else np.nan,
                    "volume_multiplier_vs_initial": float(row["volume"]) / float(initial["volume"]) if float(initial["volume"]) else np.nan,
                }
            )
    return pd.DataFrame(rows)


def build_exit_events(positions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for basket_id, group in positions.sort_values(["basket_id", "entry_time", "position_id"]).groupby("basket_id", sort=True):
        direction = str(group["direction"].iloc[0])
        total_volume = float(group["volume"].sum())
        entry_vwap = float((group["entry_price"] * group["volume"]).sum() / total_volume) if total_volume else np.nan
        exit_vwap = float((group["exit_price"] * group["volume"]).sum() / total_volume) if total_volume else np.nan
        final_exit_time = group["exit_time"].max()
        final_closes = group[group["exit_time"].eq(final_exit_time)]
        final_exit_price = float((final_closes["exit_price"] * final_closes["volume"]).sum() / final_closes["volume"].sum())
        rows.append(
            {
                "basket_id": basket_id,
                "strategy": group["strategy"].iloc[0],
                "direction": direction,
                "position_count": int(len(group)),
                "total_volume": total_volume,
                "entry_vwap": entry_vwap,
                "exit_vwap": exit_vwap,
                "final_exit_time": final_exit_time,
                "final_exit_price": final_exit_price,
                "exit_move_from_entry_vwap_points": directional_move(direction, entry_vwap, final_exit_price),
                "weighted_exit_move_from_entry_vwap_points": directional_move(direction, entry_vwap, exit_vwap),
                "pnl_est": float(group["pnl_est"].sum()) if "pnl_est" in group else np.nan,
                "close_span_minutes": (group["exit_time"].max() - group["exit_time"].min()).total_seconds() / 60,
            }
        )
    return pd.DataFrame(rows)


def build_minute_lifecycle(positions: pd.DataFrame, m1: pd.DataFrame) -> pd.DataFrame:
    prices = m1.copy()
    prices["time"] = pd.to_datetime(prices["time"]).dt.tz_localize(None)
    prices = prices.drop_duplicates("time").set_index("time").sort_index()
    rows = []
    for basket_id, group in positions.sort_values(["basket_id", "entry_time", "position_id"]).groupby("basket_id", sort=True):
        group = group.copy()
        group["entry_time"] = pd.to_datetime(group["entry_time"])
        group["exit_time"] = pd.to_datetime(group["exit_time"])
        start = group["entry_time"].min().floor("min")
        end = group["exit_time"].max().floor("min")
        timeline = prices.loc[start:end]
        if timeline.empty:
            continue
        direction = str(group["direction"].iloc[0])
        initial_time = group["entry_time"].min().floor("min")
        add_on_minutes = set(group.loc[group["entry_time"].ne(group["entry_time"].min()), "entry_time"].dt.floor("min"))
        final_exit_minute = group["exit_time"].max().floor("min")
        times = pd.Series(timeline.index)
        active = (
            (times.to_numpy(dtype="datetime64[ns]")[:, None] >= group["entry_time"].dt.floor("min").to_numpy(dtype="datetime64[ns]")[None, :])
            & (times.to_numpy(dtype="datetime64[ns]")[:, None] <= group["exit_time"].dt.floor("min").to_numpy(dtype="datetime64[ns]")[None, :])
        )
        pre_active = (
            (times.to_numpy(dtype="datetime64[ns]")[:, None] > group["entry_time"].dt.floor("min").to_numpy(dtype="datetime64[ns]")[None, :])
            & (times.to_numpy(dtype="datetime64[ns]")[:, None] <= group["exit_time"].dt.floor("min").to_numpy(dtype="datetime64[ns]")[None, :])
        )
        volumes = group["volume"].to_numpy(dtype=float)
        entry_values = group["entry_price"].to_numpy(dtype=float) * volumes
        active_float = active.astype(float)
        volume_matrix = active_float * volumes
        total_volume = volume_matrix.sum(axis=1)
        valid = total_volume > 0
        if not valid.any():
            continue
        entry_vwap = np.full(len(times), np.nan)
        entry_vwap[valid] = (active_float * entry_values).sum(axis=1)[valid] / total_volume[valid]
        close = timeline["close"].to_numpy(dtype=float)
        pre_active_float = pre_active.astype(float)
        pre_total_volume = (pre_active_float * volumes).sum(axis=1)
        pre_entry_vwap = np.full(len(times), np.nan)
        pre_valid = pre_total_volume > 0
        pre_entry_vwap[pre_valid] = (pre_active_float * entry_values).sum(axis=1)[pre_valid] / pre_total_volume[pre_valid]
        entry_minutes = group["entry_time"].dt.floor("min").to_numpy(dtype="datetime64[ns]")
        time_values = times.to_numpy(dtype="datetime64[ns]")
        pre_last_entry_price = np.full(len(times), np.nan)
        minutes_since_pre_last_entry = np.full(len(times), np.nan)
        for row_idx, time_value in enumerate(time_values):
            prior = np.where(entry_minutes < time_value)[0]
            if len(prior):
                last_idx = prior[-1]
                pre_last_entry_price[row_idx] = float(group["entry_price"].iloc[last_idx])
                minutes_since_pre_last_entry[row_idx] = (pd.Timestamp(time_value) - pd.Timestamp(entry_minutes[last_idx])).total_seconds() / 60
        if direction == "short":
            move_from_vwap = entry_vwap - close
            pre_move_from_vwap = pre_entry_vwap - close
            adverse_from_pre_last_entry = close - pre_last_entry_price
        else:
            move_from_vwap = close - entry_vwap
            pre_move_from_vwap = close - pre_entry_vwap
            adverse_from_pre_last_entry = pre_last_entry_price - close
        basket_rows = pd.DataFrame(
            {
                "basket_id": basket_id,
                "strategy": group["strategy"].iloc[0],
                "direction": direction,
                "time": times,
                "m1_close": close,
                "open_layer_count": active.sum(axis=1).astype(int),
                "open_total_volume": total_volume,
                "open_entry_vwap": entry_vwap,
                "close_move_from_open_vwap_points": move_from_vwap,
                "pre_open_layer_count": pre_active.sum(axis=1).astype(int),
                "pre_open_total_volume": pre_total_volume,
                "pre_open_entry_vwap": pre_entry_vwap,
                "close_move_from_pre_open_vwap_points": pre_move_from_vwap,
                "pre_last_entry_price": pre_last_entry_price,
                "minutes_since_pre_last_entry": minutes_since_pre_last_entry,
                "adverse_from_pre_last_entry_points": adverse_from_pre_last_entry,
                "minutes_since_initial_entry": (times - initial_time).dt.total_seconds() / 60,
                "is_add_on_minute": times.isin(add_on_minutes),
                "is_final_exit_minute": times.eq(final_exit_minute),
            }
        )
        rows.extend(basket_rows[valid].to_dict(orient="records"))
    return pd.DataFrame(rows)


def summarize_quantiles(frame: pd.DataFrame, group_col: str, value_col: str) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame()
    summary = frame.groupby(group_col)[value_col].quantile([0.1, 0.25, 0.5, 0.75, 0.9]).unstack()
    summary.columns = [f"{value_col}_q{int(q * 100)}" for q in summary.columns]
    return summary.reset_index()
