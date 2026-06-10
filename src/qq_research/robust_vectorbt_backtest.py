from __future__ import annotations

from os import PathLike

import numpy as np
import pandas as pd

from qq_research.temporal_validation import parse_rule


def evaluate_rule_mask(feature_frame: pd.DataFrame, rule: str) -> pd.Series:
    mask = pd.Series(True, index=feature_frame.index)
    for condition in parse_rule(rule):
        values = pd.to_numeric(feature_frame[condition["feature"]], errors="coerce").replace([np.inf, -np.inf], np.nan)
        if condition["operator"] == ">=":
            mask &= values >= float(condition["threshold"])
        else:
            mask &= values <= float(condition["threshold"])
    return mask.fillna(False).astype(bool)


def build_edge_signals(mask: pd.Series) -> tuple[pd.Series, pd.Series]:
    active = mask.fillna(False).astype(bool)
    previous = active.shift(1, fill_value=False)
    entries = active & ~previous
    exits = ~active & previous
    if len(exits) and active.iloc[-1]:
        exits.iloc[-1] = True
    return entries, exits


def select_robust_rule_variants(synthesis: pd.DataFrame) -> pd.DataFrame:
    rows = []
    robust = synthesis[synthesis["overall_confidence"].eq("robust")]
    for row in robust.itertuples(index=False):
        for variant, rule_column, confidence_column in [
            ("all_background", "best_all_background_rule", "all_background_confidence"),
            ("matched_context", "best_matched_rule", "matched_confidence"),
        ]:
            rule = getattr(row, rule_column)
            if isinstance(rule, str) and rule != "n/a":
                rows.append(
                    {
                        "strategy": row.strategy,
                        "variant": variant,
                        "rule": rule,
                        "validation_confidence": getattr(row, confidence_column),
                    }
                )
    return pd.DataFrame(rows)


def load_m15_close(csv_path: str | bytes | PathLike[str]) -> pd.Series:
    m15 = pd.read_csv(csv_path, usecols=["time", "close"])
    times = pd.to_datetime(m15["time"])
    if getattr(times.dt, "tz", None) is not None:
        times = times.dt.tz_convert(None)
    close = pd.Series(pd.to_numeric(m15["close"], errors="coerce").to_numpy(), index=times, name="close")
    return close[~close.index.duplicated(keep="last")].sort_index()


def align_close_to_features(close: pd.Series, feature_frame: pd.DataFrame) -> pd.Series:
    times = pd.to_datetime(feature_frame["time"])
    return close.reindex(times)


def run_vectorbt_backtest(close: pd.Series, entries: pd.Series, exits: pd.Series, init_cash: float = 10_000.0):
    import vectorbt as vbt

    return vbt.Portfolio.from_signals(
        close,
        entries=entries,
        exits=exits,
        init_cash=init_cash,
        size=1.0,
        direction="longonly",
        freq="15min",
    )


def summarize_portfolio(strategy: str, variant: str, rule: str, mask: pd.Series, entries: pd.Series, exits: pd.Series, portfolio) -> dict[str, object]:
    trades = portfolio.trades
    return {
        "strategy": strategy,
        "variant": variant,
        "rule": rule,
        "signal_bars": int(mask.sum()),
        "entry_count": int(entries.sum()),
        "exit_count": int(exits.sum()),
        "total_return_pct": float(portfolio.total_return() * 100),
        "max_drawdown_pct": float(portfolio.max_drawdown() * 100),
        "sharpe_ratio": float(portfolio.sharpe_ratio()),
        "trade_count": int(trades.count()),
        "win_rate_pct": float(trades.win_rate() * 100) if trades.count() else 0.0,
        "total_profit": float(trades.pnl.sum()) if trades.count() else 0.0,
    }


def build_backtest_report(results: pd.DataFrame) -> str:
    lines = [
        "# Vectorbt Backtest of Robust Approximate Rules",
        "",
        "## Scope",
        "",
        "- Uses only M15 close data and the robust approximate entry-rule variants from `strategy_rule_synthesis.csv`.",
        "- Long-only, one-unit position sizing, no grid/add-on management, no inferred EA take-profit/stop-loss logic, no fees/slippage.",
        "- Entry is the rule mask changing from false to true; exit is the rule mask changing from true to false.",
        "- This tests whether the inferred context filters have standalone directional edge, not whether they reproduce Quantum Queen's managed basket PnL.",
        "",
        "## Results",
        "",
        "| Strategy | Variant | Return % | Max DD % | Sharpe | Trades | Win rate % | Signal bars |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in results.sort_values(["strategy", "variant"]).itertuples(index=False):
        lines.append(
            f"| `{row.strategy}` | `{row.variant}` | {row.total_return_pct:.2f} | {row.max_drawdown_pct:.2f} | {row.sharpe_ratio:.2f} | {int(row.trade_count)} | {row.win_rate_pct:.2f} | {int(row.signal_bars)} |"
        )
    lines.extend(["", "## Rules", ""])
    for row in results.sort_values(["strategy", "variant"]).itertuples(index=False):
        lines.append(f"- `{row.strategy}` / `{row.variant}`: `{row.rule}`")
    return "\n".join(lines) + "\n"
