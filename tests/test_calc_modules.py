import unittest
import customtkinter as ctk

from ui.calc_modules.base_module import BaseToolModule
from ui.calc_modules.frez_module import FrezModule
from ui.calc_modules.drill_module import DrillModule
from ui.calc_modules.special_module import SpecialModule


class TestCalcModules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Tworzymy niewidoczne okno nadrzędne dla widgetów Tkinter
        cls.root = ctk.CTk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_calculate_shank_value_even_rounding(self):
        """Weryfikuje regułę automatycznego zaokrąglania chwytu do parzystych wartości."""
        self.assertEqual(BaseToolModule.calculate_shank_value("5.0"), "6")
        self.assertEqual(BaseToolModule.calculate_shank_value("6.0"), "6")
        self.assertEqual(BaseToolModule.calculate_shank_value("6.1"), "8")
        self.assertEqual(BaseToolModule.calculate_shank_value("10"), "10")
        self.assertEqual(BaseToolModule.calculate_shank_value("11.5"), "12")
        self.assertEqual(BaseToolModule.calculate_shank_value(""), "")
        self.assertEqual(BaseToolModule.calculate_shank_value("-2"), "")

    def test_frez_module_data_structure(self):
        """Weryfikuje strukturę danych wyjściowych dla modułu FrezModule."""
        dummy_cb = lambda: None
        settings = {}
        module = FrezModule(self.root, dummy_cb, settings)

        data = module.get_full_item_data(run_validation=False)
        self.assertIsInstance(data, dict)
        self.assertIn("type", data)
        self.assertIn("diam", data)
        self.assertIn("shank_diam", data)
        self.assertIn("z", data)
        self.assertIn("qty", data)
        self.assertIn("tool_unit", data)
        self.assertIn("total_tool", data)
        self.assertIn("coat_name", data)
        self.assertIn("services_status", data)
        self.assertIn("services_qty", data)
        module.destroy()

    def test_drill_module_standard_and_step(self):
        """Weryfikuje obsługę wierteł standardowych oraz stopniowych."""
        dummy_cb = lambda: None
        settings = {}
        module = DrillModule(self.root, dummy_cb, settings)

        self.assertFalse(module.is_step_drill())
        data_std = module.get_full_item_data(run_validation=False)
        self.assertIsInstance(data_std, dict)

        # Ustawienie typu na wiertło stopniowe
        if "Wiertła stopniowe" in module.type_combo.cget("values"):
            module.type_combo.set("Wiertła stopniowe")
        elif "Wiertło stopniowe" in module.type_combo.cget("values"):
            module.type_combo.set("Wiertło stopniowe")
        else:
            module.type_combo.set("Wiertło stopniowe")

        module._on_type_change()
        self.assertTrue(module.is_step_drill())
        self.assertGreater(len(module.step_entries), 0)

        data_step = module.get_full_item_data(run_validation=False)
        self.assertIsInstance(data_step, dict)
        self.assertIn("/", data_step["diam"])
        module.destroy()

    def test_special_module_manual_price(self):
        """Weryfikuje poprawne naliczanie ceny ręcznej w module SpecialModule."""
        dummy_cb = lambda: None
        settings = {}
        module = SpecialModule(self.root, dummy_cb, settings)

        module.unit_price_entry.delete(0, "end")
        module.unit_price_entry.insert(0, "150.00")
        module.qty_entry.delete(0, "end")
        module.qty_entry.insert(0, "3")

        data = module.get_full_item_data(run_validation=False)
        self.assertEqual(data["tool_unit"], 150.0)
        self.assertEqual(data["total_tool"], 450.0)
        module.destroy()


if __name__ == "__main__":
    unittest.main()
