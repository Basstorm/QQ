from __future__ import annotations

import pandas as pd


def build_add_on_trigger_frame(lifecycle: pd.DataFrame) -> pd.DataFrame:
    frame = lifecycle[lifecycle["pre_open_layer_count"].gt(0)].copy()
    frame["is_positive"] = frame["is_add_on_minute"].astype(bool)
    return frame


def evaluate_threshold(frame: pd.DataFrame, feature: str, threshold: float) -> dict[str, float | int]:
    valid = frame[feature].notna() & frame["is_positive"].notna()
    data = frame.loc[valid]
    matched = data[feature] >= threshold
    positives = data["is_positive"].astype(bool)
    true_positive = int((matched & positives).sum())
    matched_count = int(matched.sum())
    total_positive = int(positives.sum())
    base_rate = total_positive / len(data) if len(data) else 0.0
    precision = true_positive / matched_count if matched_count else 0.0
    return {
        "threshold": float(threshold),
        "matched": matched_count,
        "true_positive": true_positive,
        "false_positive": int((matched & ~positives).sum()),
        "total_positive": total_positive,
        "precision": precision,
        "recall": true_positive / total_positive if total_positive else 0.0,
        "base_rate": base_rate,
        "precision_lift_vs_base": precision / base_rate if base_rate else 0.0,
    }


def evaluate_two_feature_rule(frame: pd.DataFrame, adverse_threshold: float, min_minutes: float) -> dict[str, float | int]:
    valid = frame["adverse_from_pre_last_entry_points"].notna() & frame["minutes_since_pre_last_entry"].notna() & frame["is_positive"].notna()
    data = frame.loc[valid]
    matched = (data["adverse_from_pre_last_entry_points"] >= adverse_threshold) & (data["minutes_since_pre_last_entry"] >= min_minutes)
    positives = data["is_positive"].astype(bool)
    true_positive = int((matched & positives).sum())
    matched_count = int(matched.sum())
    total_positive = int(positives.sum())
    precision = true_positive / matched_count if matched_count else 0.0
    recall = true_positive / total_positive if total_positive else 0.0
    base_rate = total_positive / len(data) if len(data) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "adverse_threshold": float(adverse_threshold),
        "min_minutes": float(min_minutes),
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


def mine_add_on_thresholds(frame: pd.DataFrame, min_positives: int = 10) -> pd.DataFrame:
    rows = []
    for (strategy, layer), group in frame.groupby(["strategy", "pre_open_layer_count"], sort=True):
        positives = group[group["is_positive"]]
        if len(positives) < min_positives:
            continue
        adverse = positives["adverse_from_pre_last_entry_points"]
        minutes = positives["minutes_since_pre_last_entry"]
        threshold = float(adverse.quantile(0.25))
        metrics = evaluate_threshold(group, "adverse_from_pre_last_entry_points", threshold)
        rows.append(
            {
                "strategy": strategy,
                "pre_open_layer_count": int(layer),
                "candidate_count": int(len(group)),
                "positive_count": int(len(positives)),
                "adverse_q10": float(adverse.quantile(0.10)),
                "adverse_q25": float(adverse.quantile(0.25)),
                "adverse_median": float(adverse.quantile(0.50)),
                "adverse_q75": float(adverse.quantile(0.75)),
                "minutes_q25": float(minutes.quantile(0.25)),
                "minutes_median": float(minutes.quantile(0.50)),
                "minutes_q75": float(minutes.quantile(0.75)),
                **metrics,
            }
        )
    return pd.DataFrame(rows)


