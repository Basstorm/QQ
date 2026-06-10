import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qq_research.robust_vectorbt_backtest import (
    build_edge_signals,
    evaluate_rule_mask,
    select_robust_rule_variants,
)


class RobustVectorbtBacktestTests(unittest.TestCase):
    def test_evaluate_rule_mask_applies_and_conditions(self):
        features = pd.DataFrame({"a": [1, 2, 3], "b": [3, 2, 1]})

        mask = evaluate_rule_mask(features, "a >= 2 AND b <= 2")

        self.assertEqual(mask.tolist(), [False, True, True])

    def test_build_edge_signals_enters_on_false_to_true_and_exits_on_true_to_false(self):
        mask = pd.Series([False, True, True, False, True])

        entries, exits = build_edge_signals(mask)

        self.assertEqual(entries.tolist(), [False, True, False, False, True])
        self.assertEqual(exits.tolist(), [False, False, False, True, True])

    def test_select_robust_rule_variants_keeps_only_robust_strategies(self):
        synthesis = pd.DataFrame(
            {
                "strategy": ["T2/S03", "T4/S08"],
                "overall_confidence": ["robust", "sparse_hint"],
                "all_background_confidence": ["robust", "sparse_hint"],
                "matched_confidence": ["moderate", "sparse_hint"],
                "best_all_background_rule": ["a >= 1", "b >= 1"],
                "best_matched_rule": ["a >= 2", "b >= 2"],
            }
        )

        variants = select_robust_rule_variants(synthesis)

        self.assertEqual(variants["strategy"].tolist(), ["T2/S03", "T2/S03"])
        self.assertEqual(variants["variant"].tolist(), ["all_background", "matched_context"])


if __name__ == "__main__":
    unittest.main()
