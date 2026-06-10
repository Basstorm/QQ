from __future__ import annotations

import inspect
from collections.abc import Callable

import numpy as np
import pandas as pd
import pandas_ta_classic as ta
from sklearn.metrics import roc_auc_score


def normalize_m15(m15: pd.DataFrame) -> pd.DataFrame:
    rows = m15.copy()
    rows["time"] = pd.to_datetime(rows["time"], utc=True).dt.tz_localize(None)
    return rows.sort_values("time").reset_index(drop=True)


def build_ma_relationship_features(
    candles: pd.DataFrame,
    ma_specs: dict[str, list[int]] | None = None,
    pairs: list[tuple[str, int, int]] | None = None,
) -> pd.DataFrame:
    rows = candles[["time", "close"]].copy()
    ma_specs = ma_specs or {"ema": [8, 21, 50], "sma": [8, 21, 50], "wma": [8, 21, 50], "hma": [16, 32]}
    for ma_name, lengths in ma_specs.items():
        for length in lengths:
            series = compute_ma(rows["close"], ma_name, length)
            rows[f"{ma_name}_{length}"] = series
            rows[f"{ma_name}_{length}_slope_4"] = series - series.shift(4)
            rows[f"close_minus_{ma_name}_{length}"] = rows["close"] - series
    if pairs is None:
        pairs = []
        for ma_name, lengths in ma_specs.items():
            for fast, slow in zip(lengths[:-1], lengths[1:]):
                pairs.append((ma_name, fast, slow))
    for ma_name, fast, slow in pairs:
        fast_col = f"{ma_name}_{fast}"
        slow_col = f"{ma_name}_{slow}"
        if fast_col not in rows or slow_col not in rows:
            continue
        spread = rows[fast_col] - rows[slow_col]
        rows[f"{fast_col}_gt_{slow_col}"] = spread > 0
        rows[f"{fast_col}_minus_{slow_col}"] = spread
        rows[f"{fast_col}_cross_above_{slow_col}"] = (spread > 0) & (spread.shift(1) <= 0)
        rows[f"{fast_col}_cross_below_{slow_col}"] = (spread < 0) & (spread.shift(1) >= 0)
        rows[f"bars_since_{fast_col}_cross_above_{slow_col}"] = bars_since(rows[f"{fast_col}_cross_above_{slow_col}"])
        rows[f"bars_since_{fast_col}_cross_below_{slow_col}"] = bars_since(rows[f"{fast_col}_cross_below_{slow_col}"])
    raw_ma_columns = [f"{ma_name}_{length}" for ma_name, lengths in ma_specs.items() for length in lengths]
    return rows.drop(columns=["close", *[column for column in raw_ma_columns if column in rows]])


def compute_ma(close: pd.Series, ma_name: str, length: int) -> pd.Series:
    fn = getattr(ta, ma_name)
    result = fn(close, length=length)
    if result is None:
        return close.rolling(length, min_periods=1).mean()
    return pd.Series(result, index=close.index)


def bars_since(events: pd.Series) -> pd.Series:
    out = []
    last_seen = None
    for idx, value in enumerate(events.fillna(False).astype(bool)):
        if value:
            last_seen = idx
            out.append(0)
        elif last_seen is None:
            out.append(np.nan)
        else:
            out.append(idx - last_seen)
    return pd.Series(out, index=events.index)


def build_entry_label_frame(m15_times: pd.Series | pd.DatetimeIndex, basket_features: pd.DataFrame) -> pd.DataFrame:
    times = pd.Series(pd.to_datetime(m15_times), name="time")
    labels = pd.DataFrame({"time": times})
    for strategy in sorted(basket_features["strategy"].dropna().unique()):
        strategy_times = set(pd.to_datetime(basket_features.loc[basket_features["strategy"].eq(strategy), "entry_m15_time"]))
        labels[strategy] = labels["time"].isin(strategy_times)
    return labels


def compute_indicator_feature_frame(m15: pd.DataFrame) -> pd.DataFrame:
    candles = normalize_m15(m15)
    features = pd.DataFrame({"time": candles["time"]})
    feature_parts = [
        build_ma_relationship_features(candles),
        compute_ta_feature_family(candles),
    ]
    for part in feature_parts:
        features = features.merge(part, on="time", how="left")
    return features


