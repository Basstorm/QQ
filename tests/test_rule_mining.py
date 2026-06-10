import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qq_research.rule_mining import (
    build_candidate_rules_report,
    build_single_feature_conditions,
    evaluate_and_rule,
)


class RuleMiningTests(unittest.TestCase):
    def test_build_single_feature_conditions_uses_positive_median_threshold_and_direction(self):
        scores = pd.DataFrame(
            {
                "strategy": ["T1/S01", "T1/S01"],
                "feature": ["strong_high", "strong_low"],
                "direction": ["high", "low"],
                "positive_median": [10.0, -5.0],
                "auc_lift": [0.4, 0.3],
            }
        )

        conditions = build_single_feature_conditions(scores, "T1/S01", top_n=2)

        self.assertEqual(conditions[0]["operator"], ">=")
        self.assertEqual(conditions[0]["threshold"], 10.0)
        self.assertEqual(conditions[1]["operator"], "<=")
        self.assertEqual(conditions[1]["threshold"], -5.0)

    def test_evaluate_and_rule_computes_precision_and_recall(self):
        features = pd.DataFrame(
            {
                "time": pd.date_range("2024-01-01", periods=5, freq="15min"),
                "a": [0, 1, 2, 3, 4],
                "b": [5, 4, 3, 2, 1],
            }
        )
        labels = pd.Series([False, False, True, True, False])
        rule = [
            {"feature": "a", "operator": ">=", "threshold": 2},
            {"feature": "b", "operator": "<=", "threshold": 3},
        ]

        metrics = evaluate_and_rule(features, labels, rule)

        self.assertEqual(metrics["matched"], 3)
        self.assertEqual(metrics["true_positive"], 2)
        self.assertAlmostEqual(metrics["precision"], 2 / 3)
        self.assertAlmostEqual(metrics["recall"], 1.0)
        self.assertAlmostEqual(metrics["base_rate"], 2 / 5)
        self.assertAlmostEqual(metrics["precision_lift_vs_base"], (2 / 3) / (2 / 5))

    def test_build_candidate_rules_report_mentions_caution_and_strategy(self):
        rules = pd.DataFrame(
            {
                "strategy": ["T1/S01"],
                "rule": ["strong_high >= 10.000"],
                "precision": [0.5],
                "recall": [0.8],
                "matched": [10],
                "true_positive": [5],
                "false_positive": [5],
                "precision_lift_vs_base": [3.0],
            }
        )

        report = build_candidate_rules_report(rules)

        self.assertIn("T1/S01", report)
        self.assertIn("hypotheses", report)
        self.assertIn("strong_high", report)


if __name__ == "__main__":
    unittest.main()
