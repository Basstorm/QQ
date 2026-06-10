from __future__ import annotations

import numpy as np
import pandas as pd
import pandas_ta_classic as ta


def normalize_candles(candles: pd.DataFrame) -> pd.DataFrame:
    rows = candles.copy()
    rows["time"] = pd.to_datetime(rows["time"], utc=True).dt.tz_localize(None)
    return rows.sort_values("time").reset_index(drop=True)


def session_name(hour: int) -> str:
    if 12 <= hour < 16:
        return "london_newyork_overlap"
    if 0 <= hour < 7:
        return "asia"
    if 7 <= hour < 12:
        return "london"
    if 16 <= hour < 21:
        return "newyork"
    return "off_session"


def add_time_session_features(rows: pd.DataFrame, entry_col: str, exit_col: str | None = None, utc_offset_hours: int = 3) -> pd.DataFrame:
    features = rows.copy()
    for col in [entry_col, exit_col]:
        if col is None:
            continue
        label = _time_label(col)
        broker_time = pd.to_datetime(features[col])
        utc_est = broker_time - pd.Timedelta(hours=utc_offset_hours)
        features[f"broker_{label}_time"] = broker_time
        features[f"utc_{label}_time_est"] = utc_est
        features[f"broker_{label}_hour"] = broker_time.dt.hour
        features[f"broker_{label}_weekday"] = broker_time.dt.weekday
        features[f"broker_{label}_month"] = broker_time.dt.month
        features[f"broker_{label}_minute_mod_15"] = broker_time.dt.minute % 15
        features[f"broker_{label}_second"] = broker_time.dt.second
        features[f"broker_{label}_is_friday"] = broker_time.dt.weekday.eq(4)
        features[f"broker_{label}_session"] = broker_time.dt.hour.map(session_name)
        features[f"utc_{label}_hour_est"] = utc_est.dt.hour
        features[f"utc_{label}_weekday_est"] = utc_est.dt.weekday
        features[f"utc_{label}_month_est"] = utc_est.dt.month
        features[f"utc_{label}_session_est"] = utc_est.dt.hour.map(session_name)
        features[f"utc_{label}_in_asia_est"] = utc_est.dt.hour.between(0, 6, inclusive="both")
        features[f"utc_{label}_in_london_est"] = utc_est.dt.hour.between(7, 15, inclusive="both")
        features[f"utc_{label}_in_newyork_est"] = utc_est.dt.hour.between(12, 20, inclusive="both")
        features[f"utc_{label}_in_london_newyork_overlap_est"] = utc_est.dt.hour.between(12, 15, inclusive="both")
    return features


def attach_m15_entry_context(
    rows: pd.DataFrame,
    m15: pd.DataFrame,
    lookbacks: tuple[int, ...] = (1, 2, 4, 8, 16, 32),
    atr_window: int = 14,
    ema_spans: tuple[int, ...] = (8, 21, 50),
    entry_time_col: str = "entry_time",
    entry_price_col: str = "entry_price",
) -> pd.DataFrame:
    features = rows.copy()
    candle_features = build_m15_candle_features(m15, lookbacks, atr_window, ema_spans)
    features["entry_m15_time"] = pd.to_datetime(features[entry_time_col]).dt.floor("15min")
    features = features.join(candle_features.set_index("entry_m15_time"), on="entry_m15_time")
    if entry_price_col in features:
        m15_range = features["m15_high"] - features["m15_low"]
        features["entry_price_position_in_m15_range"] = np.where(m15_range.ne(0), (features[entry_price_col] - features["m15_low"]) / m15_range, np.nan)
        for span in ema_spans:
            features[f"entry_price_distance_to_m15_ema_{span}"] = features[entry_price_col] - features[f"m15_ema_{span}"]
    if "direction" in features:
        sign = features["direction"].map({"long": 1, "short": -1}).fillna(0)
        for lookback in lookbacks:
            features[f"m15_momentum_{lookback}_directional_points"] = features[f"m15_momentum_{lookback}_close_points"] * sign
    return features


