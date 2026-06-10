import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qq_research.features import (
    add_basket_structure_features,
    add_time_session_features,
    attach_m15_entry_context,
    compute_position_path_features,
)


class FeatureEngineeringTests(unittest.TestCase):
    def test_add_time_session_features_uses_broker_time_and_estimated_utc(self):
        rows = pd.DataFrame(
            [
                {
                    "entry_time": pd.Timestamp("2024-01-05 15:30:00"),
                    "exit_time": pd.Timestamp("2024-01-05 16:45:00"),
                }
            ]
        )

        features = add_time_session_features(rows, "entry_time", "exit_time")

        self.assertEqual(features.loc[0, "broker_entry_hour"], 15)
        self.assertEqual(features.loc[0, "utc_entry_hour_est"], 12)
        self.assertEqual(features.loc[0, "broker_entry_weekday"], 4)
        self.assertTrue(bool(features.loc[0, "broker_entry_is_friday"]))
        self.assertEqual(features.loc[0, "utc_entry_session_est"], "london_newyork_overlap")
        self.assertTrue(bool(features.loc[0, "utc_entry_in_london_est"]))
        self.assertTrue(bool(features.loc[0, "utc_entry_in_newyork_est"]))

    def test_attach_m15_entry_context_joins_containing_bar_and_lookback_features(self):
        positions = pd.DataFrame(
            [
                {
                    "position_id": 1,
                    "entry_time": pd.Timestamp("2024-01-01 10:07:00"),
                    "entry_price": 104.0,
                    "direction": "long",
                }
            ]
        )
        m15 = pd.DataFrame(
            [
                {"time": "2024-01-01 09:15:00+00:00", "open": 99.0, "high": 101.0, "low": 98.0, "close": 100.0, "tick_volume": 10, "spread": 30, "real_volume": 100},
                {"time": "2024-01-01 09:30:00+00:00", "open": 100.0, "high": 102.0, "low": 99.0, "close": 101.0, "tick_volume": 11, "spread": 31, "real_volume": 110},
                {"time": "2024-01-01 09:45:00+00:00", "open": 101.0, "high": 103.0, "low": 100.0, "close": 102.0, "tick_volume": 12, "spread": 32, "real_volume": 120},
                {"time": "2024-01-01 10:00:00+00:00", "open": 102.0, "high": 106.0, "low": 101.0, "close": 105.0, "tick_volume": 13, "spread": 33, "real_volume": 130},
            ]
        )

        features = attach_m15_entry_context(positions, m15, lookbacks=(1, 2), atr_window=3)

        self.assertEqual(features.loc[0, "entry_m15_time"], pd.Timestamp("2024-01-01 10:00:00"))
        self.assertAlmostEqual(features.loc[0, "m15_body_points"], 3.0)
        self.assertAlmostEqual(features.loc[0, "m15_range_points"], 5.0)
        self.assertAlmostEqual(features.loc[0, "entry_price_position_in_m15_range"], 0.6)
        self.assertAlmostEqual(features.loc[0, "m15_momentum_1_close_points"], 3.0)
        self.assertAlmostEqual(features.loc[0, "m15_momentum_2_close_points"], 4.0)
        self.assertAlmostEqual(features.loc[0, "m15_atr_3"], 11 / 3)

    def test_attach_m15_entry_context_adds_pandas_ta_indicator_features(self):
        positions = pd.DataFrame(
            [
                {
                    "position_id": 1,
                    "entry_time": pd.Timestamp("2024-01-01 09:45:00"),
                    "entry_price": 119.0,
                    "direction": "long",
                }
            ]
        )
        m15 = pd.DataFrame(
            [
                {
                    "time": pd.Timestamp("2024-01-01 00:00:00") + pd.Timedelta(minutes=15 * idx),
                    "open": 100.0 + idx,
                    "high": 101.0 + idx,
                    "low": 99.0 + idx,
                    "close": 100.5 + idx,
                    "tick_volume": 100 + idx,
                    "spread": 30,
                    "real_volume": 1000 + idx,
                }
                for idx in range(40)
            ]
        )

        features = attach_m15_entry_context(positions, m15)

        self.assertIn("m15_rsi_14", features.columns)
        self.assertIn("m15_adx_14", features.columns)
        self.assertIn("m15_macd_12_26_9", features.columns)
        self.assertIn("m15_macd_signal_12_26_9", features.columns)
        self.assertFalse(pd.isna(features.loc[0, "m15_rsi_14"]))

    def test_compute_position_path_features_calculates_long_and_short_mae_mfe(self):
        positions = pd.DataFrame(
            [
                {
                    "position_id": 1,
                    "entry_time": pd.Timestamp("2024-01-01 10:00:00"),
                    "exit_time": pd.Timestamp("2024-01-01 10:02:00"),
                    "entry_price": 100.0,
                    "exit_price": 103.0,
                    "direction": "long",
                },
                {
                    "position_id": 2,
                    "entry_time": pd.Timestamp("2024-01-01 10:00:00"),
                    "exit_time": pd.Timestamp("2024-01-01 10:02:00"),
                    "entry_price": 100.0,
                    "exit_price": 97.0,
                    "direction": "short",
                },
            ]
        )
        m1 = pd.DataFrame(
            [
                {"time": "2024-01-01 10:00:00+00:00", "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5, "tick_volume": 10, "spread": 30, "real_volume": 100},
                {"time": "2024-01-01 10:01:00+00:00", "open": 100.5, "high": 104.0, "low": 98.0, "close": 103.5, "tick_volume": 11, "spread": 31, "real_volume": 110},
                {"time": "2024-01-01 10:02:00+00:00", "open": 103.5, "high": 105.0, "low": 97.0, "close": 103.0, "tick_volume": 12, "spread": 32, "real_volume": 120},
            ]
        )

        features = compute_position_path_features(positions, m1)

        long_row = features.set_index("position_id").loc[1]
        short_row = features.set_index("position_id").loc[2]
        self.assertAlmostEqual(long_row["m1_mfe_points"], 5.0)
        self.assertAlmostEqual(long_row["m1_mae_points"], 3.0)
        self.assertAlmostEqual(long_row["m1_net_exit_move_points"], 3.0)
        self.assertAlmostEqual(short_row["m1_mfe_points"], 3.0)
        self.assertAlmostEqual(short_row["m1_mae_points"], 5.0)
        self.assertAlmostEqual(short_row["m1_net_exit_move_points"], 3.0)

    def test_add_basket_structure_features_marks_initial_entries_and_spacing(self):
        positions = pd.DataFrame(
            [
                {
                    "position_id": 1,
                    "basket_id": 10,
                    "entry_time": pd.Timestamp("2024-01-01 10:00:00"),
                    "exit_time": pd.Timestamp("2024-01-01 10:30:00"),
                    "entry_price": 100.0,
                    "volume": 0.1,
                },
                {
                    "position_id": 2,
                    "basket_id": 10,
                    "entry_time": pd.Timestamp("2024-01-01 10:15:00"),
                    "exit_time": pd.Timestamp("2024-01-01 10:31:00"),
                    "entry_price": 98.0,
                    "volume": 0.2,
                },
            ]
        )

        enriched_positions, basket_features = add_basket_structure_features(positions)

        self.assertEqual(list(enriched_positions["entry_sequence_in_basket"]), [1, 2])
        self.assertEqual(list(enriched_positions["is_initial_entry"]), [True, False])
        self.assertAlmostEqual(enriched_positions.loc[1, "minutes_from_basket_first_entry"], 15.0)
        self.assertAlmostEqual(enriched_positions.loc[1, "entry_price_delta_from_initial"], -2.0)
        self.assertAlmostEqual(enriched_positions.loc[1, "volume_multiplier_vs_initial"], 2.0)
        self.assertEqual(basket_features.loc[0, "add_on_count"], 1)
        self.assertAlmostEqual(basket_features.loc[0, "add_on_spacing_minutes_mean"], 15.0)
        self.assertAlmostEqual(basket_features.loc[0, "add_on_spacing_price_abs_mean"], 2.0)
        self.assertAlmostEqual(basket_features.loc[0, "close_span_minutes"], 1.0)


if __name__ == "__main__":
    unittest.main()
