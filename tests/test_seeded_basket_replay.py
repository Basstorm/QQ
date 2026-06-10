import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qq_research.seeded_basket_replay import build_replay_report, replay_seeded_baskets, summarize_replay


class SeededBasketReplayTests(unittest.TestCase):
    def test_replay_seeded_basket_exits_on_close_vwap_tp(self):
        seeds = pd.DataFrame(
            {
                "basket_id": [1],
                "strategy": ["T1/S01"],
                "direction": ["long"],
                "entry_time": [pd.Timestamp("2024-01-01 10:00")],
                "exit_time": [pd.Timestamp("2024-01-01 10:03")],
                "entry_price": [100.0],
                "volume": [0.2],
            }
        )
        m1 = pd.DataFrame(
            {
                "time": pd.date_range("2024-01-01 10:00", periods=4, freq="min"),
                "close": [100.0, 100.3, 100.7, 100.8],
            }
        )
        exit_rules = pd.DataFrame({"strategy": ["T1/S01"], "open_layer_count": [1], "move_q25": [0.6]})
        add_on_rules = pd.DataFrame({"strategy": ["T1/S01"], "pre_open_layer_count": [1], "adverse_threshold": [1.0], "min_minutes": [0.0]})

        replay = replay_seeded_baskets(seeds, m1, add_on_rules, exit_rules)

        self.assertEqual(replay.iloc[0]["sim_exit_time"], pd.Timestamp("2024-01-01 10:02"))
        self.assertEqual(replay.iloc[0]["sim_layer_count"], 1)
        self.assertAlmostEqual(replay.iloc[0]["sim_pnl_est"], 14.0)

    def test_replay_seeded_basket_adds_layer_before_exit(self):
        seeds = pd.DataFrame(
            {
                "basket_id": [1],
                "strategy": ["T1/S01"],
                "direction": ["long"],
                "entry_time": [pd.Timestamp("2024-01-01 10:00")],
                "exit_time": [pd.Timestamp("2024-01-01 10:04")],
                "entry_price": [100.0],
                "volume": [0.2],
            }
        )
        m1 = pd.DataFrame(
            {
                "time": pd.date_range("2024-01-01 10:00", periods=5, freq="min"),
                "close": [100.0, 99.0, 99.2, 99.7, 100.1],
            }
        )
        exit_rules = pd.DataFrame({"strategy": ["T1/S01", "T1/S01"], "open_layer_count": [1, 2], "move_q25": [0.6, 0.5]})
        add_on_rules = pd.DataFrame({"strategy": ["T1/S01"], "pre_open_layer_count": [1], "adverse_threshold": [1.0], "min_minutes": [0.0]})
        volume_schedule = {("T1/S01", 2): 0.2}

        replay = replay_seeded_baskets(seeds, m1, add_on_rules, exit_rules, volume_schedule=volume_schedule)

        self.assertEqual(replay.iloc[0]["sim_layer_count"], 2)
        self.assertEqual(replay.iloc[0]["sim_exit_time"], pd.Timestamp("2024-01-01 10:04"))
        self.assertAlmostEqual(replay.iloc[0]["sim_exit_move_points"], 0.6)

    def test_replay_seeded_basket_respects_max_layers(self):
        seeds = pd.DataFrame(
            {
                "basket_id": [1],
                "strategy": ["T1/S01"],
                "direction": ["long"],
                "entry_time": [pd.Timestamp("2024-01-01 10:00")],
                "exit_time": [pd.Timestamp("2024-01-01 10:05")],
                "entry_price": [100.0],
                "volume": [0.2],
            }
        )
        m1 = pd.DataFrame(
            {
                "time": pd.date_range("2024-01-01 10:00", periods=5, freq="min"),
                "close": [100.0, 99.0, 98.0, 97.0, 96.0],
            }
        )
        exit_rules = pd.DataFrame({"strategy": ["T1/S01"], "open_layer_count": [1], "move_q25": [10.0]})
        add_on_rules = pd.DataFrame({"strategy": ["T1/S01"], "pre_open_layer_count": [1], "adverse_threshold": [1.0], "min_minutes": [0.0]})

        replay = replay_seeded_baskets(seeds, m1, add_on_rules, exit_rules, max_layers_by_strategy={"T1/S01": 2})

        self.assertEqual(replay.iloc[0]["sim_layer_count"], 2)

    def test_summarize_replay_excludes_s10_and_reports_timing(self):
        replay = pd.DataFrame(
            {
                "strategy": ["T1/S01", "T1/S01", "T5/S10"],
                "actual_exit_time": pd.to_datetime(["2024-01-01 10:02", "2024-01-01 11:00", "2024-01-01 12:00"]),
                "sim_exit_time": pd.to_datetime(["2024-01-01 10:03", "2024-01-01 11:10", "2024-01-01 12:00"]),
                "sim_closed": [True, True, True],
                "sim_pnl_est": [10.0, -2.0, 5.0],
                "actual_pnl_est": [9.0, -1.0, 5.0],
                "sim_layer_count": [1, 2, 1],
                "actual_layer_count": [1, 2, 1],
            }
        )

        summary = summarize_replay(replay, excluded_strategies={"T5/S10"})

        self.assertEqual(summary.iloc[0]["strategy"], "T1/S01")
        self.assertEqual(summary.iloc[0]["basket_count"], 2)
        self.assertAlmostEqual(summary.iloc[0]["exit_within_5m_pct"], 50.0)
        self.assertIn("T1/S01", build_replay_report(summary))


if __name__ == "__main__":
    unittest.main()
