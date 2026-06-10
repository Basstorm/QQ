import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qq_research.exit_first_cross import build_first_cross_report, compute_first_cross_events, summarize_first_cross_lags


class ExitFirstCrossTests(unittest.TestCase):
    def test_compute_first_cross_events_compares_first_signal_to_actual_exit(self):
        lifecycle = pd.DataFrame(
            {
                "basket_id": [1, 1, 1, 1],
                "strategy": ["T1/S01"] * 4,
                "time": pd.date_range("2024-01-01 10:00", periods=4, freq="min"),
                "open_layer_count": [1, 1, 1, 1],
                "close_move_from_open_vwap_points": [0.2, 0.7, 0.8, 0.9],
                "high_move_from_open_vwap_points": [0.3, 0.75, 0.9, 1.0],
                "is_final_exit_minute": [False, False, False, True],
            }
        )
        thresholds = pd.DataFrame({"strategy": ["T1/S01"], "open_layer_count": [1], "move_q25": [0.6]})

        events = compute_first_cross_events(lifecycle, thresholds, threshold_col="move_q25", move_col="close_move_from_open_vwap_points")

        self.assertEqual(events.iloc[0]["first_cross_time"], pd.Timestamp("2024-01-01 10:01"))
        self.assertEqual(events.iloc[0]["actual_exit_time"], pd.Timestamp("2024-01-01 10:03"))
        self.assertEqual(events.iloc[0]["lag_minutes"], 2.0)

    def test_compute_first_cross_events_supports_intrabar_touch_column(self):
        lifecycle = pd.DataFrame(
            {
                "basket_id": [1, 1, 1],
                "strategy": ["T1/S01"] * 3,
                "time": pd.date_range("2024-01-01 10:00", periods=3, freq="min"),
                "open_layer_count": [1, 1, 1],
                "close_move_from_open_vwap_points": [0.2, 0.4, 0.7],
                "touch_move_from_open_vwap_points": [0.3, 0.65, 0.8],
                "is_final_exit_minute": [False, False, True],
            }
        )
        thresholds = pd.DataFrame({"strategy": ["T1/S01"], "open_layer_count": [1], "move_q25": [0.6]})

        events = compute_first_cross_events(lifecycle, thresholds, threshold_col="move_q25", move_col="touch_move_from_open_vwap_points")

        self.assertEqual(events.iloc[0]["first_cross_time"], pd.Timestamp("2024-01-01 10:01"))

    def test_summarize_first_cross_lags_returns_strategy_metrics(self):
        events = pd.DataFrame(
            {
                "strategy": ["T1/S01", "T1/S01", "T2/S03"],
                "open_layer_count_at_exit": [1, 1, 1],
                "lag_minutes": [0.0, 2.0, None],
            }
        )

        summary = summarize_first_cross_lags(events)

        self.assertEqual(summary.loc[summary["strategy"].eq("T1/S01"), "basket_count"].iloc[0], 2)
        self.assertAlmostEqual(summary.loc[summary["strategy"].eq("T1/S01"), "within_1m_pct"].iloc[0], 50.0)
        self.assertIn("T1/S01", build_first_cross_report(summary, "close-cross"))


if __name__ == "__main__":
    unittest.main()
