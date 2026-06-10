from __future__ import annotations

import pandas as pd


def build_exit_trigger_frame(lifecycle: pd.DataFrame) -> pd.DataFrame:
    frame = lifecycle[lifecycle["open_layer_count"].gt(0)].copy()
    frame["is_positive"] = frame["is_final_exit_minute"].astype(bool)
    return frame


def evaluate_exit_threshold(frame: pd.DataFrame, feature: str, threshold: float) -> dict[str, float | int]:
    valid = frame[feature].notna() & frame["is_positive"].notna()
    data = frame.loc[valid]
    matched = data[feature] >= threshold
    positives = data["is_positive"].astype(bool)
    true_positive = int((matched & positives).sum())
    matched_count = int(matched.sum())
    total_positive = int(positives.sum())
    precision = true_positive / matched_count if matched_count else 0.0
    recall = true_positive / total_positive if total_positive else 0.0
    base_rate = total_positive / len(data) if len(data) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "threshold": float(threshold),
        "matched": matched_count,
        "true_positive": true_positive,
        "false_positive": int((matched & ~positives).sum()),
        "total_positive": total_positive,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "base_rate": base_rate,
        "precision_lift_vs_base": precision / base_rate if base_rate else 0.0,
    }


def mine_exit_thresholds(frame: pd.DataFrame, min_positives: int = 10) -> pd.DataFrame:
    rows = []
    for (strategy, layer_count), group in frame.groupby(["strategy", "open_layer_count"], sort=True):
        positives = group[group["is_positive"]]
        if len(positives) < min_positives:
            continue
        moves = positives["close_move_from_open_vwap_points"]
        thresholds = sorted(set(float(moves.quantile(q)) for q in [0.10, 0.25, 0.50, 0.75]))
        candidates = [evaluate_exit_threshold(group, "close_move_from_open_vwap_points", threshold) for threshold in thresholds]
        best = sorted(candidates, key=lambda row: (row["f1"], row["precision"], row["recall"], -row["matched"]), reverse=True)[0]
        q25_metrics = evaluate_exit_threshold(group, "close_move_from_open_vwap_points", float(moves.quantile(0.25)))
        rows.append(
            {
                "strategy": strategy,
                "open_layer_count": int(layer_count),
                "candidate_count": int(len(group)),
                "positive_count": int(len(positives)),
                "move_q10": float(moves.quantile(0.10)),
                "move_q25": float(moves.quantile(0.25)),
                "move_median": float(moves.quantile(0.50)),
                "move_q75": float(moves.quantile(0.75)),
                "q25_precision": q25_metrics["precision"],
                "q25_recall": q25_metrics["recall"],
                "q25_f1": q25_metrics["f1"],
                **best,
            }
        )
    return pd.DataFrame(rows)


def build_exit_threshold_report(thresholds: pd.DataFrame) -> str:
    lines = [
        "# Exit Trigger Threshold Mining",
        "",
        "## Scope",
        "",
        "- Uses active basket-minute rows from `basket_minute_lifecycle.parquet`.",
        "- Positives are final exit minutes.",
        "- Main rule form is `close_move_from_open_vwap_points >= TP(strategy, open_layer_count)`.",
        "- Threshold candidates are positive q10/q25/median/q75 exit moves per strategy/layer count.",
        "",
        "| Strategy | Open layers | Positives | Move q25 | Move median | Best TP | Precision | Recall | F1 | Lift |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in thresholds.sort_values(["strategy", "open_layer_count"]).itertuples(index=False):
        lines.append(
            f"| `{row.strategy}` | {int(row.open_layer_count)} | {int(row.positive_count)} | {row.move_q25:.2f} | {row.move_median:.2f} | {row.threshold:.2f} | {row.precision:.4f} | {row.recall:.3f} | {row.f1:.3f} | {row.precision_lift_vs_base:.1f}x |"
        )
    return "\n".join(lines) + "\n"
