import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from phase1_reconstruct_trades import build_report


class Phase1ReportTests(unittest.TestCase):
    def test_seconds_diagnostics_reports_actual_second_values(self):
        deals = pd.DataFrame(
            [
                {"time": pd.Timestamp("2024-01-01 10:00:00"), "entry": "in", "m1_match_tol_0_25": True, "profit": 0.0},
                {"time": pd.Timestamp("2024-01-01 10:01:00"), "entry": "in", "m1_match_tol_0_25": True, "profit": 0.0},
                {"time": pd.Timestamp("2024-01-01 10:02:01"), "entry": "in", "m1_match_tol_0_25": True, "profit": 0.0},
                {"time": pd.Timestamp("2024-01-01 10:03:02"), "entry": "out", "m1_match_tol_0_25": True, "profit": 3.0},
                {"time": pd.Timestamp("2024-01-01 10:04:02"), "entry": "out", "m1_match_tol_0_25": True, "profit": 4.0},
            ]
        )
        positions = pd.DataFrame(
            [
                {
                    "position_id": 1,
                    "strategy": "T1/S01",
                    "volume": 0.1,
                    "pnl_est": 3.0,
                    "holding_seconds": 60,
                },
                {
                    "position_id": 2,
                    "strategy": "T1/S01",
                    "volume": 0.1,
                    "pnl_est": 4.0,
                    "holding_seconds": 120,
                },
            ]
        )
        baskets = pd.DataFrame(
            [
                {
                    "basket_id": 1,
                    "strategy": "T1/S01",
                    "position_count": 2,
                    "max_layers": 2,
                    "first_entry_time": pd.Timestamp("2024-01-01 10:00:00"),
                }
            ]
        )

        report = build_report(deals, positions, baskets)

        self.assertIn("| 0 | 2 |", report)
        self.assertIn("| 1 | 1 |", report)
        self.assertIn("| 2 | 2 |", report)
        self.assertNotIn("| 790 |", report)


if __name__ == "__main__":
    unittest.main()
