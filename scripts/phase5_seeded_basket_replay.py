from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from qq_research.seeded_basket_replay import build_replay_report, replay_seeded_baskets, summarize_replay

OUTPUTS = PROJECT / "outputs"
POSITIONS = OUTPUTS / "positions.parquet"
M1_CSV = PROJECT / "xauusd_m1_2016_2026.csv"
ADD_ON_RULES = OUTPUTS / "add_on_cooldown_rules.csv"
EXIT_RULES = OUTPUTS / "exit_trigger_thresholds.csv"
REPLAY_CSV = OUTPUTS / "seeded_basket_replay.csv"
SUMMARY_CSV = OUTPUTS / "seeded_basket_replay_summary.csv"
REPORT_MD = OUTPUTS / "seeded_basket_replay.md"
EXCLUDED = {"T5/S10"}
EXIT_VARIANTS = ["move_q25", "move_median", "threshold"]


def build_seed_frame(positions: pd.DataFrame) -> pd.DataFrame:
    ordered = positions.sort_values(["basket_id", "entry_time", "position_id"]).copy()
    ordered["layer_index"] = ordered.groupby("basket_id").cumcount() + 1
    first = ordered[ordered["layer_index"].eq(1)].copy()
    basket_summary = ordered.groupby("basket_id").agg(actual_layer_count=("position_id", "count"), actual_pnl_est=("pnl_est", "sum"))
    seeds = first.merge(basket_summary, left_on="basket_id", right_index=True)
    return seeds[
        [
            "basket_id",
            "strategy",
            "direction",
            "entry_time",
            "exit_time",
            "entry_price",
            "volume",
            "actual_layer_count",
            "actual_pnl_est",
        ]
    ]


def build_volume_schedule(positions: pd.DataFrame) -> dict[tuple[str, int], float]:
    ordered = positions.sort_values(["basket_id", "entry_time", "position_id"]).copy()
    ordered["layer_index"] = ordered.groupby("basket_id").cumcount() + 1
    schedule = ordered.groupby(["strategy", "layer_index"])["volume"].median()
    return {(strategy, int(layer)): float(volume) for (strategy, layer), volume in schedule.items()}


def build_max_layers_by_strategy(positions: pd.DataFrame) -> dict[str, int]:
    ordered = positions.sort_values(["basket_id", "entry_time", "position_id"]).copy()
    ordered["layer_index"] = ordered.groupby("basket_id").cumcount() + 1
    return {strategy: int(layer_count) for strategy, layer_count in ordered.groupby("strategy")["layer_index"].max().items()}


def main() -> None:
    positions = pd.read_parquet(POSITIONS)
    m1 = pd.read_csv(M1_CSV, usecols=["time", "close"])
    add_on_rules = pd.read_csv(ADD_ON_RULES)
    exit_rules = pd.read_csv(EXIT_RULES)
    seeds = build_seed_frame(positions)
    seeds = seeds[~seeds["strategy"].isin(EXCLUDED)]
    scoped_positions = positions[~positions["strategy"].isin(EXCLUDED)]
    volume_schedule = build_volume_schedule(scoped_positions)
    max_layers_by_strategy = build_max_layers_by_strategy(scoped_positions)
    replay_frames = []
    summary_frames = []
    for exit_variant in EXIT_VARIANTS:
        replay = replay_seeded_baskets(
            seeds,
            m1,
            add_on_rules,
            exit_rules,
            volume_schedule=volume_schedule,
            max_layers_by_strategy=max_layers_by_strategy,
            max_minutes=20_160,
            exit_threshold_col=exit_variant,
        )
        replay["variant"] = exit_variant
        summary = summarize_replay(replay, excluded_strategies=EXCLUDED)
        summary["variant"] = exit_variant
        replay_frames.append(replay)
        summary_frames.append(summary)
    replay = pd.concat(replay_frames, ignore_index=True)
    summary = pd.concat(summary_frames, ignore_index=True)
    replay.to_csv(REPLAY_CSV, index=False)
    summary.to_csv(SUMMARY_CSV, index=False)
    REPORT_MD.write_text(build_replay_report(summary), encoding="utf-8")
    print("Wrote outputs/seeded_basket_replay.csv")
    print("Wrote outputs/seeded_basket_replay_summary.csv")
    print("Wrote outputs/seeded_basket_replay.md")


if __name__ == "__main__":
    main()
