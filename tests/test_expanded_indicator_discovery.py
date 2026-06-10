import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qq_research.expanded_indicator_discovery import (
    build_entry_label_frame,
    build_ma_relationship_features,
    score_features_for_strategy,
)


class ExpandedIndicatorDiscoveryTests(unittest.TestCase):
    def test_build_ma_relationship_features_adds_stacking_and_cross_columns(self):
        candles = pd.DataFrame(
            {
                "time": pd.date_range("2024-01-01", periods=8, freq="15min"),
                "close": [10.0, 9.0, 8.0, 7.0, 8.0, 9.0, 10.0, 11.0],
            }
        )

        features = build_ma_relationship_features(candles, ma_specs={"ema": [2, 4]}, pairs=[("ema", 2, 4)])

        self.assertIn("ema_2_gt_ema_4", features.columns)
        self.assertIn("ema_2_cross_above_ema_4", features.columns)
        self.assertIn("ema_2_minus_ema_4", features.columns)
        self.assertNotIn("ema_2", features.columns)
        self.assertNotIn("ema_4", features.columns)
        self.assertTrue(features["ema_2_cross_above_ema_4"].any())

    def test_build_entry_label_frame_marks_strategy_entries_on_m15_bars(self):
        m15_times = pd.date_range("2024-01-01 10:00:00", periods=4, freq="15min")
        basket_features = pd.DataFrame(
            {
                "strategy": ["T1/S01", "T2/S03"],
                "entry_m15_time": [m15_times[1], m15_times[3]],
            }
        )

        labels = build_entry_label_frame(m15_times, basket_features)

        self.assertEqual(int(labels["T1/S01"].sum()), 1)
        self.assertTrue(bool(labels.loc[labels["time"].eq(m15_times[1]), "T1/S01"].iloc[0]))
        self.assertFalse(bool(labels.loc[labels["time"].eq(m15_times[0]), "T1/S01"].iloc[0]))

    def test_score_features_for_strategy_ranks_separating_feature_by_auc_lift(self):
        feature_frame = pd.DataFrame(
            {
                "time": pd.date_range("2024-01-01", periods=6, freq="15min"),
                "strong_feature": [0.0, 0.1, 0.2, 10.0, 11.0, 12.0],
                "weak_feature": [1.0, 1.0, 1.0, 1.1, 1.1, 1.1],
            }
        )
        labels = pd.Series([False, False, False, True, True, True], name="T1/S01")

        scores = score_features_for_strategy(feature_frame, labels, "T1/S01", min_valid=4)

        self.assertEqual(scores.iloc[0]["feature"], "strong_feature")
        self.assertAlmostEqual(scores.iloc[0]["auc_lift"], 0.5)


if __name__ == "__main__":
    unittest.main()
