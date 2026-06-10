import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qq_research.lifecycle_management import (
    build_add_on_events,
    build_exit_events,
    build_minute_lifecycle,
)


class LifecycleManagementTests(unittest.TestCase):
    def test_build_add_on_events_measures_directional_adverse_spacing(self):
        positions = pd.DataFrame(
            {
                "basket_id": [1, 1, 1],
                "strategy": ["T1/S01"] * 3,
                "direction": ["long"] * 3,
                "position_id": [1, 2, 3],
                "entry_time": pd.to_datetime(["2024-01-01 10:00", "2024-01-01 10:10", "2024-01-01 10:30"]),
                "exit_time": pd.to_datetime(["2024-01-01 11:00"] * 3),
                "entry_price": [100.0, 98.5, 96.0],
                "exit_price": [101.0, 101.0, 101.0],
                "volume": [0.1, 0.2, 0.4],
            }
        )

        events = build_add_on_events(positions)

        self.assertEqual(events["layer_index"].tolist(), [2, 3])
        self.assertAlmostEqual(events.iloc[0]["adverse_from_prev_entry_points"], 1.5)
        self.assertAlmostEqual(events.iloc[1]["adverse_from_initial_entry_points"], 4.0)
        self.assertAlmostEqual(events.iloc[1]["volume_multiplier_vs_prev"], 2.0)

    def test_build_exit_events_measures_take_profit_from_weighted_average(self):
        positions = pd.DataFrame(
            {
                "basket_id": [1, 1],
                "strategy": ["T1/S01", "T1/S01"],
                "direction": ["long", "long"],
                "position_id": [1, 2],
                "entry_time": pd.to_datetime(["2024-01-01 10:00", "2024-01-01 10:10"]),
                "exit_time": pd.to_datetime(["2024-01-01 11:00", "2024-01-01 11:00"]),
                "entry_price": [100.0, 98.0],
                "exit_price": [100.0, 100.0],
                "volume": [1.0, 1.0],
                "pnl_est": [0.0, 200.0],
            }
        )

        exits = build_exit_events(positions)

        self.assertAlmostEqual(exits.iloc[0]["entry_vwap"], 99.0)
        self.assertAlmostEqual(exits.iloc[0]["exit_move_from_entry_vwap_points"], 1.0)
        self.assertEqual(exits.iloc[0]["position_count"], 2)

    def test_build_minute_lifecycle_marks_add_on_and_final_exit_minutes(self):
        positions = pd.DataFrame(
            {
                "basket_id": [1, 1],
                "strategy": ["T1/S01", "T1/S01"],
                "direction": ["long", "long"],
                "position_id": [1, 2],
                "entry_time": pd.to_datetime(["2024-01-01 10:00", "2024-01-01 10:02"]),
                "exit_time": pd.to_datetime(["2024-01-01 10:04", "2024-01-01 10:04"]),
                "entry_price": [100.0, 99.0],
                "exit_price": [101.0, 101.0],
                "volume": [1.0, 1.0],
            }
        )
        m1 = pd.DataFrame(
            {
                "time": pd.date_range("2024-01-01 10:00", periods=5, freq="min"),
                "high": [100.2, 99.8, 99.2, 100.4, 101.2],
                "low": [99.8, 99.2, 98.8, 99.7, 100.8],
                "close": [100.0, 99.5, 99.0, 100.0, 101.0],
            }
        )

        lifecycle = build_minute_lifecycle(positions, m1)

        self.assertEqual(len(lifecycle), 5)
        self.assertEqual(lifecycle["is_add_on_minute"].tolist(), [False, False, True, False, False])
        self.assertEqual(lifecycle["is_final_exit_minute"].tolist(), [False, False, False, False, True])
        self.assertAlmostEqual(lifecycle.loc[lifecycle["time"].eq(pd.Timestamp("2024-01-01 10:03")), "open_entry_vwap"].iloc[0], 99.5)
        add_on_row = lifecycle[lifecycle["time"].eq(pd.Timestamp("2024-01-01 10:02"))].iloc[0]
        self.assertEqual(add_on_row["pre_open_layer_count"], 1)
        self.assertAlmostEqual(add_on_row["close_move_from_pre_open_vwap_points"], -1.0)
        self.assertAlmostEqual(add_on_row["pre_last_entry_price"], 100.0)
        self.assertAlmostEqual(add_on_row["minutes_since_pre_last_entry"], 2.0)
        self.assertAlmostEqual(add_on_row["adverse_from_pre_last_entry_points"], 1.0)
        exit_row = lifecycle[lifecycle["time"].eq(pd.Timestamp("2024-01-01 10:04"))].iloc[0]
        self.assertAlmostEqual(exit_row["high_move_from_open_vwap_points"], 1.7)
        self.assertAlmostEqual(exit_row["low_move_from_open_vwap_points"], 1.3)
        self.assertAlmostEqual(exit_row["touch_move_from_open_vwap_points"], 1.7)


if __name__ == "__main__":
    unittest.main()
