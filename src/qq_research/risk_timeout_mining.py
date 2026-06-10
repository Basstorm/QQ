from __future__ import annotations

import pandas as pd


def build_strategy_risk_frame(lifecycle: pd.DataFrame) -> pd.DataFrame:
    rows = []
    ordered = lifecycle.sort_values(["basket_id", "time"])
    for basket_id, group in ordered.groupby("basket_id", sort=True):
        exit_rows = group[group["is_final_exit_minute"]]
        if exit_rows.empty:
            continue
        exit_row = exit_rows.sort_values("time").iloc[-1]
        moves = group["close_move_from_open_vwap_points"]
        rows.append(
            {
                "basket_id": basket_id,
                "strategy": exit_row["strategy"],
                "direction": exit_row["direction"],
                "entry_time": pd.Timestamp(group["time"].min()),
                "exit_time": pd.Timestamp(exit_row["time"]),
                "holding_min": float(exit_row["minutes_since_initial_entry"]),
                "max_layers": int(group["open_layer_count"].max()),
                "exit_move": float(exit_row["close_move_from_open_vwap_points"]),
                "min_close_move": float(moves.min()),
                "max_close_move": float(moves.max()),
                "max_adverse_points": float(max(0.0, -moves.min())),
                "max_favorable_points": float(max(0.0, moves.max())),
            }
        )
    return pd.DataFrame(rows)


def mine_timeout_candidates(risk: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for strategy, group in risk.groupby("strategy", sort=True):
        rows.append(
            {
                "strategy": strategy,
                "basket_count": int(len(group)),
                "negative_exit_count": int(group["exit_move"].lt(0).sum()),
                "hold_median": float(group["holding_min"].median()),
                "hold_q75": float(group["holding_min"].quantile(0.75)),
                "hold_q90": float(group["holding_min"].quantile(0.90)),
                "hold_q95": float(group["holding_min"].quantile(0.95)),
                "adverse_median": float(group["max_adverse_points"].median()),
                "adverse_q75": float(group["max_adverse_points"].quantile(0.75)),
                "adverse_q90": float(group["max_adverse_points"].quantile(0.90)),
                "exit_move_q10": float(group["exit_move"].quantile(0.10)),
                "exit_move_median": float(group["exit_move"].median()),
                "max_layers_median": float(group["max_layers"].median()),
                "max_layers_max": int(group["max_layers"].max()),
            }
        )
    return pd.DataFrame(rows)


def build_risk_timeout_report(candidates: pd.DataFrame) -> str:
    lines = [
        "# Phase 6 Risk / Timeout Exit Mining",
        "",
        "## Scope",
        "",
        "- Lightweight diagnostic focused on observed QQ baskets, not a new optimized stop-loss model.",
        "- Primary targets are `T3/S06` and `T6/S12`, because Phase 5 backtests exposed tail risk there.",
        "- Candidate timeout levels are descriptive quantiles of real QQ basket holding time and adverse excursion.",
        "",
        "| Strategy | Baskets | Negative exits | Hold median | Hold q75 | Hold q90 | Hold q95 | Adverse median | Adverse q90 | Exit q10 | Exit median | Max layers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in candidates.sort_values("strategy").itertuples(index=False):
        lines.append(
            f"| `{row.strategy}` | {int(row.basket_count)} | {int(row.negative_exit_count)} | {row.hold_median:.1f} | {row.hold_q75:.1f} | {row.hold_q90:.1f} | {row.hold_q95:.1f} | {row.adverse_median:.2f} | {row.adverse_q90:.2f} | {row.exit_move_q10:.2f} | {row.exit_move_median:.2f} | {int(row.max_layers_max)} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- A practical first timeout cap should be conservative: near observed `hold_q95`, not fitted to maximize this sample.",
            "- A separate adverse-excursion kill switch is not supported yet unless adverse tails are far beyond normal observed QQ baskets.",
            "- Use these values only as candidate risk-control bounds for the next backtest pass.",
        ]
    )
    return "\n".join(lines) + "\n"
