import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qq_research.exit_trigger_mining import (
    build_exit_threshold_report,
    build_exit_trigger_frame,
    evaluate_exit_threshold,
    mine_exit_thresholds,
)


class ExitTriggerMiningTests(unittest.TestCase):
    def test_build_exit_trigger_frame_uses_active_basket_minutes(self):
        lifecycle = pd.DataFrame(
            {
                "strategy": ["T1/S01", "T1/S01", "T1/S01"],
                "open_layer_count": [0, 1, 1],
                "close_move_from_open_vwap_points": [0.0, 0.4, 0.8],
                "is_final_exit_minute": [False, False, True],
            }
        )

        frame = build_exit_trigger_frame(lifecycle)

        self.assertEqual(len(frame), 2)
        self.assertEqual(frame["is_positive"].tolist(), [False, True])

    def test_evaluate_exit_threshold_scores_vwap_tp_rule(self):
        frame = pd.DataFrame({"move": [0.2, 0.6, 0.8, 1.0], "is_positive": [False, True, True, False]})

        metrics = evaluate_exit_threshold(frame, "move", 0.6)

        self.assertEqual(metrics["matched"], 3)
        self.assertEqual(metrics["true_positive"], 2)
        self.assertAlmostEqual(metrics["recall"], 1.0)
        self.assertAlmostEqual(metrics["precision"], 2 / 3)

    def test_mine_exit_thresholds_returns_strategy_layer_rows(self):
        frame = pd.DataFrame(
            {
                "strategy": ["T1/S01"] * 6,
                "open_layer_count": [1, 1, 1, 1, 1, 1],
                "close_move_from_open_vwap_points": [0.1, 0.5, 0.7, 0.8, 0.9, 1.2],
                "is_positive": [False, True, True, True, False, True],
            }
        )

        thresholds = mine_exit_thresholds(frame, min_positives=2)

        self.assertEqual(thresholds.iloc[0]["strategy"], "T1/S01")
        self.assertEqual(thresholds.iloc[0]["open_layer_count"], 1)
        self.assertIn("move_median", thresholds.columns)
        self.assertIn("T1/S01", build_exit_threshold_report(thresholds))


if __name__ == "__main__":
    unittest.main()
