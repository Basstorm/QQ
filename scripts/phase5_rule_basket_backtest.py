from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from qq_research.rule_basket_backtest import (
    build_rule_backtest_report,
    build_rule_entry_seeds,
    filter_non_overlapping_replays,
    summarize_rule_backtest,
)
from qq_research.seeded_basket_replay import replay_seeded_baskets

OUTPUTS = PROJECT / "outputs"
FEATURES = OUTPUTS / "expanded_indicator_feature_matrix.parquet"
SYNTHESIS = OUTPUTS / "strategy_rule_synthesis.csv"
POSITIONS = OUTPUTS / "positions.parquet"
M1_CSV = PROJECT / "xauusd_m1_2016_2026.csv"
ADD_ON_RULES = OUTPUTS / "add_on_cooldown_rules.csv"
EXIT_RULES = OUTPUTS / "exit_trigger_thresholds.csv"
SEEDS_CSV = OUTPUTS / "rule_basket_backtest_seeds.csv"
TRADES_CSV = OUTPUTS / "rule_basket_backtest_trades.csv"
SUMMARY_CSV = OUTPUTS / "rule_basket_backtest_summary.csv"
REPORT_MD = OUTPUTS / "rule_basket_backtest.md"
EXCLUDED = {"T5/S10"}
ENTRY_VARIANTS = [("all_background", "best_all_background_rule"), ("matched_context", "best_matched_rule")]


def build_direction_map(positions: pd.DataFrame) -> dict[str, str]:
    directions = positions.groupby("strategy")["direction"].agg(lambda values: values.value_counts().idxmax())
    return {strategy: str(direction) for strategy, direction in directions.items()}


def build_max_layers_by_strategy(positions: pd.DataFrame) -> dict[str, int]:
    ordered = positions.sort_values(["basket_id", "entry_time", "position_id"]).copy()
    ordered["layer_index"] = ordered.groupby("basket_id").cumcount() + 1
    return {strategy: int(layer_count) for strategy, layer_count in ordered.groupby("strategy")["layer_index"].max().items()}


def main() -> None:
    features = pd.read_parquet(FEATURES)
    synthesis = pd.read_csv(SYNTHESIS)
    positions = pd.read_parquet(POSITIONS)
    m1 = pd.read_csv(M1_CSV, usecols=["time", "close"])
    add_on_rules = pd.read_csv(ADD_ON_RULES)
    exit_rules = pd.read_csv(EXIT_RULES)
    direction_map = build_direction_map(positions)
    max_layers = build_max_layers_by_strategy(positions[~positions["strategy"].isin(EXCLUDED)])
    seed_frames = []
    replay_frames = []
    for variant, rule_column in ENTRY_VARIANTS:
        seeds = build_rule_entry_seeds(
            features,
            synthesis,
            m1,
            rule_column=rule_column,
            variant=variant,
            direction_map=direction_map,
            excluded_strategies=EXCLUDED,
            initial_volume=1.0,
        )
        replay = replay_seeded_baskets(
            seeds,
            m1,
            add_on_rules,
            exit_rules,
            max_layers_by_strategy=max_layers,
            max_minutes=20_160,
            exit_threshold_col="threshold",
        )
        replay["variant"] = variant
        seed_frames.append(seeds)
        replay_frames.append(filter_non_overlapping_replays(replay))
    seeds = pd.concat(seed_frames, ignore_index=True)
    trades = pd.concat(replay_frames, ignore_index=True)
    summary = summarize_rule_backtest(trades)
    seeds.to_csv(SEEDS_CSV, index=False)
    trades.to_csv(TRADES_CSV, index=False)
    summary.to_csv(SUMMARY_CSV, index=False)
    REPORT_MD.write_text(build_rule_backtest_report(summary), encoding="utf-8")
    print("Wrote outputs/rule_basket_backtest_seeds.csv")
    print("Wrote outputs/rule_basket_backtest_trades.csv")
    print("Wrote outputs/rule_basket_backtest_summary.csv")
    print("Wrote outputs/rule_basket_backtest.md")


if __name__ == "__main__":
    main()
