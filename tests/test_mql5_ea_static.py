from pathlib import Path
import unittest


PROJECT = Path(__file__).resolve().parents[1]
EA_PATH = PROJECT / "mql5" / "Experts" / "QuantumQueenApproxNonRisky.mq5"


class Mql5EaStaticTests(unittest.TestCase):
    def test_ea_contains_only_selected_matched_context_strategies(self):
        source = EA_PATH.read_text(encoding="utf-8")

        for strategy in ["T1/S01", "T2/S03", "T2/S04", "T4/S08", "T5/S09"]:
            self.assertIn(strategy, source)
        for excluded in ["T3/S06", "T5/S10", "T6/S12"]:
            self.assertNotIn(f'Name = "{excluded}"', source)
        self.assertIn("UseS01", source)
        self.assertIn("UseS09", source)

    def test_ea_contains_compounding_lot_and_basket_management_logic(self):
        source = EA_PATH.read_text(encoding="utf-8")

        self.assertIn("BalancePer001Lot", source)
        self.assertIn("MathFloor(balance / BalancePer001Lot) * 0.01", source)
        self.assertIn("BasketVwap", source)
        self.assertIn("MaybeOpenAddOn", source)
        self.assertIn("MaybeCloseBasket", source)

    def test_ea_contains_required_matched_context_indicators(self):
        source = EA_PATH.read_text(encoding="utf-8")

        for function_name in ["CCI", "ADXMain", "DIPlus", "DIMinus", "SMA", "EMA", "WMA", "ROC", "CMO", "CHOP"]:
            self.assertIn(function_name, source)
        self.assertNotIn("Fisher", source)


if __name__ == "__main__":
    unittest.main()
