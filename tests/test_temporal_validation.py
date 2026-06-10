import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qq_research.temporal_validation import (
    evaluate_rule_on_period,
    matched_context_mask,
    parse_rule,
    temporal_split_masks,
    validate_train_rules_on_test,
)


class TemporalValidationTests(unittest.TestCase):
    def test_temporal_split_masks_partition_rows_by_split_time(self):
        frame = pd.DataFrame({"time": pd.to_datetime(["2020-01-01", "2021-01-01", "2021-01-02"])})

        train, test = temporal_split_masks(frame, "2021-01-01")

        self.assertEqual(train.tolist(), [True, False, False])
        self.assertEqual(test.tolist(), [False, True, True])

    def test_parse_rule_recovers_conditions_from_rule_string(self):
        rule = "a >= 1.2500 AND b <= -2.5000"

        conditions = parse_rule(rule)

        self.assertEqual(conditions[0]["feature"], "a")
        self.assertEqual(conditions[0]["operator"], ">=")
        self.assertEqual(conditions[1]["threshold"], -2.5)

    def test_matched_context_mask_keeps_positive_rows_and_same_hour_weekday_negatives(self):
        times = pd.to_datetime(
            [
                "2024-01-01 10:00",
                "2024-01-01 10:15",
                "2024-01-01 11:00",
                "2024-01-02 10:00",
            ]
        )
        labels = pd.Series([True, False, False, False])

        mask = matched_context_mask(times, labels)

        self.assertEqual(mask.tolist(), [True, True, False, False])

    def test_evaluate_rule_on_period_returns_prefixed_metrics(self):
        features = pd.DataFrame(
            {
                "time": pd.date_range("2024-01-01", periods=4, freq="15min"),
                "a": [0, 2, 3, 4],
            }
        )
        labels = pd.Series([False, True, True, False])

        row = evaluate_rule_on_period(features, labels, "a >= 2", "test")

        self.assertAlmostEqual(row["test_precision"], 2 / 3)
        self.assertAlmostEqual(row["test_recall"], 1.0)
        self.assertIn("test_precision_lift_vs_base", row)

    def test_validate_train_rules_on_test_returns_train_and_test_metrics(self):
        features = pd.DataFrame(
            {
                "time": pd.date_range("2020-01-01", periods=8, freq="365D"),
                "signal": [0, 2, 3, 4, 0, 2, 3, 4],
            }
        )
        labels = pd.DataFrame({"time": features["time"], "T1/S01": [False, True, True, False, False, True, True, False]})
        scores = pd.DataFrame(
            {
                "strategy": ["T1/S01"],
                "feature": ["signal"],
                "direction": ["high"],
                "positive_median": [2.5],
                "auc_lift": [0.4],
            }
        )

        validation = validate_train_rules_on_test(features, labels, scores, "2022-01-01", min_precision=0.0, min_recall=0.0)

        self.assertFalse(validation.empty)
        self.assertIn("train_precision", validation.columns)
        self.assertIn("test_precision_lift_vs_base", validation.columns)


if __name__ == "__main__":
    unittest.main()
