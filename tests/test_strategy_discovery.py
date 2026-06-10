import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qq_research.strategy_discovery import (
    build_cluster_report,
    choose_best_k,
    cluster_strategy_overlap,
    prepare_clustering_matrix,
    select_clustering_features,
)


class StrategyDiscoveryTests(unittest.TestCase):
    def test_select_clustering_features_keeps_behavior_features_and_excludes_identifiers(self):
        baskets = pd.DataFrame(
            {
                "basket_id": [1, 2, 3],
                "strategy": ["T1/S01", "T2/S03", "T3/S06"],
                "pnl_est": [10.0, 20.0, -5.0],
                "add_on_count": [0, 1, 2],
                "initial_entry_price": [1800.0, 1900.0, 2000.0],
                "m15_close": [1801.0, 1901.0, 2001.0],
                "m15_rsi_14": [45.0, 55.0, 35.0],
                "m1_mae_points": [1.0, 2.0, 9.0],
                "all_missing": [None, None, None],
                "text_label": ["a", "b", "c"],
            }
        )

        selected = select_clustering_features(baskets)

        self.assertIn("add_on_count", selected)
        self.assertIn("m15_rsi_14", selected)
        self.assertIn("m1_mae_points", selected)
        self.assertNotIn("basket_id", selected)
        self.assertNotIn("strategy", selected)
        self.assertNotIn("pnl_est", selected)
        self.assertNotIn("initial_entry_price", selected)
        self.assertNotIn("m15_close", selected)
        self.assertNotIn("all_missing", selected)
        self.assertNotIn("text_label", selected)

    def test_prepare_clustering_matrix_scales_large_zero_iqr_columns(self):
        baskets = pd.DataFrame(
            {
                "large_zero_iqr": [3_091_471.0, 3_091_471.0, 3_091_471.0, 3_091_471.0, 6_000_000.0],
                "normal_feature": [1.0, 2.0, 3.0, None, 100.0],
            }
        )

        matrix = prepare_clustering_matrix(baskets, ["large_zero_iqr", "normal_feature"])

        self.assertTrue(pd.notna(matrix).all())
        self.assertLess(abs(matrix).max(), 5.0)

    def test_choose_best_k_prefers_highest_silhouette_then_smaller_k(self):
        diagnostics = pd.DataFrame(
            {
                "k": [2, 3, 4],
                "silhouette": [0.30, 0.45, 0.45],
            }
        )

        self.assertEqual(choose_best_k(diagnostics), 3)

    def test_cluster_strategy_overlap_reports_dominant_strategy_and_purity(self):
        assignments = pd.DataFrame(
            {
                "strategy": ["T1/S01", "T1/S01", "T2/S03", "T2/S03", "T2/S03"],
                "cluster": [0, 0, 0, 1, 1],
            }
        )

        overlap = cluster_strategy_overlap(assignments, "cluster")

        cluster0 = overlap.set_index("cluster").loc[0]
        cluster1 = overlap.set_index("cluster").loc[1]
        self.assertEqual(cluster0["dominant_strategy"], "T1/S01")
        self.assertAlmostEqual(cluster0["dominant_strategy_share"], 2 / 3)
        self.assertEqual(cluster1["dominant_strategy"], "T2/S03")
        self.assertAlmostEqual(cluster1["dominant_strategy_share"], 1.0)

    def test_build_cluster_report_mentions_active_strategies_and_forced_12_view(self):
        assignments = pd.DataFrame(
            {
                "basket_id": [1, 2],
                "strategy": ["T1/S01", "T2/S03"],
                "cluster_best": [0, 1],
                "cluster_k12": [3, 4],
            }
        )
        diagnostics = pd.DataFrame({"k": [2, 12], "silhouette": [0.25, 0.10]})
        overlap = pd.DataFrame(
            {
                "cluster": [0, 1],
                "rows": [1, 1],
                "dominant_strategy": ["T1/S01", "T2/S03"],
                "dominant_strategy_share": [1.0, 1.0],
            }
        )

        report = build_cluster_report(assignments, diagnostics, overlap, best_k=2, feature_columns=["m15_rsi_14", "m1_mae_points"])

        self.assertIn("Active explicit strategies: `2`", report)
        self.assertIn("Forced 12-cluster view", report)
        self.assertIn("m15_rsi_14", report)


if __name__ == "__main__":
    unittest.main()
