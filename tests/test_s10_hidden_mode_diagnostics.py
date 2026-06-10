import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qq_research.s10_hidden_mode_diagnostics import (
    build_s10_basket_feature_frame,
    build_s10_hidden_mode_report,
    label_s10_target_modes,
    score_s10_mode_feature_rules,
    score_s10_mode_features,
)


class S10HiddenModeDiagnosticsTests(unittest.TestCase):
    def test_label_s10_target_modes_assigns_interpretable_modes(self):
        diagnostics = pd.DataFrame(
            {
                "basket_id": [1, 2, 3, 4],
                "exit_time": pd.to_datetime(["2024-01-01 22:10", "2024-01-02 03:00", "2024-01-02 10:00", "2024-01-02 22:30"]),
                "holding_min": [10.0, 300.0, 600.0, 60.0],
                "exit_move": [1.0, 1.8, 3.5, -0.2],
            }
        )

        labeled = label_s10_target_modes(diagnostics)

        self.assertEqual(labeled["target_mode"].tolist(), ["quick_low", "overnight_medium", "late_high", "timeout_loss"])

    def test_build_s10_basket_feature_frame_extracts_entry_and_early_path(self):
        lifecycle = pd.DataFrame(
            {
                "basket_id": [1, 1, 1],
                "strategy": ["T5/S10"] * 3,
                "time": pd.date_range("2024-01-01 22:00", periods=3, freq="min"),
                "minutes_since_initial_entry": [0.0, 1.0, 2.0],
                "open_layer_count": [1, 1, 2],
                "close_move_from_open_vwap_points": [0.0, 0.5, -0.2],
                "adverse_from_pre_last_entry_points": [None, None, 1.0],
                "is_add_on_minute": [False, False, True],
            }
        )
        labeled = pd.DataFrame({"basket_id": [1], "target_mode": ["quick_low"]})

        features = build_s10_basket_feature_frame(lifecycle, labeled)

        self.assertEqual(features.iloc[0]["entry_hour"], 22)
        self.assertAlmostEqual(features.iloc[0]["mfe_5m"], 0.5)
        self.assertAlmostEqual(features.iloc[0]["mae_5m"], -0.2)
        self.assertEqual(features.iloc[0]["add_ons_30m"], 1)

    def test_score_s10_mode_features_ranks_separating_feature(self):
        features = pd.DataFrame(
            {
                "target_mode": ["a", "a", "b", "b"],
                "strong": [1.0, 1.1, 5.0, 5.2],
                "weak": [1.0, 2.0, 1.5, 2.5],
            }
        )

        scores = score_s10_mode_features(features, ["strong", "weak"])

        self.assertEqual(scores.iloc[0]["feature"], "strong")
        self.assertGreater(scores.iloc[0]["eta_squared"], 0.9)
        self.assertIn("T5/S10", build_s10_hidden_mode_report(features, scores))

    def test_score_s10_mode_feature_rules_returns_best_one_feature_rules(self):
        features = pd.DataFrame(
            {
                "target_mode": ["quick", "quick", "other", "other"],
                "mfe": [2.0, 2.2, 0.1, 0.2],
            }
        )

        rules = score_s10_mode_feature_rules(features, ["mfe"])

        quick_rules = rules[rules["target_mode"].eq("quick")]
        self.assertEqual(quick_rules.iloc[0]["feature"], "mfe")
        self.assertGreaterEqual(quick_rules.iloc[0]["f1"], 0.9)


if __name__ == "__main__":
    unittest.main()
