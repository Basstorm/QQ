import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qq_research.rule_inference import (
    build_strategy_profiles_report,
    classify_candidate_family,
    feature_contrast_table,
)


class RuleInferenceTests(unittest.TestCase):
    def test_feature_contrast_table_ranks_strategy_specific_shifts(self):
        rows = pd.DataFrame(
            {
                "strategy": ["T1/S01", "T1/S01", "T2/S03", "T2/S03"],
                "m15_rsi_14": [70.0, 72.0, 40.0, 42.0],
                "m15_adx_14": [20.0, 22.0, 21.0, 23.0],
            }
        )

        contrast = feature_contrast_table(rows, "T1/S01", ["m15_rsi_14", "m15_adx_14"])

        self.assertEqual(contrast.iloc[0]["feature"], "m15_rsi_14")
        self.assertGreater(contrast.iloc[0]["effect_size"], 1.0)

    def test_classify_candidate_family_detects_momentum_breakout_context(self):
        medians = {
            "m15_momentum_16_close_points": 12.0,
            "m15_breakout_above_recent_high_8_points": 2.5,
            "m15_close_distance_to_ema_21": 4.0,
            "m15_adx_14": 28.0,
            "m15_rsi_14": 62.0,
        }

        label, confidence, evidence = classify_candidate_family(medians)

        self.assertEqual(label, "trend breakout / momentum continuation")
        self.assertEqual(confidence, "medium")
        self.assertTrue(any("momentum" in item for item in evidence))

    def test_build_strategy_profiles_report_includes_uncertainty_and_expanded_indicator_fallback(self):
        deal_features = pd.DataFrame(
            {
                "strategy": ["T1/S01", "T2/S03"],
                "is_initial_entry": [True, True],
                "broker_entry_session": ["london", "asia"],
                "m15_momentum_16_close_points": [10.0, -2.0],
                "m15_breakout_above_recent_high_8_points": [1.0, -1.0],
                "m15_close_distance_to_ema_21": [3.0, -3.0],
                "m15_adx_14": [30.0, 15.0],
                "m15_rsi_14": [65.0, 45.0],
                "m1_mae_points": [1.0, 2.0],
                "m1_mfe_points": [3.0, 4.0],
            }
        )
        basket_features = pd.DataFrame(
            {
                "strategy": ["T1/S01", "T2/S03"],
                "basket_id": [1, 2],
                "direction": ["long", "short"],
                "pnl_est": [10.0, -2.0],
                "holding_minutes": [30.0, 60.0],
                "add_on_count": [1, 2],
                "m1_mae_points": [1.0, 2.0],
                "m1_mfe_points": [3.0, 4.0],
            }
        )

        report = build_strategy_profiles_report(deal_features, basket_features)

        self.assertIn("T1/S01", report)
        self.assertIn("Uncertainty", report)
        self.assertIn("Expanded indicator fallback", report)


if __name__ == "__main__":
    unittest.main()
