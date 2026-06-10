from __future__ import annotations

import re

import pandas as pd

from qq_research.rule_mining import evaluate_and_rule, mine_candidate_rules


def temporal_split_masks(frame: pd.DataFrame, split_time: str | pd.Timestamp) -> tuple[pd.Series, pd.Series]:
    times = pd.to_datetime(frame["time"])
    split = pd.Timestamp(split_time)
    train = times < split
    return train, ~train


def parse_rule(rule: str) -> list[dict[str, object]]:
    conditions = []
    for part in rule.split(" AND "):
        match = re.fullmatch(r"(.+?)\s*(>=|<=)\s*(-?\d+(?:\.\d+)?)", part.strip())
        if not match:
            raise ValueError(f"Cannot parse rule condition: {part}")
        feature, operator, threshold = match.groups()
        conditions.append({"feature": feature, "operator": operator, "threshold": float(threshold)})
    return conditions


def matched_context_mask(times: pd.Series | pd.DatetimeIndex, labels: pd.Series) -> pd.Series:
    dt = pd.to_datetime(pd.Series(times, index=labels.index))
    y = labels.astype(bool)
    positive_contexts = set(zip(dt[y].dt.dayofweek, dt[y].dt.hour))
    if not positive_contexts:
        return pd.Series(False, index=labels.index)
    contexts = list(zip(dt.dt.dayofweek, dt.dt.hour))
    return pd.Series([context in positive_contexts for context in contexts], index=labels.index)


def evaluate_rule_on_period(feature_frame: pd.DataFrame, labels: pd.Series, rule: str, prefix: str) -> dict[str, float | int]:
    metrics = evaluate_and_rule(feature_frame, labels, parse_rule(rule))
    return {f"{prefix}_{key}": value for key, value in metrics.items()}


def validate_train_rules_on_test(
    feature_frame: pd.DataFrame,
    labels: pd.DataFrame,
    train_scores: pd.DataFrame,
    split_time: str | pd.Timestamp,
    mode: str = "all_background",
    top_features: int = 8,
    max_rule_size: int = 3,
    min_precision: float = 0.01,
    min_recall: float = 0.05,
    top_n: int = 10,
) -> pd.DataFrame:
    train_mask, test_mask = temporal_split_masks(feature_frame, split_time)
    rows = []
    for strategy in [column for column in labels.columns if column != "time"]:
        train_context = train_mask.copy()
        test_context = test_mask.copy()
        if mode == "matched_hour_weekday":
            train_context &= matched_context_mask(feature_frame.loc[train_mask, "time"], labels.loc[train_mask, strategy]).reindex(feature_frame.index, fill_value=False)
            test_context &= matched_context_mask(feature_frame.loc[test_mask, "time"], labels.loc[test_mask, strategy]).reindex(feature_frame.index, fill_value=False)
        rules = mine_candidate_rules(
            feature_frame.loc[train_context].reset_index(drop=True),
            labels.loc[train_context, ["time", strategy]].reset_index(drop=True),
            train_scores[train_scores["strategy"].eq(strategy)],
            top_features=top_features,
            max_rule_size=max_rule_size,
            min_precision=min_precision,
            min_recall=min_recall,
            top_n=top_n,
        )
        for rule_row in rules.itertuples(index=False):
            train_eval = evaluate_rule_on_period(feature_frame.loc[train_context].reset_index(drop=True), labels.loc[train_context, strategy].reset_index(drop=True), rule_row.rule, "train")
            test_eval = evaluate_rule_on_period(feature_frame.loc[test_context].reset_index(drop=True), labels.loc[test_context, strategy].reset_index(drop=True), rule_row.rule, "test")
            rows.append(
                {
                    "mode": mode,
                    "strategy": strategy,
                    "rule": rule_row.rule,
                    "rule_size": int(rule_row.rule_size),
                    **train_eval,
                    **test_eval,
                }
            )
    return pd.DataFrame(rows)
