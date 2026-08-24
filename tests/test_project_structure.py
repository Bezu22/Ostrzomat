import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class TestProjectStructure(unittest.TestCase):
    def test_expected_layers_exist(self):
        self.assertTrue((ROOT / "database.py").exists())
        self.assertTrue((ROOT / "logic").is_dir())
        self.assertTrue((ROOT / "ui").is_dir())
        self.assertTrue((ROOT / "utils").is_dir())

    def test_core_modules_import(self):
        import database
        import logic.cart_logic
        import logic.db_editor_logic

        self.assertTrue(hasattr(database, "get_connection"))
        self.assertTrue(hasattr(logic.cart_logic, "calculate_tool_price"))
        self.assertTrue(hasattr(logic.db_editor_logic, "save_record"))

    def test_ui_module_imports(self):
        from ui.main_window import OstrzomatApp
        self.assertTrue(callable(OstrzomatApp))


if __name__ == "__main__":
    unittest.main()
