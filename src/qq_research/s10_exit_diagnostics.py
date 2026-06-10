from __future__ import annotations

import pandas as pd


def build_s10_path_diagnostics(lifecycle: pd.DataFrame) -> pd.DataFrame:
    rows = []
    s10 = lifecycle[lifecycle["strategy"].eq("T5/S10")].sort_values(["basket_id", "time"])
    for basket_id, group in s10.groupby("basket_id", sort=True):
        exit_rows = group[group["is_final_exit_minute"]]
        if exit_rows.empty:
            continue
        exit_row = exit_rows.iloc[-1]
        close_moves = group["close_move_from_open_vwap_points"]
        max_idx = close_moves.idxmax()
        entry_time = pd.Timestamp(group["time"].min())
        max_time = pd.Timestamp(group.loc[max_idx, "time"])
        exit_time = pd.Timestamp(exit_row["time"])
        exit_move = float(exit_row["close_move_from_open_vwap_points"])
        max_close_move = float(close_moves.max())
        rows.append(
            {
                "basket_id": basket_id,
                "entry_time": entry_time,
                "layers_exit": int(exit_row["open_layer_count"]),
                "holding_min": float(group["minutes_since_initial_entry"].max()),
                "exit_move": exit_move,
                "max_close_move": max_close_move,
                "max_touch_move": float(group["touch_move_from_open_vwap_points"].max()),
                "min_close_move": float(close_moves.min()),
                "retrace_from_max_to_exit": max_close_move - exit_move,
                "time_of_max": max_time,
                "exit_time": exit_time,
                "minutes_max_to_exit": (exit_time - max_time).total_seconds() / 60,
            }
        )
    return pd.DataFrame(rows)


def summarize_s10_path_diagnostics(diagnostics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for layers_exit, group in diagnostics.groupby("layers_exit", sort=True):
        rows.append(
            {
                "layers_exit": int(layers_exit),
                "basket_count": int(len(group)),
                "exit_move_median": float(group["exit_move"].median()),
                "exit_move_q25": float(group["exit_move"].quantile(0.25)),
                "exit_move_q75": float(group["exit_move"].quantile(0.75)),
                "max_close_move_median": float(group["max_close_move"].median()),
                "retrace_median": float(group["retrace_from_max_to_exit"].median()),
                "holding_median": float(group["holding_min"].median()),
                "max_to_exit_median": float(group["minutes_max_to_exit"].median()),
                "max_to_exit_within_1m_pct": float(group["minutes_max_to_exit"].le(1).mean() * 100),
            }
        )
    return pd.DataFrame(rows)


def build_s10_exit_report(diagnostics: pd.DataFrame, summary: pd.DataFrame) -> str:
    overall_cols = [
        col
        for col in ["holding_min", "exit_move", "max_close_move", "max_touch_move", "retrace_from_max_to_exit", "minutes_max_to_exit"]
        if col in diagnostics
    ]
    overall = diagnostics[overall_cols].describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9])
    lines = [
        "# T5/S10 Exit Path Diagnostics",
        "",
        "## Overall Distribution",
        "",
        "```text",
        overall.to_string(float_format=lambda value: f"{value:.2f}"),
        "```",
        "",
        "## By Exit Layer Count",
        "",
        "| Exit layers | Baskets | Exit median | Exit q25 | Exit q75 | Max median | Retrace median | Holding median | Max-to-exit median | Max-to-exit <=1m % |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary.sort_values("layers_exit").itertuples(index=False):
        lines.append(
            f"| {int(row.layers_exit)} | {int(row.basket_count)} | {row.exit_move_median:.2f} | {row.exit_move_q25:.2f} | {row.exit_move_q75:.2f} | {row.max_close_move_median:.2f} | {row.retrace_median:.2f} | {row.holding_median:.1f} | {row.max_to_exit_median:.1f} | {row.max_to_exit_within_1m_pct:.1f} |"
        )
    holding = diagnostics.copy()
    holding["holding_bucket"] = pd.cut(holding["holding_min"], [-1, 30, 120, 360, 1440, 10000])
    bucket_summary = holding.groupby("holding_bucket", observed=True).agg(
        basket_count=("holding_min", "count"),
        exit_move_median=("exit_move", "median"),
        max_close_move_median=("max_close_move", "median"),
        retrace_median=("retrace_from_max_to_exit", "median"),
        max_to_exit_median=("minutes_max_to_exit", "median"),
        loss_pct=("exit_move", lambda values: values.le(0).mean() * 100),
    )
    lines.extend(
        [
            "",
            "## Holding Duration Buckets",
            "",
            "| Holding bucket | Baskets | Exit median | Max median | Retrace median | Max-to-exit median | Loss exit % |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for bucket, row in bucket_summary.iterrows():
        lines.append(
            f"| `{bucket}` | {int(row.basket_count)} | {row.exit_move_median:.2f} | {row.max_close_move_median:.2f} | {row.retrace_median:.2f} | {row.max_to_exit_median:.1f} | {row.loss_pct:.1f} |"
        )
    if "exit_time" in diagnostics:
        entry_hour_counts = pd.to_datetime(diagnostics["entry_time"]).dt.hour.value_counts().sort_index()
        lines.extend(["", "## Entry Hour Counts", "", "| Broker entry hour | Baskets |", "|---:|---:|"])
        for hour, count in entry_hour_counts.items():
            lines.append(f"| {int(hour)} | {int(count)} |")
        hour_counts = pd.to_datetime(diagnostics["exit_time"]).dt.hour.value_counts().sort_index()
        lines.extend(["", "## Exit Hour Counts", "", "| Broker exit hour | Baskets |", "|---:|---:|"])
        for hour, count in hour_counts.items():
            lines.append(f"| {int(hour)} | {int(count)} |")
        session_data = diagnostics.copy()
        session_data["exit_hour"] = pd.to_datetime(session_data["exit_time"]).dt.hour
        session_data["exit_session"] = pd.cut(
            session_data["exit_hour"],
            [-1, 0, 4, 8, 12, 16, 20, 23],
            labels=["00", "01-04", "05-08", "09-12", "13-16", "17-20", "21-23"],
        )
        session_summary = session_data.groupby("exit_session", observed=True).agg(
            basket_count=("holding_min", "count"),
            exit_move_median=("exit_move", "median"),
            exit_move_q25=("exit_move", lambda values: values.quantile(0.25)),
            exit_move_q75=("exit_move", lambda values: values.quantile(0.75)),
            holding_median=("holding_min", "median"),
            loss_pct=("exit_move", lambda values: values.le(0).mean() * 100),
            layers_median=("layers_exit", "median"),
        )
        lines.extend(
            [
                "",
                "## Exit Session Buckets",
                "",
                "| Exit session | Baskets | Exit median | Exit q25 | Exit q75 | Holding median | Loss exit % | Layers median |",
                "|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for session, row in session_summary.iterrows():
            lines.append(
                f"| `{session}` | {int(row.basket_count)} | {row.exit_move_median:.2f} | {row.exit_move_q25:.2f} | {row.exit_move_q75:.2f} | {row.holding_median:.1f} | {row.loss_pct:.1f} | {row.layers_median:.1f} |"
            )
    return "\n".join(lines) + "\n"
