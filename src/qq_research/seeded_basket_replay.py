from __future__ import annotations

import numpy as np
import pandas as pd


def _normalize_time(series: pd.Series) -> pd.Series:
    values = pd.to_datetime(series)
    if getattr(values.dt, "tz", None) is not None:
        values = values.dt.tz_convert(None)
    return values


def _directional_move(direction: str, entry_price: float, exit_price: float) -> float:
    return entry_price - exit_price if direction == "short" else exit_price - entry_price


def _compile_rule_map(rules: pd.DataFrame, layer_col: str, value_col: str) -> dict[str, list[tuple[int, float]]]:
    result = {}
    for strategy, group in rules.groupby("strategy", sort=True):
        ordered = group.sort_values(layer_col)
        result[strategy] = [(int(row[layer_col]), float(row[value_col])) for _, row in ordered.iterrows()]
    return result


def _lookup_compiled_rule(rule_map: dict[str, list[tuple[int, float]]], strategy: str, layer_count: int) -> float | None:
    strategy_rules = rule_map.get(strategy, [])
    if not strategy_rules:
        return None
    exact = [value for layer, value in strategy_rules if layer == layer_count]
    if exact:
        return exact[-1]
    prior = [value for layer, value in strategy_rules if layer <= layer_count]
    return prior[-1] if prior else strategy_rules[0][1]


def replay_seeded_baskets(
    seeds: pd.DataFrame,
    m1: pd.DataFrame,
    add_on_rules: pd.DataFrame,
    exit_rules: pd.DataFrame,
    volume_schedule: dict[tuple[str, int], float] | None = None,
    max_layers_by_strategy: dict[str, int] | None = None,
    max_minutes: int = 10_080,
    exit_threshold_col: str = "move_q25",
) -> pd.DataFrame:
    prices = m1.copy()
    prices["time"] = _normalize_time(prices["time"])
    prices = prices.drop_duplicates("time").set_index("time").sort_index()
    price_times = prices.index.to_numpy()
    close_values = prices["close"].astype(float).to_numpy()
    add_thresholds = _compile_rule_map(add_on_rules, "pre_open_layer_count", "adverse_threshold")
    add_min_minutes = _compile_rule_map(add_on_rules, "pre_open_layer_count", "min_minutes")
    exit_thresholds = _compile_rule_map(exit_rules, "open_layer_count", exit_threshold_col)
    volume_schedule = volume_schedule or {}
    max_layers_by_strategy = max_layers_by_strategy or {}
    rows = []
    for seed in seeds.sort_values("entry_time").itertuples(index=False):
        strategy = seed.strategy
        direction = seed.direction
        entry_time = pd.Timestamp(seed.entry_time).floor("min")
        actual_exit_time = pd.Timestamp(seed.exit_time).floor("min") if hasattr(seed, "exit_time") else pd.NaT
        end_time = min(pd.Timestamp(prices.index.max()), entry_time + pd.Timedelta(minutes=max_minutes))
        start_idx = int(np.searchsorted(price_times, np.datetime64(entry_time), side="left"))
        end_idx = int(np.searchsorted(price_times, np.datetime64(end_time), side="right"))
        layers = [{"entry_price": float(seed.entry_price), "volume": float(seed.volume), "entry_time": entry_time}]
        sim_exit_time = pd.NaT
        sim_exit_price = np.nan
        sim_closed = False
        if start_idx >= end_idx:
            rows.append(_build_result_row(seed, layers, actual_exit_time, sim_exit_time, sim_exit_price, sim_closed))
            continue
        last_time = pd.Timestamp(price_times[end_idx - 1])
        last_close = float(close_values[end_idx - 1])
        for idx in range(start_idx, end_idx):
            current_time = pd.Timestamp(price_times[idx])
            close = float(close_values[idx])
            total_volume = sum(layer["volume"] for layer in layers)
            vwap = sum(layer["entry_price"] * layer["volume"] for layer in layers) / total_volume
            layer_count = len(layers)
            exit_threshold = _lookup_compiled_rule(exit_thresholds, strategy, layer_count)
            if exit_threshold is not None and _directional_move(direction, vwap, close) >= exit_threshold:
                sim_exit_time = pd.Timestamp(current_time)
                sim_exit_price = close
                sim_closed = True
                break
            add_threshold = _lookup_compiled_rule(add_thresholds, strategy, layer_count)
            min_minutes = _lookup_compiled_rule(add_min_minutes, strategy, layer_count)
            if add_threshold is None or min_minutes is None:
                continue
            if layer_count >= max_layers_by_strategy.get(strategy, max(layer_count, 1_000_000)):
                continue
            last_layer = layers[-1]
            adverse_from_last = -_directional_move(direction, last_layer["entry_price"], close)
            minutes_since_last = (pd.Timestamp(current_time) - last_layer["entry_time"]).total_seconds() / 60
            if adverse_from_last >= add_threshold and minutes_since_last >= min_minutes:
                next_layer = len(layers) + 1
                layers.append(
                    {
                        "entry_price": close,
                        "volume": float(volume_schedule.get((strategy, next_layer), last_layer["volume"])),
                        "entry_time": pd.Timestamp(current_time),
                    }
                )
        if not sim_closed:
            sim_exit_time = last_time
            sim_exit_price = last_close
        rows.append(_build_result_row(seed, layers, actual_exit_time, sim_exit_time, sim_exit_price, sim_closed))
    return pd.DataFrame(rows)


