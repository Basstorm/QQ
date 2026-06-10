from __future__ import annotations

import numpy as np
import pandas as pd

from qq_research.robust_vectorbt_backtest import build_edge_signals, evaluate_rule_mask


def _normalize_times(series: pd.Series) -> pd.Series:
    values = pd.to_datetime(series)
    if getattr(values.dt, "tz", None) is not None:
        values = values.dt.tz_convert(None)
    return values


def build_rule_entry_seeds(
    features: pd.DataFrame,
    synthesis: pd.DataFrame,
    m1: pd.DataFrame,
    rule_column: str,
    variant: str,
    direction_map: dict[str, str],
    excluded_strategies: set[str] | None = None,
    initial_volume: float = 1.0,
) -> pd.DataFrame:
    excluded_strategies = excluded_strategies or set()
    feature_frame = features.copy()
    feature_frame["time"] = _normalize_times(feature_frame["time"])
    prices = m1.copy()
    prices["time"] = _normalize_times(prices["time"])
    close = prices.drop_duplicates("time").set_index("time")["close"].sort_index()
    rows = []
    next_id = 1
    for strategy_row in synthesis.sort_values("strategy").itertuples(index=False):
        strategy = strategy_row.strategy
        if strategy in excluded_strategies:
            continue
        rule = getattr(strategy_row, rule_column)
        if not isinstance(rule, str) or rule == "n/a":
            continue
        mask = evaluate_rule_mask(feature_frame, rule)
        entries, _ = build_edge_signals(mask)
        for entry_time in feature_frame.loc[entries, "time"]:
            timestamp = pd.Timestamp(entry_time)
            if timestamp not in close.index:
                continue
            rows.append(
                {
                    "basket_id": next_id,
                    "strategy": strategy,
                    "variant": variant,
                    "direction": direction_map[strategy],
                    "entry_time": timestamp,
                    "entry_price": float(close.loc[timestamp]),
                    "volume": float(initial_volume),
                }
            )
            next_id += 1
    return pd.DataFrame(rows)


def filter_non_overlapping_replays(replay: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, group in replay.sort_values(["variant", "strategy", "entry_time"]).groupby(["variant", "strategy"], sort=True):
        open_until = pd.Timestamp.min
        for row in group.itertuples(index=False):
            entry_time = pd.Timestamp(row.entry_time)
            if entry_time < open_until:
                continue
            rows.append(row._asdict())
            open_until = pd.Timestamp(row.sim_exit_time)
    return pd.DataFrame(rows)


def summarize_rule_backtest(replay: pd.DataFrame, pnl_scale: float = 100.0) -> pd.DataFrame:
    rows = []
    for (variant, strategy), group in replay.groupby(["variant", "strategy"], sort=True):
        ordered = group.sort_values("sim_exit_time")
        pnl = ordered["sim_pnl_est"].astype(float) / pnl_scale
        equity = pnl.cumsum()
        drawdown = equity - equity.cummax()
        rows.append(
            {
                "variant": variant,
                "strategy": strategy,
                "trade_count": int(len(group)),
                "closed_rate_pct": float(group["sim_closed"].mean() * 100),
                "unclosed_count": int((~group["sim_closed"]).sum()),
                "win_rate_pct": float(pnl.gt(0).mean() * 100),
                "total_points": float(pnl.sum()),
                "avg_points": float(pnl.mean()) if len(pnl) else np.nan,
                "median_points": float(pnl.median()) if len(pnl) else np.nan,
                "worst_trade_points": float(pnl.min()) if len(pnl) else np.nan,
                "max_drawdown_points": float(drawdown.min()) if len(drawdown) else np.nan,
                "avg_layers": float(group["sim_layer_count"].mean()) if len(group) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_rule_backtest_report(summary: pd.DataFrame) -> str:
    lines = [
        "# Non-S10 Rule Entry Basket Backtest",
        "",
        "## Scope",
        "",
        "- Uses inferred M15 entry rules to seed baskets.",
        "- Excludes `T5/S10`.",
        "- Uses normalized one-unit initial sizing; reported PnL is direction-aware points, not account currency.",
        "- Basket management uses inferred add-on thresholds and close-based VWAP TP on M1 close.",
        "",
        "| Variant | Strategy | Trades | Unclosed | Closed % | Win % | Total points | Avg points | Median points | Worst trade | Max DD | Avg layers |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary.sort_values(["variant", "strategy"]).itertuples(index=False):
        lines.append(
            f"| `{row.variant}` | `{row.strategy}` | {int(row.trade_count)} | {int(row.unclosed_count)} | {row.closed_rate_pct:.1f} | {row.win_rate_pct:.1f} | {row.total_points:.2f} | {row.avg_points:.3f} | {row.median_points:.3f} | {row.worst_trade_points:.2f} | {row.max_drawdown_points:.2f} | {row.avg_layers:.2f} |"
        )
    return "\n".join(lines) + "\n"