def build_m15_candle_features(
    m15: pd.DataFrame,
    lookbacks: tuple[int, ...] = (1, 2, 4, 8, 16, 32),
    atr_window: int = 14,
    ema_spans: tuple[int, ...] = (8, 21, 50),
) -> pd.DataFrame:
    candles = normalize_candles(m15)
    candles = candles.rename(
        columns={
            "time": "entry_m15_time",
            "open": "m15_open",
            "high": "m15_high",
            "low": "m15_low",
            "close": "m15_close",
            "tick_volume": "m15_tick_volume",
            "spread": "m15_spread",
            "real_volume": "m15_real_volume",
        }
    )
    candles["m15_body_points"] = candles["m15_close"] - candles["m15_open"]
    candles["m15_body_abs_points"] = candles["m15_body_points"].abs()
    candles["m15_range_points"] = candles["m15_high"] - candles["m15_low"]
    candles["m15_upper_wick_points"] = candles["m15_high"] - candles[["m15_open", "m15_close"]].max(axis=1)
    candles["m15_lower_wick_points"] = candles[["m15_open", "m15_close"]].min(axis=1) - candles["m15_low"]
    candles["m15_body_to_range"] = np.where(candles["m15_range_points"].ne(0), candles["m15_body_abs_points"] / candles["m15_range_points"], np.nan)
    for lookback in lookbacks:
        candles[f"m15_momentum_{lookback}_close_points"] = candles["m15_close"] - candles["m15_close"].shift(lookback)
        candles[f"m15_recent_high_{lookback}"] = candles["m15_high"].shift(1).rolling(lookback, min_periods=1).max()
        candles[f"m15_recent_low_{lookback}"] = candles["m15_low"].shift(1).rolling(lookback, min_periods=1).min()
        candles[f"m15_breakout_above_recent_high_{lookback}_points"] = candles["m15_high"] - candles[f"m15_recent_high_{lookback}"]
        candles[f"m15_breakout_below_recent_low_{lookback}_points"] = candles[f"m15_recent_low_{lookback}"] - candles["m15_low"]
    prev_close = candles["m15_close"].shift(1)
    true_range = pd.concat(
        [
            candles["m15_high"] - candles["m15_low"],
            (candles["m15_high"] - prev_close).abs(),
            (candles["m15_low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    rolling_atr = true_range.rolling(atr_window, min_periods=1).mean()
    ta_atr = ta.atr(candles["m15_high"], candles["m15_low"], candles["m15_close"], length=atr_window)
    candles[f"m15_atr_{atr_window}"] = ta_atr.fillna(rolling_atr) if ta_atr is not None else rolling_atr
    candles[f"m15_range_atr_{atr_window}_ratio"] = np.where(candles[f"m15_atr_{atr_window}"].ne(0), candles["m15_range_points"] / candles[f"m15_atr_{atr_window}"], np.nan)
    candles[f"m15_atr_{atr_window}_percentile_252"] = candles[f"m15_atr_{atr_window}"].rolling(252, min_periods=20).rank(pct=True)
    for span in ema_spans:
        fallback_ema = candles["m15_close"].ewm(span=span, adjust=False, min_periods=1).mean()
        ta_ema = ta.ema(candles["m15_close"], length=span)
        candles[f"m15_ema_{span}"] = ta_ema.fillna(fallback_ema) if ta_ema is not None else fallback_ema
        candles[f"m15_ema_{span}_slope_4"] = candles[f"m15_ema_{span}"] - candles[f"m15_ema_{span}"].shift(4)
        candles[f"m15_close_distance_to_ema_{span}"] = candles["m15_close"] - candles[f"m15_ema_{span}"]
    candles["m15_rsi_14"] = ta.rsi(candles["m15_close"], length=14)
    adx = ta.adx(candles["m15_high"], candles["m15_low"], candles["m15_close"], length=14)
    if adx is not None:
        candles["m15_adx_14"] = adx["ADX_14"]
        candles["m15_dmp_14"] = adx["DMP_14"]
        candles["m15_dmn_14"] = adx["DMN_14"]
    macd = ta.macd(candles["m15_close"], fast=12, slow=26, signal=9)
    if macd is not None:
        candles["m15_macd_12_26_9"] = macd["MACD_12_26_9"]
        candles["m15_macd_hist_12_26_9"] = macd["MACDh_12_26_9"]
        candles["m15_macd_signal_12_26_9"] = macd["MACDs_12_26_9"]
    return candles


def compute_position_path_features(
    rows: pd.DataFrame,
    m1: pd.DataFrame,
    id_col: str = "position_id",
    entry_time_col: str = "entry_time",
    exit_time_col: str = "exit_time",
    entry_price_col: str = "entry_price",
    exit_price_col: str = "exit_price",
) -> pd.DataFrame:
    features = rows.copy()
    candles = normalize_candles(m1).set_index("time").sort_index()
    path_rows = []
    for row in features.to_dict(orient="records"):
        start = pd.Timestamp(row[entry_time_col]).floor("min")
        end = pd.Timestamp(row[exit_time_col]).floor("min")
        path = candles.loc[start:end]
        path_rows.append(_path_feature_row(row, path, id_col, entry_time_col, entry_price_col, exit_price_col))
    return features.merge(pd.DataFrame(path_rows), on=id_col, how="left")


def add_basket_structure_features(positions: pd.DataFrame, baskets: pd.DataFrame | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = positions.sort_values(["basket_id", "entry_time", "position_id"], kind="mergesort").copy()
    rows["entry_sequence_in_basket"] = rows.groupby("basket_id").cumcount() + 1
    first = rows.groupby("basket_id").agg(
        basket_first_entry_time=("entry_time", "min"),
        initial_entry_price=("entry_price", "first"),
        initial_volume=("volume", "first"),
    )
    rows = rows.join(first, on="basket_id")
    rows["is_initial_entry"] = rows["entry_sequence_in_basket"].eq(1)
    rows["minutes_from_basket_first_entry"] = (rows["entry_time"] - rows["basket_first_entry_time"]).dt.total_seconds() / 60
    rows["entry_price_delta_from_initial"] = rows["entry_price"] - rows["initial_entry_price"]
    rows["entry_price_abs_delta_from_initial"] = rows["entry_price_delta_from_initial"].abs()
    rows["volume_multiplier_vs_initial"] = np.where(rows["initial_volume"].ne(0), rows["volume"] / rows["initial_volume"], np.nan)
    basket_features = _basket_structure_from_positions(rows)
    if baskets is not None:
        basket_features = baskets.merge(basket_features, on="basket_id", how="left", suffixes=("", "_structure"))
    return rows.sort_values("position_id").reset_index(drop=True), basket_features.sort_values("basket_id").reset_index(drop=True)


def _time_label(col: str) -> str:
    if "entry" in col:
        return "entry"
    if "exit" in col:
        return "exit"
    return col.removesuffix("_time")


def _path_feature_row(row: dict[str, object], path: pd.DataFrame, id_col: str, entry_time_col: str, entry_price_col: str, exit_price_col: str) -> dict[str, object]:
    result: dict[str, object] = {id_col: row[id_col], "m1_path_bar_count": int(len(path))}
    if path.empty:
        result.update(
            {
                "m1_path_available": False,
                "m1_path_high_max": np.nan,
                "m1_path_low_min": np.nan,
                "m1_mfe_points": np.nan,
                "m1_mae_points": np.nan,
                "m1_net_exit_move_points": np.nan,
                "m1_time_to_mfe_minutes": np.nan,
                "m1_time_to_mae_minutes": np.nan,
                "m1_spread_mean": np.nan,
                "m1_spread_max": np.nan,
                "m1_tick_volume_sum": np.nan,
                "m1_tick_volume_mean": np.nan,
            }
        )
        return result
    entry_price = float(row[entry_price_col])
    exit_price = float(row[exit_price_col])
    high_max = float(path["high"].max())
    low_min = float(path["low"].min())
    direction = row.get("direction")
    if direction == "short":
        mfe = entry_price - low_min
        mae = high_max - entry_price
        net = entry_price - exit_price
        mfe_time = path["low"].idxmin()
        mae_time = path["high"].idxmax()
    else:
        mfe = high_max - entry_price
        mae = entry_price - low_min
        net = exit_price - entry_price
        mfe_time = path["high"].idxmax()
        mae_time = path["low"].idxmin()
    start = pd.Timestamp(row[entry_time_col]).floor("min")
    result.update(
        {
            "m1_path_available": True,
            "m1_path_high_max": high_max,
            "m1_path_low_min": low_min,
            "m1_path_close_last": float(path["close"].iloc[-1]),
            "m1_mfe_points": float(mfe),
            "m1_mae_points": float(mae),
            "m1_net_exit_move_points": float(net),
            "m1_time_to_mfe_minutes": (pd.Timestamp(mfe_time) - start).total_seconds() / 60,
            "m1_time_to_mae_minutes": (pd.Timestamp(mae_time) - start).total_seconds() / 60,
            "m1_spread_mean": float(path["spread"].mean()),
            "m1_spread_max": float(path["spread"].max()),
            "m1_tick_volume_sum": float(path["tick_volume"].sum()),
            "m1_tick_volume_mean": float(path["tick_volume"].mean()),
        }
    )
    return result


def _basket_structure_from_positions(rows: pd.DataFrame) -> pd.DataFrame:
    records = []
    for basket_id, group in rows.groupby("basket_id", sort=True):
        group = group.sort_values(["entry_time", "position_id"], kind="mergesort")
        entry_deltas = group["entry_time"].diff().dt.total_seconds().div(60).iloc[1:]
        price_deltas = group["entry_price"].diff().abs().iloc[1:]
        close_span = (group["exit_time"].max() - group["exit_time"].min()).total_seconds() / 60
        initial = group.iloc[0]
        final_exit = group.sort_values(["exit_time", "position_id"], kind="mergesort").iloc[-1]
        records.append(
            {
                "basket_id": basket_id,
                "add_on_count": int(max(len(group) - 1, 0)),
                "initial_position_id": int(initial["position_id"]),
                "initial_entry_time": initial["entry_time"],
                "initial_entry_price": float(initial["entry_price"]),
                "initial_volume": float(initial["volume"]),
                "final_exit_time": final_exit["exit_time"],
                "final_exit_price": float(final_exit["exit_price"]) if "exit_price" in final_exit else np.nan,
                "add_on_spacing_minutes_mean": float(entry_deltas.mean()) if len(entry_deltas) else np.nan,
                "add_on_spacing_minutes_min": float(entry_deltas.min()) if len(entry_deltas) else np.nan,
                "add_on_spacing_minutes_max": float(entry_deltas.max()) if len(entry_deltas) else np.nan,
                "add_on_spacing_price_abs_mean": float(price_deltas.mean()) if len(price_deltas) else np.nan,
                "add_on_spacing_price_abs_min": float(price_deltas.min()) if len(price_deltas) else np.nan,
                "add_on_spacing_price_abs_max": float(price_deltas.max()) if len(price_deltas) else np.nan,
                "max_volume_multiplier_vs_initial": float(group["volume_multiplier_vs_initial"].max()),
                "close_span_minutes": float(close_span),
                "closed_together_within_1m": bool(close_span <= 1.0),
            }
        )
    return pd.DataFrame(records)