def _build_result_row(seed, layers: list[dict[str, float | pd.Timestamp]], actual_exit_time: pd.Timestamp, sim_exit_time: pd.Timestamp, sim_exit_price: float, sim_closed: bool) -> dict[str, object]:
    direction = seed.direction
    total_volume = sum(float(layer["volume"]) for layer in layers)
    vwap = sum(float(layer["entry_price"]) * float(layer["volume"]) for layer in layers) / total_volume if total_volume else np.nan
    sim_exit_move = _directional_move(direction, vwap, sim_exit_price) if pd.notna(sim_exit_price) else np.nan
    sim_pnl = sum(_directional_move(direction, float(layer["entry_price"]), sim_exit_price) * float(layer["volume"]) * 100 for layer in layers) if pd.notna(sim_exit_price) else np.nan
    return {
        "basket_id": seed.basket_id,
        "strategy": seed.strategy,
        "direction": direction,
        "entry_time": pd.Timestamp(seed.entry_time),
        "actual_exit_time": actual_exit_time,
        "sim_exit_time": sim_exit_time,
        "sim_closed": bool(sim_closed),
        "sim_layer_count": int(len(layers)),
        "actual_layer_count": int(seed.actual_layer_count) if hasattr(seed, "actual_layer_count") and pd.notna(seed.actual_layer_count) else np.nan,
        "sim_entry_vwap": vwap,
        "sim_exit_price": sim_exit_price,
        "sim_exit_move_points": sim_exit_move,
        "sim_pnl_est": sim_pnl,
        "actual_pnl_est": float(seed.actual_pnl_est) if hasattr(seed, "actual_pnl_est") and pd.notna(seed.actual_pnl_est) else np.nan,
    }


def summarize_replay(replay: pd.DataFrame, excluded_strategies: set[str] | None = None) -> pd.DataFrame:
    frame = replay.copy()
    if excluded_strategies:
        frame = frame[~frame["strategy"].isin(excluded_strategies)]
    rows = []
    for strategy, group in frame.groupby("strategy", sort=True):
        lag = (pd.to_datetime(group["sim_exit_time"]) - pd.to_datetime(group["actual_exit_time"])).dt.total_seconds().abs() / 60
        signed_lag = (pd.to_datetime(group["sim_exit_time"]) - pd.to_datetime(group["actual_exit_time"])).dt.total_seconds() / 60
        layer_diff = group["sim_layer_count"] - group["actual_layer_count"]
        rows.append(
            {
                "strategy": strategy,
                "basket_count": int(len(group)),
                "closed_rate_pct": float(group["sim_closed"].mean() * 100),
                "exit_within_1m_pct": float(lag.le(1).mean() * 100),
                "exit_within_5m_pct": float(lag.le(5).mean() * 100),
                "exit_within_30m_pct": float(lag.le(30).mean() * 100),
                "exit_lag_median": float(lag.median()),
                "exit_lag_q75": float(lag.quantile(0.75)),
                "sim_early_exit_pct": float(signed_lag.lt(0).mean() * 100),
                "sim_late_exit_pct": float(signed_lag.gt(0).mean() * 100),
                "layer_exact_match_pct": float(layer_diff.eq(0).mean() * 100),
                "sim_win_rate_pct": float(group["sim_pnl_est"].gt(0).mean() * 100),
                "actual_win_rate_pct": float(group["actual_pnl_est"].gt(0).mean() * 100) if group["actual_pnl_est"].notna().any() else np.nan,
                "sim_total_pnl": float(group["sim_pnl_est"].sum()),
                "actual_total_pnl": float(group["actual_pnl_est"].sum()) if group["actual_pnl_est"].notna().any() else np.nan,
                "median_layer_diff": float(layer_diff.median()) if layer_diff.notna().any() else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_replay_report(summary: pd.DataFrame) -> str:
    has_variant = "variant" in summary.columns
    lines = [
        "# Seeded Non-S10 Basket Engine Replay",
        "",
        "## Scope",
        "",
        "- Uses real QQ initial basket entries as seeds.",
        "- Excludes `T5/S10`.",
        "- Replays inferred add-on and close-based VWAP TP rules on M1 close data.",
        "- PnL uses an approximate point-value and median observed add-on volumes; timing and layer-match metrics are the primary validation signals.",
        "",
        (
            "| Variant | Strategy | Baskets | Closed % | Exit <=1m % | Exit <=5m % | Exit <=30m % | Lag median | Early % | Late % | Layer exact % | Sim win % | Actual win % | Median layer diff |"
            if has_variant
            else "| Strategy | Baskets | Closed % | Exit <=1m % | Exit <=5m % | Exit <=30m % | Lag median | Early % | Late % | Layer exact % | Sim win % | Actual win % | Median layer diff |"
        ),
        (
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
            if has_variant
            else "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
        ),
    ]
    sort_cols = ["variant", "strategy"] if has_variant else ["strategy"]
    for row in summary.sort_values(sort_cols).itertuples(index=False):
        base = f"`{row.strategy}` | {int(row.basket_count)} | {row.closed_rate_pct:.1f} | {row.exit_within_1m_pct:.1f} | {row.exit_within_5m_pct:.1f} | {row.exit_within_30m_pct:.1f} | {row.exit_lag_median:.1f} | {row.sim_early_exit_pct:.1f} | {row.sim_late_exit_pct:.1f} | {row.layer_exact_match_pct:.1f} | {row.sim_win_rate_pct:.1f} | {row.actual_win_rate_pct:.1f} | {row.median_layer_diff:.1f} |"
        lines.append(f"| `{row.variant}` | {base}" if has_variant else f"| {base}")
    return "\n".join(lines) + "\n"
