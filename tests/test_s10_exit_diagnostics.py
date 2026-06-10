import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qq_research.s10_exit_diagnostics import build_s10_exit_report, build_s10_path_diagnostics, summarize_s10_path_diagnostics


class S10ExitDiagnosticsTests(unittest.TestCase):
    def test_build_s10_path_diagnostics_measures_exit_near_max_and_retrace(self):
        lifecycle = pd.DataFrame(
            {
                "basket_id": [1, 1, 1],
                "strategy": ["T5/S10"] * 3,
                "time": pd.date_range("2024-01-01 10:00", periods=3, freq="min"),
                "open_layer_count": [1, 1, 1],
                "minutes_since_initial_entry": [0.0, 1.0, 2.0],
                "close_move_from_open_vwap_points": [0.5, 2.0, 1.7],
                "touch_move_from_open_vwap_points": [0.7, 2.2, 1.9],
                "is_final_exit_minute": [False, False, True],
            }
        )

        diagnostics = build_s10_path_diagnostics(lifecycle)

        self.assertEqual(diagnostics.iloc[0]["basket_id"], 1)
        self.assertAlmostEqual(diagnostics.iloc[0]["max_close_move"], 2.0)
        self.assertAlmostEqual(diagnostics.iloc[0]["exit_move"], 1.7)
        self.assertAlmostEqual(diagnostics.iloc[0]["retrace_from_max_to_exit"], 0.3)
        self.assertEqual(diagnostics.iloc[0]["minutes_max_to_exit"], 1.0)
        self.assertEqual(diagnostics.iloc[0]["entry_time"], pd.Timestamp("2024-01-01 10:00"))

    def test_summarize_s10_path_diagnostics_groups_by_exit_layers(self):
        diagnostics = pd.DataFrame(
            {
                "layers_exit": [1, 1, 2],
                "exit_move": [1.0, 2.0, 3.0],
                "max_close_move": [1.2, 2.1, 3.2],
                "retrace_from_max_to_exit": [0.2, 0.1, 0.2],
                "holding_min": [10.0, 20.0, 30.0],
                "minutes_max_to_exit": [1.0, 1.0, 2.0],
            }
        )

        summary = summarize_s10_path_diagnostics(diagnostics)

        self.assertEqual(summary.loc[summary["layers_exit"].eq(1), "basket_count"].iloc[0], 2)
        self.assertAlmostEqual(summary.loc[summary["layers_exit"].eq(1), "exit_move_median"].iloc[0], 1.5)
        report = build_s10_exit_report(diagnostics, summary)
        self.assertIn("T5/S10", report)
        self.assertIn("Holding Duration Buckets", report)


if __name__ == "__main__":
    unittest.main()
