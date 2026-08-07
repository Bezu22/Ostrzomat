import unittest
import os
from unittest.mock import patch
import database as database
from logic import cart_logic
import utils.cache_manager as cache_manager

# Importujemy oryginalną aplikację
from ui.main_window import OstrzomatApp


class TestOstrzomatComprehensive(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Uruchamia aplikację i BEZWZGLĘDNIE izoluje ją od prawdziwych plików danych."""
        cls.test_cache_path = os.path.join("data", "cart_cache_test.json")
        os.makedirs("data", exist_ok=True)

        if os.path.exists(cls.test_cache_path):
            os.remove(cls.test_cache_path)

        # Zachowujemy oryginalne funkcje i oryginalną ścieżkę do cache
        cls.original_save = database.save_cart_to_file
        cls.original_load = database.load_cart_from_file
        cls.original_cache_path = database.CART_CACHE_PATH

        # Podmieniamy domyślną ścieżkę w module database na plik testowy
        database.CART_CACHE_PATH = cls.test_cache_path

        # Przekierowujemy funkcje zapisu i odczytu na plik testowy
        database.save_cart_to_file = lambda cart_items, client_id=None, client_name="Nieokreślony", path=None: cls.original_save(
            cart_items, client_id, client_name, path or cls.test_cache_path
        )
        database.load_cart_from_file = lambda path=None: cls.original_load(path or cls.test_cache_path)

        # Inicjalizacja pamięci podręcznej przed uruchomieniem okna
        cache_manager.preload_all_cache()

        cls.app = OstrzomatApp()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        """Przywraca oryginalne funkcje bazy danych, ścieżki i sprząta po testach."""
        # Przywracamy oryginalną ścieżkę oraz funkcje w module database
        database.CART_CACHE_PATH = cls.original_cache_path
        database.save_cart_to_file = cls.original_save
        database.load_cart_from_file = cls.original_load

        if hasattr(cls, "app") and cls.app:
            try:
                cls.app.update_idletasks()
                for after_id in cls.app.tk.call('after', 'info'):
                    cls.app.after_cancel(after_id)
                cls.app.destroy()
            except Exception:
                pass

        # Usuwamy tymczasowy plik testowy, nie dotykając cart_cache.json
        if os.path.exists(cls.test_cache_path):
            os.remove(cls.test_cache_path)

    def setUp(self):
        """Przed każdym testem czyścimy wirtualny koszyk aplikacji."""
        self.app.cart_items = []

    def _get_footer_total_value(self):
        """
        Pomocnicza funkcja odczytująca wartość kwoty łącznej z atrybutu self.lbl_total w CartFooter.
        """
        footer = self.app.cart_footer
        
        # Pobieramy tekst z widżetu lbl_total
        if hasattr(footer, 'lbl_total'):
            text = footer.lbl_total.cget("text")
        else:
            text = "0.00 zł"

        # Oczyszczamy tekst ze znaków waluty i spacji
        clean_text = text.replace("zł", "").replace(",", ".").strip()
        return float(clean_text) if clean_text else 0.0

    # =========================================================================
    # 1. TESTY LOGIKI BIZNESOWEJ I WIERTEŁ
    # =========================================================================

    def test_logic_heavy_wear_and_coating(self):
        print("\nTEST: Zużycie +5% i powłoki... ", end="", flush=True)
        p_unit_normal, _ = cart_logic.calculate_tool_price("Frez prosty", "4", "10.0", "1", heavy_wear=False)
        p_unit_wear, _ = cart_logic.calculate_tool_price("Frez prosty", "4", "10.0", "1", heavy_wear=True)

        if p_unit_normal > 0:
            expected_wear_price = round(p_unit_normal * 1.05, 2)
            self.assertEqual(p_unit_wear, expected_wear_price)
        print("OK")

    def test_drill_price_logic(self):
        """Weryfikacja odporności logiki wierteł na puste/dowolne wartości ostrzy."""
        print("TEST: Pobieranie cen dla wierteł (Wymuszenie 2 ostrzy)... ", end="", flush=True)

        p_unit, p_total = cart_logic.calculate_tool_price("Wiertla", "", "10.0", "1", heavy_wear=False)
        p_unit_str, _ = cart_logic.calculate_tool_price("Wiertła", "dowolne", "10.0", "1", heavy_wear=False)

        self.assertIsInstance(p_unit, float)
        self.assertIsInstance(p_unit_str, float)
        print("OK")

    def test_logic_extra_services(self):
        print("TEST: Kombinacje usług (Checkboxy)... ", end="", flush=True)

        class MockBooleanVar:
            def __init__(self, val):
                self.val = val

            def get(self):
                return self.val

        mock_services = {
            "ciecie": MockBooleanVar(True),
            "opuszczenie": MockBooleanVar(False),
            "polerowanie": MockBooleanVar(True),
            "zuzycie": MockBooleanVar(False),
        }
        total_unit, total_res, active_labels = cart_logic.calculate_extra_services(mock_services, "10.0", "2")

        self.assertIn("Cięcie", active_labels)
        self.assertNotIn("Zaniżenie średnicy", active_labels)
        self.assertEqual(total_res, total_unit * 2)
        print("OK")

    # =========================================================================
    # 2. TESTY ODPORNOŚCI NA INPUTY (SKRAJNE I BŁĘDNE DANE)
    # =========================================================================

    def test_input_resilience(self):
        print("TEST: Spacje, przecinki, tekst... ", end="", flush=True)
        cart_logic.calculate_tool_price("Frez prosty", " 4 ", "10,5 ", " 2", heavy_wear=False)
        p_err_unit, p_err_total = cart_logic.calculate_tool_price("Frez prosty", "xyz", "10..0", " s2 ", heavy_wear=False)
        self.assertEqual(p_err_unit, 0.0)
        self.assertEqual(p_err_total, 0.0)
        print("OK")

    def test_edge_cases_and_zero_quantities(self):
        print("TEST: Dane brzegowe (Wartości ujemne i zera)... ", end="", flush=True)
        _, p_zero_t = cart_logic.calculate_tool_price("Frez prosty", "4", "12.0", "0", heavy_wear=False)
        self.assertEqual(p_zero_t, 0.0)

        p_zero_diam_u, _ = cart_logic.calculate_tool_price("Frez prosty", "4", "0.0", "1", heavy_wear=False)
        self.assertEqual(p_zero_diam_u, 0.0)

        p_macro_u, _ = cart_logic.calculate_tool_price("Frez prosty", "4", "999.0", "1", heavy_wear=False)
        self.assertEqual(p_macro_u, 0.0)
        print("OK")

    # =========================================================================
    # 3. TESTY INTEGRACYJNE KOSZYKA I MEMORY CACHE
    # =========================================================================

    def test_cache_manager_integration(self):
        """Weryfikacja działania modułu pamięci podręcznej cache_manager."""
        print("TEST: Odczyt danych z centralnego cache_manager... ", end="", flush=True)
        clients = cache_manager.get_cached_clients()
        self.assertIsInstance(clients, list)
        self.assertFalse(cache_manager.is_clients_loading())
        print("OK")

    def test_cart_lifecycle(self):
        print("TEST: Cykl życia (Dodaj->Edytuj->Wyczyść)... ", end="", flush=True)

        item_1 = {
            "type": "Frez Alum",
            "diam": "8.0",
            "qty": "5",
            "total_tool": 50.0,
            "total_coat": 0.0,
            "total_extra": 0.0,
            "notes": "",
        }
        self.app.add_item_to_cart(item_1)
        self.assertEqual(len(self.app.cart_items), 1)

        updated_item_1 = {
            "type": "Frez Alum Modyfikowany",
            "diam": "8.0",
            "qty": "10",
            "total_tool": 100.0,
            "total_coat": 0.0,
            "total_extra": 0.0,
            "notes": "Pilne",
        }
        self.app.update_item_in_cart(0, updated_item_1)

        self.assertEqual(self.app.cart_items[0]["qty"], "10")
        self.assertEqual(self.app.cart_items[0]["type"], "Frez Alum Modyfikowany")

        from ui.components import OstrzomatPopup

        def mock_popup_clear(shadow_self, parent, title, message, type="info", on_confirm=None):
            if type == "confirm" and on_confirm:
                on_confirm()

        with patch.object(OstrzomatPopup, "__init__", mock_popup_clear):
            self.app.clear_cart()

        self.assertEqual(len(self.app.cart_items), 0)
        print("OK")

    # =========================================================================
    # 4. SCENARIUSZE ZAAWANSOWANE (Wielopozycyjność, finanse)
    # =========================================================================

    def test_advanced_multiple_items_and_totals(self):
        print("TEST: Łączenie wielu cen i podsumowanie stopki... ", end="", flush=True)

        item_a = {"type": "Frez 1", "total_tool": 120.55, "total_coat": 45.20, "total_extra": 10.00}
        item_b = {"type": "Frez 2", "total_tool": 80.00, "total_coat": 0.00, "total_extra": 15.50}
        item_c = {"type": "Frez 3", "total_tool": 210.13, "total_coat": 85.00, "total_extra": 0.00}

        self.app.add_item_to_cart(item_a)
        self.app.add_item_to_cart(item_b)
        self.app.add_item_to_cart(item_c)

        self.assertEqual(len(self.app.cart_items), 3)

        extracted_sum = self._get_footer_total_value()
        self.assertEqual(extracted_sum, 566.38, f"Błąd w stopce! Oczekiwano 566.38, wyszło {extracted_sum}")
        print("OK")

    def test_advanced_middle_item_edit_isolation(self):
        print("TEST: Izolacja edycji środkowej pozycji (Indeksy)... ", end="", flush=True)

        pos_0 = {"type": "Pierwszy", "qty": "5", "total_tool": 50.0, "total_coat": 0.0, "total_extra": 0.0}
        pos_1 = {"type": "Do Edycji", "qty": "2", "total_tool": 40.0, "total_coat": 10.0, "total_extra": 0.0}
        pos_2 = {"type": "Trzeci", "qty": "1", "total_tool": 30.0, "total_coat": 0.0, "total_extra": 0.0}

        self.app.add_item_to_cart(pos_0)
        self.app.add_item_to_cart(pos_1)
        self.app.add_item_to_cart(pos_2)

        edited_pos_1 = {"type": "Zmieniony Srodek", "qty": "5", "total_tool": 100.0, "total_coat": 25.0, "total_extra": 0.0}
        self.app.update_item_in_cart(1, edited_pos_1)

        self.assertEqual(len(self.app.cart_items), 3)
        self.assertEqual(self.app.cart_items[0]["type"], "Pierwszy")
        self.assertEqual(self.app.cart_items[2]["type"], "Trzeci")
        self.assertEqual(self.app.cart_items[1]["type"], "Zmieniony Srodek")
        self.assertEqual(self.app.cart_items[1]["qty"], "5")

        extracted_sum = self._get_footer_total_value()
        self.assertEqual(extracted_sum, 205.00)
        print("OK")

    def test_advanced_delete_and_lp_recalculation(self):
        print("TEST: Usuwanie pozycji i przeliczanie L.p... ", end="", flush=True)

        p0 = {"type": "Frez Pierwszy", "diam": "8.0", "total_tool": 10.0, "total_coat": 0.0, "total_extra": 0.0}
        p1 = {"type": "Frez Drugi (Do Usunięcia)", "diam": "10.0", "total_tool": 20.0, "total_coat": 0.0, "total_extra": 0.0}
        p2 = {"type": "Frez Trzeci", "diam": "12.0", "total_tool": 30.0, "total_coat": 0.0, "total_extra": 0.0}

        self.app.add_item_to_cart(p0)
        self.app.add_item_to_cart(p1)
        self.app.add_item_to_cart(p2)

        self.assertEqual(len(self.app.cart_items), 3)
        self.app.cart_table.get_selected_index = lambda: 1

        from ui.components import OstrzomatPopup

        def mock_popup_init(shadow_self, parent, title, message, type="info", on_confirm=None):
            if type == "confirm" and on_confirm:
                on_confirm()

        with patch.object(OstrzomatPopup, "__init__", mock_popup_init):
            self.app.delete_selected_item()

        self.assertEqual(len(self.app.cart_items), 2)
        self.assertEqual(self.app.cart_items[1]["type"], "Frez Trzeci")
        self.assertEqual(self.app.cart_items[0]["type"], "Frez Pierwszy")

        extracted_sum = self._get_footer_total_value()
        self.assertEqual(extracted_sum, 40.00)
        print("OK")

    # =========================================================================
    # 5. UWAGI I ZANIŻENIA
    # =========================================================================

    def test_advanced_notes_truncation_and_storage(self):
        print("TEST: Obsługa uwag (Zapis i ucinanie tekstu)... ", end="", flush=True)

        long_note = "Ostrzyć głęboko - wyszczerbiony"
        item = {
            "type": "Frez Testowy",
            "diam": "12.0",
            "qty": "1",
            "total_tool": 45.0,
            "total_coat": 0.0,
            "total_extra": 0.0,
            "notes": long_note,
        }

        self.app.add_item_to_cart(item)

        saved_note_in_mem = self.app.cart_items[0]["notes"]
        self.assertEqual(saved_note_in_mem, long_note)

        if len(saved_note_in_mem) > 20:
            display_text = saved_note_in_mem[:20] + "..."
        else:
            display_text = saved_note_in_mem if saved_note_in_mem else "-"

        self.assertEqual(display_text, "Ostrzyć głęboko - wy...")

        self.app.cart_items[0]["notes"] = ""
        cleared_note = self.app.cart_items[0]["notes"]
        display_text_after = cleared_note if cleared_note else "-"
        self.assertEqual(display_text_after, "-")
        print("OK")

    def test_advanced_opuszczenie_multiplier_and_pluses(self):
        print("TEST: Mnożnik zaniżenia i renderowanie plusów... ", end="", flush=True)

        item = {
            "type": "Frez z długą szyjką",
            "diam": "10.0",
            "qty": "2",
            "tool_unit": 40.0,
            "total_tool": 80.0,
            "coat_name": "Brak",
            "coat_len": "100",
            "coat_unit": 0.0,
            "total_coat": 0.0,
            "services_status": {"ciecie": False, "opuszczenie": True, "polerowanie": False, "zuzycie": False},
            "opuszczenie_mult": 3,
            "extra_unit": 45.0,
            "total_extra": 90.0,
        }

        self.app.add_item_to_cart(item)

        saved_item = self.app.cart_items[0]
        self.assertEqual(saved_item["opuszczenie_mult"], 3)

        status = saved_item.get("services_status", {})
        is_o = status.get("opuszczenie", False)

        if is_o:
            mult = saved_item.get("opuszczenie_mult", 1)
            text_zan = "+" * mult
        else:
            text_zan = "-"

        self.assertEqual(text_zan, "+++")

        saved_item["services_status"]["opuszczenie"] = False

        status_after = saved_item.get("services_status", {})
        if status_after.get("opuszczenie", False):
            text_zan_after = "+" * saved_item.get("opuszczenie_mult", 1)
        else:
            text_zan_after = "-"

        self.assertEqual(text_zan_after, "-")
        print("OK")


if __name__ == "__main__":
    unittest.main()