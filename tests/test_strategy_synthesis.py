import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qq_research.strategy_synthesis import (
    classify_rule_confidence,
    select_best_temporal_rule,
    synthesize_strategy_rows,
    build_synthesis_report,
)


class StrategySynthesisTests(unittest.TestCase):
    def test_select_best_temporal_rule_prefers_test_lift_then_recall_and_matched_count(self):
        validation = pd.DataFrame(
            {
                "strategy": ["T1/S01", "T1/S01"],
                "mode": ["all_background", "all_background"],
                "rule": ["low_recall", "better"],
                "test_precision_lift_vs_base": [10.0, 10.0],
                "test_recall": [0.1, 0.2],
                "test_matched": [100, 50],
            }
        )

        selected = select_best_temporal_rule(validation, "T1/S01", "all_background")

        self.assertEqual(selected["rule"], "better")

    def test_classify_rule_confidence_marks_stable_and_sparse_rules(self):
        robust = {"test_precision_lift_vs_base": 20.0, "test_recall": 0.4, "test_matched": 100}
        sparse = {"test_precision_lift_vs_base": 100.0, "test_recall": 0.03, "test_matched": 1}

        self.assertEqual(classify_rule_confidence(robust), "robust")
        self.assertEqual(classify_rule_confidence(sparse), "sparse_hint")

    def test_synthesize_strategy_rows_combines_profiles_and_temporal_rules(self):
        profiles = pd.DataFrame(
            {
                "strategy": ["T1/S01"],
                "candidate_family": ["trend continuation"],
                "confidence": ["low"],
            }
        )
        validation = pd.DataFrame(
            {
                "strategy": ["T1/S01"],
                "mode": ["all_background"],
                "rule": ["fisher_9 >= 2"],
                "test_precision_lift_vs_base": [9.0],
                "test_recall": [0.4],
                "test_precision": [0.02],
                "test_matched": [100],
                "train_precision_lift_vs_base": [9.5],
            }
        )

        rows = synthesize_strategy_rows(profiles, validation)

        self.assertEqual(rows.iloc[0]["strategy"], "T1/S01")
        self.assertIn("fisher_9", rows.iloc[0]["best_all_background_rule"])
        self.assertEqual(rows.iloc[0]["all_background_confidence"], "moderate")

    def test_build_synthesis_report_includes_cautions_and_all_strategies(self):
        rows = pd.DataFrame(
            {
                "strategy": ["T1/S01"],
                "candidate_family": ["trend continuation"],
                "overall_confidence": ["moderate"],
                "best_all_background_rule": ["fisher_9 >= 2"],
                "best_matched_rule": ["n/a"],
            }
        )

        report = build_synthesis_report(rows)

        self.assertIn("T1/S01", report)
        self.assertIn("not source-code recovery", report)
        self.assertIn("fisher_9", report)


if __name__ == "__main__":
    unittest.main()