def compute_ta_feature_family(candles: pd.DataFrame) -> pd.DataFrame:
    features = pd.DataFrame({"time": candles["time"]})
    close = candles["close"]
    high = candles["high"]
    low = candles["low"]
    volume = candles["tick_volume"] if "tick_volume" in candles else None
    add_series_grid(features, "rsi", lambda length: ta.rsi(close, length=length), [5, 8, 14, 21, 34])
    add_series_grid(features, "cci", lambda length: ta.cci(high, low, close, length=length), [10, 14, 20, 34])
    add_series_grid(features, "cmo", lambda length: ta.cmo(close, length=length), [9, 14, 21])
    add_series_grid(features, "roc", lambda length: ta.roc(close, length=length), [5, 10, 20, 34])
    add_series_grid(features, "mom", lambda length: ta.mom(close, length=length), [5, 10, 20, 34])
    add_dataframe_indicator(features, "adx", lambda length: ta.adx(high, low, close, length=length), [7, 14, 21])
    add_dataframe_indicator(features, "aroon", lambda length: ta.aroon(high, low, length=length), [14, 25])
    add_dataframe_indicator(features, "bbands", lambda length: ta.bbands(close, length=length, std=2), [10, 20, 34])
    add_dataframe_indicator(features, "donchian", lambda length: ta.donchian(high, low, lower_length=length, upper_length=length), [10, 20, 34])
    add_dataframe_indicator(features, "kc", lambda length: ta.kc(high, low, close, length=length), [10, 20])
    add_series_grid(features, "chop", lambda length: ta.chop(high, low, close, length=length), [14, 21])
    add_series_grid(features, "fisher", lambda length: first_column(ta.fisher(high, low, length=length)), [9, 14])
    add_optional_series(features, "ao", lambda: ta.ao(high, low))
    add_optional_series(features, "bop", lambda: ta.bop(candles["open"], high, low, close))
    if volume is not None:
        add_optional_series(features, "cmf_20", lambda: ta.cmf(high, low, close, volume, length=20))
        add_optional_series(features, "efi_13", lambda: ta.efi(close, volume, length=13))
    return features


def add_series_grid(features: pd.DataFrame, prefix: str, factory: Callable[[int], object], lengths: list[int]) -> None:
    for length in lengths:
        add_optional_series(features, f"{prefix}_{length}", lambda length=length: factory(length))


def add_dataframe_indicator(features: pd.DataFrame, prefix: str, factory: Callable[[int], object], lengths: list[int]) -> None:
    for length in lengths:
        result = safe_call(lambda length=length: factory(length))
        if isinstance(result, pd.DataFrame):
            for col in result.columns:
                features[f"{prefix}_{length}_{clean_column_name(str(col))}"] = pd.to_numeric(result[col], errors="coerce")


def add_optional_series(features: pd.DataFrame, name: str, factory: Callable[[], object]) -> None:
    result = safe_call(factory)
    if result is None:
        return
    if isinstance(result, pd.DataFrame):
        result = first_column(result)
    features[name] = pd.to_numeric(pd.Series(result, index=features.index), errors="coerce")


def first_column(frame: object) -> object:
    if isinstance(frame, pd.DataFrame):
        return frame.iloc[:, 0]
    return frame


def safe_call(factory: Callable[[], object]) -> object | None:
    try:
        return factory()
    except Exception:
        return None


def clean_column_name(name: str) -> str:
    return name.lower().replace(".", "_").replace("-", "_").replace(" ", "_")


def discover_callable_indicator_names() -> list[str]:
    names = []
    for name in dir(ta):
        if name.startswith("_"):
            continue
        obj = getattr(ta, name)
        if callable(obj) and name.islower() and not inspect.isclass(obj):
            names.append(name)
    return sorted(names)


def score_features_for_strategy(feature_frame: pd.DataFrame, labels: pd.Series, strategy: str, top_n: int = 30, min_valid: int = 10) -> pd.DataFrame:
    rows = []
    y = labels.astype(bool)
    for feature in [col for col in feature_frame.columns if col != "time"]:
        values = pd.to_numeric(feature_frame[feature], errors="coerce").replace([np.inf, -np.inf], np.nan)
        valid = values.notna() & y.notna()
        if valid.sum() < min_valid or y[valid].nunique() < 2 or values[valid].nunique() <= 1:
            continue
        try:
            auc = roc_auc_score(y[valid], values[valid])
        except ValueError:
            continue
        directional_auc = max(float(auc), float(1 - auc))
        pos = values[valid & y].median()
        neg = values[valid & ~y].median()
        rows.append(
            {
                "strategy": strategy,
                "feature": feature,
                "auc": float(auc),
                "auc_lift": directional_auc - 0.5,
                "direction": "high" if auc >= 0.5 else "low",
                "positive_median": float(pos),
                "background_median": float(neg),
                "positive_count": int((valid & y).sum()),
                "background_count": int((valid & ~y).sum()),
            }
        )
    if not rows:
        return pd.DataFrame(columns=["strategy", "feature", "auc", "auc_lift", "direction", "positive_median", "background_median", "positive_count", "background_count"])
    return pd.DataFrame(rows).sort_values(["auc_lift", "feature"], ascending=[False, True]).head(top_n).reset_index(drop=True)
