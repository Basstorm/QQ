import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qq_research.add_on_trigger_mining import (
    build_add_on_trigger_frame,
    evaluate_threshold,
    mine_add_on_thresholds,
)


class AddOnTriggerMiningTests(unittest.TestCase):
    def test_build_add_on_trigger_frame_filters_to_rows_with_prior_state(self):
        lifecycle = pd.DataFrame(
            {
                "strategy": ["T1/S01", "T1/S01", "T1/S01"],
                "pre_open_layer_count": [0, 1, 1],
                "adverse_from_pre_last_entry_points": [None, 1.0, 2.0],
                "is_add_on_minute": [False, False, True],
            }
        )

        frame = build_add_on_trigger_frame(lifecycle)

        self.assertEqual(len(frame), 2)
        self.assertEqual(frame["is_positive"].tolist(), [False, True])

    def test_evaluate_threshold_computes_precision_recall_and_lift(self):
        frame = pd.DataFrame({"adverse": [0.5, 1.0, 2.0, 3.0], "is_positive": [False, True, True, False]})

        metrics = evaluate_threshold(frame, "adverse", 1.0)

        self.assertEqual(metrics["matched"], 3)
        self.assertEqual(metrics["true_positive"], 2)
        self.assertAlmostEqual(metrics["recall"], 1.0)
        self.assertAlmostEqual(metrics["precision_lift_vs_base"], (2 / 3) / (2 / 4))

    def test_mine_add_on_thresholds_returns_strategy_layer_rows(self):
        frame = pd.DataFrame(
            {
                "strategy": ["T1/S01"] * 6,
                "pre_open_layer_count": [1, 1, 1, 1, 1, 1],
                "adverse_from_pre_last_entry_points": [0.2, 1.5, 1.7, 1.8, 0.3, 2.0],
                "minutes_since_pre_last_entry": [1, 5, 6, 8, 2, 10],
                "is_positive": [False, True, True, True, False, True],
            }
        )

        thresholds = mine_add_on_thresholds(frame, min_positives=2)

        self.assertEqual(thresholds.iloc[0]["strategy"], "T1/S01")
        self.assertEqual(thresholds.iloc[0]["pre_open_layer_count"], 1)
        self.assertIn("adverse_q25", thresholds.columns)


if __name__ == "__main__":
    unittest.main()
