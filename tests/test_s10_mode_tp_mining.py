import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qq_research.s10_mode_tp_mining import (
    add_s10_exit_modes,
    build_s10_mode_tp_report,
    compute_final_mode_oracle_events,
    compute_mode_first_cross_events,
    mine_s10_mode_tp_thresholds,
)


class S10ModeTpMiningTests(unittest.TestCase):
    def test_add_s10_exit_modes_labels_session_and_holding_bucket(self):
        frame = pd.DataFrame(
            {
                "strategy": ["T5/S10", "T5/S10"],
                "time": [pd.Timestamp("2024-01-01 22:10"), pd.Timestamp("2024-01-02 03:00")],
                "minutes_since_initial_entry": [10.0, 300.0],
            }
        )

        modes = add_s10_exit_modes(frame)

        self.assertEqual(modes["s10_session"].tolist(), ["21-23", "01-04"])
        self.assertEqual(modes["s10_holding_bucket"].tolist(), ["<=30m", "120-360m"])
        self.assertEqual(modes["s10_mode"].tolist(), ["21-23|<=30m", "01-04|120-360m"])

    def test_mine_s10_mode_tp_thresholds_uses_positive_exit_moves_per_mode(self):
        frame = pd.DataFrame(
            {
                "strategy": ["T5/S10"] * 5,
                "time": pd.date_range("2024-01-01 22:00", periods=5, freq="min"),
                "minutes_since_initial_entry": [0, 1, 2, 3, 4],
                "close_move_from_open_vwap_points": [0.2, 0.8, 1.0, 1.4, 2.0],
                "is_final_exit_minute": [False, True, True, False, True],
            }
        )

        thresholds = mine_s10_mode_tp_thresholds(add_s10_exit_modes(frame), min_positives=2)

        self.assertEqual(thresholds.iloc[0]["s10_mode"], "21-23|<=30m")
        self.assertAlmostEqual(thresholds.iloc[0]["tp_median"], 1.0)
        self.assertIn("tp_q25", thresholds.columns)

    def test_compute_mode_first_cross_events_uses_threshold_for_current_mode(self):
        lifecycle = add_s10_exit_modes(
            pd.DataFrame(
                {
                    "basket_id": [1, 1, 1],
                    "strategy": ["T5/S10"] * 3,
                    "time": pd.date_range("2024-01-01 22:00", periods=3, freq="min"),
                    "minutes_since_initial_entry": [0, 1, 2],
                    "close_move_from_open_vwap_points": [0.5, 1.2, 1.4],
                    "is_final_exit_minute": [False, False, True],
                }
            )
        )
        thresholds = pd.DataFrame({"s10_mode": ["21-23|<=30m"], "tp_median": [1.0]})

        events = compute_mode_first_cross_events(lifecycle, thresholds, threshold_col="tp_median")

        self.assertEqual(events.iloc[0]["first_cross_time"], pd.Timestamp("2024-01-01 22:01"))
        self.assertEqual(events.iloc[0]["lag_minutes"], 1.0)
        self.assertIn("T5/S10", build_s10_mode_tp_report(thresholds, events, "tp_median"))

    def test_compute_final_mode_oracle_events_waits_until_exit_mode(self):
        lifecycle = add_s10_exit_modes(
            pd.DataFrame(
                {
                    "basket_id": [1, 1, 1],
                    "strategy": ["T5/S10"] * 3,
                    "time": [pd.Timestamp("2024-01-01 22:00"), pd.Timestamp("2024-01-02 03:00"), pd.Timestamp("2024-01-02 03:01")],
                    "minutes_since_initial_entry": [0, 300, 301],
                    "close_move_from_open_vwap_points": [2.0, 0.5, 1.5],
                    "is_final_exit_minute": [False, False, True],
                }
            )
        )
        thresholds = pd.DataFrame({"s10_mode": ["21-23|<=30m", "01-04|120-360m"], "tp_median": [1.0, 1.0]})

        events = compute_final_mode_oracle_events(lifecycle, thresholds, threshold_col="tp_median")

        self.assertEqual(events.iloc[0]["first_cross_time"], pd.Timestamp("2024-01-02 03:01"))
        self.assertEqual(events.iloc[0]["lag_minutes"], 0.0)


if __name__ == "__main__":
    unittest.main()