def mine_add_on_cooldown_rules(frame: pd.DataFrame, min_positives: int = 10) -> pd.DataFrame:
    rows = []
    for (strategy, layer), group in frame.groupby(["strategy", "pre_open_layer_count"], sort=True):
        positives = group[group["is_positive"]]
        if len(positives) < min_positives:
            continue
        adverse_thresholds = sorted(set(float(positives["adverse_from_pre_last_entry_points"].quantile(q)) for q in [0.10, 0.25, 0.50]))
        minute_thresholds = sorted(set([0.0, 1.0, 5.0, 15.0, *[float(positives["minutes_since_pre_last_entry"].quantile(q)) for q in [0.10, 0.25, 0.50]]]))
        candidates = []
        for adverse_threshold in adverse_thresholds:
            for min_minutes in minute_thresholds:
                metrics = evaluate_two_feature_rule(group, adverse_threshold, min_minutes)
                if metrics["true_positive"]:
                    candidates.append(metrics)
        if not candidates:
            continue
        best = sorted(candidates, key=lambda row: (row["f1"], row["precision"], row["recall"], -row["matched"]), reverse=True)[0]
        baseline = evaluate_two_feature_rule(group, float(positives["adverse_from_pre_last_entry_points"].quantile(0.25)), 0.0)
        rows.append(
            {
                "strategy": strategy,
                "pre_open_layer_count": int(layer),
                "candidate_count": int(len(group)),
                "positive_count": int(len(positives)),
                "positive_adverse_q25": float(positives["adverse_from_pre_last_entry_points"].quantile(0.25)),
                "positive_minutes_q25": float(positives["minutes_since_pre_last_entry"].quantile(0.25)),
                "positive_minutes_median": float(positives["minutes_since_pre_last_entry"].quantile(0.50)),
                "baseline_precision": baseline["precision"],
                "baseline_recall": baseline["recall"],
                "baseline_f1": baseline["f1"],
                **best,
            }
        )
    return pd.DataFrame(rows)


def build_add_on_threshold_report(thresholds: pd.DataFrame) -> str:
    lines = [
        "# Add-on Trigger Threshold Mining",
        "",
        "## Scope",
        "",
        "- Uses `basket_minute_lifecycle.parquet` and only rows with an existing basket state (`pre_open_layer_count > 0`).",
        "- Positives are delayed/grid add-on minutes with prior basket state.",
        "- Main feature is adverse move from the previous open layer before the add-on minute.",
        "- Threshold metrics evaluate `adverse_from_pre_last_entry_points >= adverse_q25` per strategy/layer.",
        "",
        "## Strategy/Layer Thresholds",
        "",
        "| Strategy | Prior layers | Positives | Adverse q25 | Adverse median | Minutes median | Precision | Recall | Lift |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in thresholds.sort_values(["strategy", "pre_open_layer_count"]).itertuples(index=False):
        lines.append(
            f"| `{row.strategy}` | {int(row.pre_open_layer_count)} | {int(row.positive_count)} | {row.adverse_q25:.2f} | {row.adverse_median:.2f} | {row.minutes_median:.1f} | {row.precision:.4f} | {row.recall:.3f} | {row.precision_lift_vs_base:.1f}x |"
        )
    return "\n".join(lines) + "\n"


def build_add_on_cooldown_report(rules: pd.DataFrame) -> str:
    lines = [
        "# Add-on Cooldown Rule Mining",
        "",
        "## Scope",
        "",
        "- Tests whether delayed/grid add-ons are better explained by adverse distance plus a minimum time since previous layer.",
        "- Candidate rules use `adverse_from_pre_last_entry_points >= adverse_threshold` and `minutes_since_pre_last_entry >= min_minutes`.",
        "- Rows are selected per strategy/layer by F1, then precision, then recall.",
        "",
        "| Strategy | Prior layers | Positives | Adverse threshold | Min minutes | Precision | Recall | F1 | Baseline F1 | Lift |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rules.sort_values(["strategy", "pre_open_layer_count"]).itertuples(index=False):
        lines.append(
            f"| `{row.strategy}` | {int(row.pre_open_layer_count)} | {int(row.positive_count)} | {row.adverse_threshold:.2f} | {row.min_minutes:.1f} | {row.precision:.4f} | {row.recall:.3f} | {row.f1:.3f} | {row.baseline_f1:.3f} | {row.precision_lift_vs_base:.1f}x |"
        )
    return "\n".join(lines) + "\n"
