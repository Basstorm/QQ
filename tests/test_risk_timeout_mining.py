import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qq_research.risk_timeout_mining import build_risk_timeout_report, build_strategy_risk_frame, mine_timeout_candidates


class RiskTimeoutMiningTests(unittest.TestCase):
    def test_build_strategy_risk_frame_measures_hold_exit_and_adverse_path(self):
        lifecycle = pd.DataFrame(
            {
                "basket_id": [1, 1, 1, 2, 2],
                "strategy": ["T6/S12", "T6/S12", "T6/S12", "T3/S06", "T3/S06"],
                "direction": ["short", "short", "short", "short", "short"],
                "time": pd.to_datetime(["2024-01-01 10:00", "2024-01-01 10:01", "2024-01-01 10:02", "2024-01-01 11:00", "2024-01-01 11:01"]),
                "minutes_since_initial_entry": [0.0, 1.0, 2.0, 0.0, 1.0],
                "open_layer_count": [1, 1, 1, 1, 2],
                "close_move_from_open_vwap_points": [0.0, -2.0, 1.2, -0.5, -1.5],
                "is_final_exit_minute": [False, False, True, False, True],
            }
        )

        risk = build_strategy_risk_frame(lifecycle)

        first = risk[risk["basket_id"].eq(1)].iloc[0]
        self.assertEqual(first["holding_min"], 2.0)
        self.assertEqual(first["max_layers"], 1)
        self.assertAlmostEqual(first["exit_move"], 1.2)
        self.assertAlmostEqual(first["max_adverse_points"], 2.0)
        self.assertAlmostEqual(first["max_favorable_points"], 1.2)

    def test_mine_timeout_candidates_returns_strategy_quantiles_and_tail_counts(self):
        risk = pd.DataFrame(
            {
                "strategy": ["T6/S12"] * 4,
                "holding_min": [10.0, 20.0, 100.0, 1000.0],
                "max_adverse_points": [1.0, 2.0, 3.0, 40.0],
                "exit_move": [1.0, 1.2, 1.4, -5.0],
                "max_layers": [1, 1, 2, 6],
            }
        )

        candidates = mine_timeout_candidates(risk)

        self.assertEqual(candidates.iloc[0]["strategy"], "T6/S12")
        self.assertEqual(candidates.iloc[0]["basket_count"], 4)
        self.assertEqual(candidates.iloc[0]["negative_exit_count"], 1)
        self.assertGreater(candidates.iloc[0]["hold_q90"], candidates.iloc[0]["hold_median"])
        self.assertIn("T6/S12", build_risk_timeout_report(candidates))


if __name__ == "__main__":
    unittest.main()
