import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qq_research.rule_basket_backtest import (
    build_rule_entry_seeds,
    filter_non_overlapping_replays,
    summarize_rule_backtest,
)


class RuleBasketBacktestTests(unittest.TestCase):
    def test_build_rule_entry_seeds_uses_rule_edges_and_direction_map(self):
        features = pd.DataFrame(
            {
                "time": pd.date_range("2024-01-01 10:00", periods=4, freq="15min"),
                "signal": [0.0, 2.0, 3.0, 0.0],
            }
        )
        synthesis = pd.DataFrame(
            {
                "strategy": ["T1/S01", "T5/S10"],
                "best_all_background_rule": ["signal >= 1.0", "signal >= 1.0"],
            }
        )
        m1 = pd.DataFrame(
            {
                "time": pd.date_range("2024-01-01 10:00", periods=60, freq="min"),
                "close": range(100, 160),
            }
        )

        seeds = build_rule_entry_seeds(
            features,
            synthesis,
            m1,
            rule_column="best_all_background_rule",
            variant="all_background",
            direction_map={"T1/S01": "long", "T5/S10": "long"},
            excluded_strategies={"T5/S10"},
        )

        self.assertEqual(len(seeds), 1)
        self.assertEqual(seeds.iloc[0]["strategy"], "T1/S01")
        self.assertEqual(seeds.iloc[0]["direction"], "long")
        self.assertEqual(seeds.iloc[0]["entry_time"], pd.Timestamp("2024-01-01 10:15"))
        self.assertEqual(seeds.iloc[0]["entry_price"], 115)

    def test_filter_non_overlapping_replays_keeps_first_open_basket_per_strategy_variant(self):
        replay = pd.DataFrame(
            {
                "strategy": ["T1/S01", "T1/S01", "T1/S01"],
                "variant": ["all", "all", "all"],
                "entry_time": pd.to_datetime(["2024-01-01 10:00", "2024-01-01 10:05", "2024-01-01 10:10"]),
                "sim_exit_time": pd.to_datetime(["2024-01-01 10:10", "2024-01-01 10:30", "2024-01-01 10:25"]),
                "sim_pnl_est": [1.0, 2.0, -1.0],
            }
        )

        filtered = filter_non_overlapping_replays(replay)

        self.assertEqual(filtered["entry_time"].tolist(), [pd.Timestamp("2024-01-01 10:00"), pd.Timestamp("2024-01-01 10:10")])

    def test_summarize_rule_backtest_reports_trade_points_and_win_rate(self):
        replay = pd.DataFrame(
            {
                "strategy": ["T1/S01", "T1/S01"],
                "variant": ["all", "all"],
                "sim_pnl_est": [200.0, -100.0],
                "sim_layer_count": [1, 2],
                "sim_closed": [True, True],
                "sim_exit_time": pd.to_datetime(["2024-01-01 10:00", "2024-01-01 10:01"]),
            }
        )

        summary = summarize_rule_backtest(replay)

        self.assertEqual(summary.iloc[0]["trade_count"], 2)
        self.assertAlmostEqual(summary.iloc[0]["total_points"], 1.0)
        self.assertAlmostEqual(summary.iloc[0]["win_rate_pct"], 50.0)
        self.assertEqual(summary.iloc[0]["unclosed_count"], 0)
        self.assertLessEqual(summary.iloc[0]["max_drawdown_points"], 0.0)


if __name__ == "__main__":
    unittest.main()
