import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

import database
from utils.price_list_excel import export_pricelist, import_pricelist


class TestPriceListExcel(unittest.TestCase):
    def test_excel_round_trip_supports_new_tool_range(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            db_path = temp_path / "ostrzomat.db"
            excel_path = temp_path / "cennik.xlsx"
            shutil.copy2(Path("data") / "ostrzomat.db", db_path)

            original_db_path = database.DB_PATH
            database.DB_PATH = str(db_path)
            try:
                export_pricelist(excel_path)
                workbook = load_workbook(excel_path)
                workbook["Narzędzia"].append(
                    ["Frezy", "Frez testowy", 1, 4, 20.1, 25.0, 80, 70, 60, 50]
                )
                workbook["Zakresy ilościowe"].append(
                    ["Frez testowy", 1, 4, 20.1, 25.0, 21, 30, 33]
                )
                workbook.save(excel_path)
                workbook.close()

                counts = import_pricelist(excel_path)
                self.assertGreater(counts["Narzędzia"], 0)
                self.assertGreater(counts["Zakresy ilościowe"], 0)
                self.assertEqual(
                    sqlite3.connect(db_path).execute(
                        "SELECT price FROM pricelist_tool_ranges WHERE tool_type=? "
                        "AND blades_min=? AND blades_max=? AND qty_min=? AND qty_max=?",
                        ("Frez testowy", 1, 4, 21, 30),
                    ).fetchone()[0],
                    33.0,
                )
                self.assertEqual(database.get_tool_price("Frez testowy", "4", 22, 25), 33.0)
                self.assertEqual(
                    sqlite3.connect(db_path).execute(
                        "SELECT COUNT(*) FROM pricelist_tools WHERE tool_type=?", ("Frez testowy",)
                    ).fetchone()[0],
                    1,
                )
            finally:
                database.DB_PATH = original_db_path

    def test_invalid_quantity_range_reports_cells_and_preserves_cache(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            db_path = temp_path / "ostrzomat.db"
            excel_path = temp_path / "cennik.xlsx"
            shutil.copy2(Path("data") / "ostrzomat.db", db_path)

            original_db_path = database.DB_PATH
            database.DB_PATH = str(db_path)
            try:
                export_pricelist(excel_path)
                workbook = load_workbook(excel_path)
                workbook["Zakresy ilościowe"]["F2"] = 30
                workbook["Zakresy ilościowe"]["G2"] = 20
                workbook.save(excel_path)
                workbook.close()

                before = sqlite3.connect(db_path).execute(
                    "SELECT COUNT(*) FROM pricelist_tool_ranges"
                ).fetchone()[0]
                with self.assertRaisesRegex(ValueError, r"Zakresy ilościowe!F2/G2"):
                    import_pricelist(excel_path)
                after = sqlite3.connect(db_path).execute(
                    "SELECT COUNT(*) FROM pricelist_tool_ranges"
                ).fetchone()[0]
                self.assertEqual(before, after)
            finally:
                database.DB_PATH = original_db_path

    def test_editing_standard_tool_price_is_not_hidden_by_quantity_sheet(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            db_path = temp_path / "ostrzomat.db"
            excel_path = temp_path / "cennik.xlsx"
            shutil.copy2(Path("data") / "ostrzomat.db", db_path)

            original_db_path = database.DB_PATH
            database.DB_PATH = str(db_path)
            try:
                export_pricelist(excel_path)
                workbook = load_workbook(excel_path)
                workbook["Narzędzia"]["G2"] = 999
                workbook.save(excel_path)
                workbook.close()

                import_pricelist(excel_path)
                self.assertEqual(database.get_tool_price("Frez prosty", "1", 5, 1), 999.0)
            finally:
                database.DB_PATH = original_db_path


if __name__ == "__main__":
    unittest.main()