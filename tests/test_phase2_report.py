import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from phase2_feature_engineering import build_feature_dictionary, build_phase2_report


class Phase2ReportTests(unittest.TestCase):
    def test_feature_dictionary_documents_pandas_ta_and_basket_structure_columns(self):
        deal_features = pd.DataFrame(
            {
                "position_id": [1],
                "strategy": ["T1/S01"],
                "m15_rsi_14": [55.0],
                "m15_adx_14": [22.0],
                "m15_macd_12_26_9": [1.2],
                "m1_mfe_points": [5.0],
                "is_initial_entry": [True],
            }
        )
        basket_features = pd.DataFrame(
            {
                "basket_id": [1],
                "add_on_count": [2],
                "closed_together_within_1m": [False],
                "utc_entry_session_est": ["london"],
            }
        )

        dictionary = build_feature_dictionary(deal_features, basket_features)

        self.assertIn("m15_rsi_14", dictionary)
        self.assertIn("pandas-ta-classic", dictionary)
        self.assertIn("add_on_count", dictionary)
        self.assertIn("closed_together_within_1m", dictionary)

    def test_phase2_report_summarizes_outputs_and_m15_initial_entry_timing(self):
        deal_features = pd.DataFrame(
            {
                "position_id": [1, 2],
                "strategy": ["T1/S01", "T1/S01"],
                "pnl_est": [10.0, -2.0],
                "is_initial_entry": [True, False],
                "broker_entry_minute_mod_15": [0, 7],
                "m1_path_available": [True, True],
                "m1_mae_points": [1.0, 2.0],
                "m1_mfe_points": [3.0, 4.0],
            }
        )
        basket_features = pd.DataFrame(
            {
                "basket_id": [1],
                "strategy": ["T1/S01"],
                "pnl_est": [8.0],
                "add_on_count": [1],
            }
        )

        report = build_phase2_report(deal_features, basket_features)

        self.assertIn("deal_features.parquet", report)
        self.assertIn("basket_features.parquet", report)
        self.assertIn("Initial-entry M15 alignment", report)
        self.assertIn("T1/S01", report)


if __name__ == "__main__":
    unittest.main()
