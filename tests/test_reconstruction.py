import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qq_research.reconstruction import assign_baskets, parse_strategy_comment, reconstruct_positions_fifo


class ReconstructionTests(unittest.TestCase):
    def test_parse_strategy_comment_extracts_symbol_magic_family_and_strategy(self):
        parsed = parse_strategy_comment("QQ[XAUUSD]1234[T5/S10]")
        self.assertEqual(
            parsed,
            {
                "tag_symbol": "XAUUSD",
                "magic": "1234",
                "T": 5,
                "S": 10,
                "strategy": "T5/S10",
            },
        )

    def test_reconstruct_positions_fifo_preserves_entry_strategy_on_blank_exits(self):
        deals = pd.DataFrame(
            [
                {
                    "time": pd.Timestamp("2018-01-02 22:00:00"),
                    "deal": 2,
                    "order": 2,
                    "symbol": "XAUUSD",
                    "type": "buy",
                    "entry": "in",
                    "volume": 0.2,
                    "price": 1316.19,
                    "profit": 0.0,
                    "comment": "QQ[XAUUSD]1234[T1/S01]",
                },
                {
                    "time": pd.Timestamp("2018-01-02 22:00:00"),
                    "deal": 3,
                    "order": 3,
                    "symbol": "XAUUSD",
                    "type": "buy",
                    "entry": "in",
                    "volume": 0.2,
                    "price": 1316.19,
                    "profit": 0.0,
                    "comment": "QQ[XAUUSD]1234[T5/S10]",
                },
                {
                    "time": pd.Timestamp("2018-01-02 22:33:00"),
                    "deal": 4,
                    "order": 4,
                    "symbol": "XAUUSD",
                    "type": "sell",
                    "entry": "out",
                    "volume": 0.2,
                    "price": 1316.92,
                    "profit": 14.6,
                    "comment": None,
                },
                {
                    "time": pd.Timestamp("2018-01-02 22:36:00"),
                    "deal": 5,
                    "order": 5,
                    "symbol": "XAUUSD",
                    "type": "buy",
                    "entry": "in",
                    "volume": 0.2,
                    "price": 1318.04,
                    "profit": 0.0,
                    "comment": "QQ[XAUUSD]1234[T1/S01]",
                },
                {
                    "time": pd.Timestamp("2018-01-02 22:55:00"),
                    "deal": 6,
                    "order": 6,
                    "symbol": "XAUUSD",
                    "type": "sell",
                    "entry": "out",
                    "volume": 0.2,
                    "price": 1318.23,
                    "profit": 40.8,
                    "comment": None,
                },
                {
                    "time": pd.Timestamp("2018-01-02 23:14:00"),
                    "deal": 7,
                    "order": 7,
                    "symbol": "XAUUSD",
                    "type": "sell",
                    "entry": "out",
                    "volume": 0.2,
                    "price": 1318.76,
                    "profit": 14.4,
                    "comment": None,
                },
            ]
        )

        positions = reconstruct_positions_fifo(deals)

        self.assertEqual(list(positions["entry_deal"]), [2, 3, 5])
        self.assertEqual(list(positions["exit_deal"]), [4, 6, 7])
        self.assertEqual(list(positions["strategy"]), ["T1/S01", "T5/S10", "T1/S01"])
        self.assertAlmostEqual(positions.loc[0, "pnl_est"], 14.6, places=6)
        self.assertAlmostEqual(positions.loc[1, "pnl_est"], 40.8, places=6)
        self.assertAlmostEqual(positions.loc[2, "pnl_est"], 14.4, places=6)

    def test_assign_baskets_groups_overlapping_positions_by_strategy_and_direction(self):
        positions = pd.DataFrame(
            [
                {
                    "position_id": 1,
                    "strategy": "T1/S01",
                    "direction": "long",
                    "entry_time": pd.Timestamp("2024-01-01 10:00:00"),
                    "exit_time": pd.Timestamp("2024-01-01 10:30:00"),
                    "volume": 0.1,
                    "pnl_est": 10.0,
                },
                {
                    "position_id": 2,
                    "strategy": "T1/S01",
                    "direction": "long",
                    "entry_time": pd.Timestamp("2024-01-01 10:15:00"),
                    "exit_time": pd.Timestamp("2024-01-01 10:45:00"),
                    "volume": 0.1,
                    "pnl_est": 5.0,
                },
                {
                    "position_id": 3,
                    "strategy": "T1/S01",
                    "direction": "long",
                    "entry_time": pd.Timestamp("2024-01-01 11:00:00"),
                    "exit_time": pd.Timestamp("2024-01-01 11:10:00"),
                    "volume": 0.1,
                    "pnl_est": 3.0,
                },
            ]
        )

        assigned, baskets = assign_baskets(positions)

        self.assertEqual(list(assigned["basket_id"]), [1, 1, 2])
        self.assertEqual(list(baskets["position_count"]), [2, 1])
        self.assertEqual(list(baskets["max_layers"]), [2, 1])
        self.assertEqual(list(baskets["pnl_est"]), [15.0, 3.0])


if __name__ == "__main__":
    unittest.main()
