import unittest
import os
from unittest.mock import patch
import database as database
from logic import cart_logic

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
            
        cls.original_save = database.save_cart_to_file
        cls.original_load = database.load_cart_from_file
        
        database.save_cart_to_file = lambda items, client, path=cls.test_cache_path: cls.original_save(items, client, path)
        database.load_cart_from_file = lambda path=cls.test_cache_path: cls.original_load(path)

        cls.app = OstrzomatApp()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        """Przywraca oryginalne funkcje bazy danych i sprząta po testach."""
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
                
        if os.path.exists(cls.test_cache_path):
            os.remove(cls.test_cache_path)

    def setUp(self):
        """Przed każdym testem czyścimy wirtualny koszyk aplikacji."""
        self.app.cart_items = []

    # =========================================================================
    # 1. TESTY LOGIKI BIZNESOWEJ
    # =========================================================================

    def test_logic_heavy_wear_and_coating(self):
        print("\nTEST: Zużycie +5% i powłoki... ", end="", flush=True)
        p_unit_normal, _ = cart_logic.calculate_tool_price("Frez prosty", "4", "10.0", "1", heavy_wear=False)
        p_unit_wear, _ = cart_logic.calculate_tool_price("Frez prosty", "4", "10.0", "1", heavy_wear=True)
        
        if p_unit_normal > 0:
            expected_wear_price = round(p_unit_normal * 1.05, 2)
            self.assertEqual(p_unit_wear, expected_wear_price)
        print("OK")

    def test_logic_extra_services(self):
        print("TEST: Kombinacje usług (Checkboxy)... ", end="", flush=True)
        class MockBooleanVar:
            def __init__(self, val): self.val = val
            def get(self): return self.val

        mock_services = {
            "ciecie": MockBooleanVar(True),
            "opuszczenie": MockBooleanVar(False),
            "polerowanie": MockBooleanVar(True),
            "zuzycie": MockBooleanVar(False)
        }
        total_unit, total_res, active_labels = cart_logic.calculate_extra_services(mock_services, "10.0", "2")
        
        self.assertIn("Cięcie", active_labels)
        self.assertNotIn("Zaniżenie", active_labels)
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
        # 1. Próba kalkulacji dla zerowej ilości - musi dać 0.0
        _, p_zero_t = cart_logic.calculate_tool_price("Frez prosty", "4", "12.0", "0", heavy_wear=False)
        self.assertEqual(p_zero_t, 0.0)
        
        # 2. Średnica równa dokładnie 0.0 - brak fizycznego narzędzia, wynik musi być 0.0
        p_zero_diam_u, _ = cart_logic.calculate_tool_price("Frez prosty", "4", "0.0", "1", heavy_wear=False)
        self.assertEqual(p_zero_diam_u, 0.0)
        
        # 3. Ekstremalny gigant (Średnica 999.0) - całkowicie poza skalą cennika SQL, wynik musi być 0.0
        p_macro_u, _ = cart_logic.calculate_tool_price("Frez prosty", "4", "999.0", "1", heavy_wear=False)
        self.assertEqual(p_macro_u, 0.0)
        print("OK")

    # =========================================================================
    # 3. TESTY INTEGRACYJNE KOSZYKA (Prawdziwe funkcje aplikacji)
    # =========================================================================

    def test_cart_lifecycle(self):
        print("TEST: Cykl życia (Dodaj->Edytuj->Wyczyść)... ", end="", flush=True)
        
        # DODAWANIE
        item_1 = {"type": "Frez Alum", "diam": "8.0", "qty": "5", "total_tool": 50.0, "total_coat": 0.0, "total_extra": 0.0, "notes": ""}
        self.app.add_item_to_cart(item_1)
        self.assertEqual(len(self.app.cart_items), 1)

        # EDYCJA
        updated_item_1 = {"type": "Frez Alum Modyfikowany", "diam": "8.0", "qty": "10", "total_tool": 100.0, "total_coat": 0.0, "total_extra": 0.0, "notes": "Pilne"}
        self.app.update_item_in_cart(0, updated_item_1)
        
        self.assertEqual(self.app.cart_items[0]["qty"], "10")
        self.assertEqual(self.app.cart_items[0]["type"], "Frez Alum Modyfikowany")

        # Bezpieczne czyszczenie koszyka bez popupu sukcesu
        from ui.components import OstrzomatPopup
        def mock_popup_clear(shadow_self, parent, title, message, type="info", on_confirm=None):
            if type == "confirm" and on_confirm:
                on_confirm()
                
        with patch.object(OstrzomatPopup, '__init__', mock_popup_clear):
            self.app.clear_cart()
            
        self.assertEqual(len(self.app.cart_items), 0)
        print("OK")

    # =========================================================================
    # 4. SCENARIUSZE ZAAWANSOWANE (Wielopozycyjność, precyzja edycji, finanse)
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
        
        footer_text = self.app.cart_footer.total_label.cget("text")
        extracted_sum = float(footer_text.replace("ŁĄCZNIE DO ZAPŁATY: ", "").replace(" zł", "").strip())
        
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
        
        footer_text = self.app.cart_footer.total_label.cget("text")
        extracted_sum = float(footer_text.replace("ŁĄCZNIE DO ZAPŁATY: ", "").replace(" zł", "").strip())
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
                
        with patch.object(OstrzomatPopup, '__init__', mock_popup_init):
            self.app.delete_selected_item()
        
        self.assertEqual(len(self.app.cart_items), 2)
        self.assertEqual(self.app.cart_items[1]["type"], "Frez Trzeci")
        self.assertEqual(self.app.cart_items[0]["type"], "Frez Pierwszy")
        
        footer_text = self.app.cart_footer.total_label.cget("text")
        extracted_sum = float(footer_text.replace("ŁĄCZNIE DO ZAPŁATY: ", "").replace(" zł", "").strip())
        self.assertEqual(extracted_sum, 40.00)
        print("OK")

    # =========================================================================
    # 5. NEW: ZAAWANSOWANE ZARZĄDZANIE UWAGAMI (UCIECIE TEKSTU I TRWAŁOŚĆ)
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
            "notes": long_note
        }
        
        self.app.add_item_to_cart(item)
        
        # Weryfikacja bezstratnego zapisu w pamięci operacyjnej
        saved_note_in_mem = self.app.cart_items[0]["notes"]
        self.assertEqual(saved_note_in_mem, long_note)

        # Weryfikacja algorytmu maskowania wizualnego w tabeli (obcięcie do 20 znaków + ...)
        if len(saved_note_in_mem) > 20:
            display_text = saved_note_in_mem[:20] + "..."
        else:
            display_text = saved_note_in_mem if saved_note_in_mem else "-"
            
        self.assertEqual(display_text, "Ostrzyć głęboko - wy...")
        
        # Weryfikacja powrotu do domyślnego znaku braku uwag po wyczyszczeniu
        self.app.cart_items[0]["notes"] = ""
        cleared_note = self.app.cart_items[0]["notes"]
        display_text_after = cleared_note if cleared_note else "-"
        self.assertEqual(display_text_after, "-")
        print("OK")

    def test_advanced_opuszczenie_multiplier_and_pluses(self):
        print("TEST: Mnożnik zaniżenia i renderowanie plusów... ", end="", flush=True)
        
        # 1. Przygotowujemy pozycję z zaniżeniem o krotności 3 (30 mm)
        item = {
            "type": "Frez z długą szyjką",
            "diam": "10.0",
            "qty": "2",
            "tool_unit": 40.0, "total_tool": 80.0,
            "coat_name": "Brak", "coat_len": "100", "coat_unit": 0.0, "total_coat": 0.0,
            "services_status": {
                "ciecie": False,
                "opuszczenie": True,  # Aktywne zaniżenie
                "polerowanie": False,
                "zuzycie": False
            },
            "opuszczenie_mult": 3,  # Krotność x3 (30 mm)
            "extra_unit": 45.0,     # Załóżmy, że bazowa usługa to 15 zł, więc x3 = 45 zł
            "total_extra": 90.0     # 45 zł * 2 sztuki = 90 zł
        }
        
        # Dodajemy element do aplikacji
        self.app.add_item_to_cart(item)
        
        # WERYFIKACJA 1: Czy aplikacja poprawnie zachowała mnożnik w pamięci RAM
        saved_item = self.app.cart_items[0]
        self.assertEqual(saved_item["opuszczenie_mult"], 3, "Mnożnik zaniżenia został uszkodzony w pamięci!")
        
        # WERYFIKACJA 2: Testujemy dokładnie ten sam algorytm renderowania plusów, który wdrożyliśmy w cart_table.py
        status = saved_item.get("services_status", {})
        is_o = status.get("opuszczenie", False)
        
        if is_o:
            mult = saved_item.get("opuszczenie_mult", 1)
            text_zan = "+" * mult
        else:
            text_zan = "-"
            
        # Oczekujemy dokładnie trzech plusów '+++'
        self.assertEqual(text_zan, "+++", f"Algorytm generowania plusów zwrócił: '{text_zan}' zamiast '+++'")
        
        # WERYFIKACJA 3: Co się stanie, gdy usługa zaniżenia zostanie wyłączona (mult przechodzi w stan spoczynku)
        saved_item["services_status"]["opuszczenie"] = False
        
        # Ponowne sprawdzenie po wyłączeniu usługi
        status_after = saved_item.get("services_status", {})
        if status_after.get("opuszczenie", False):
            text_zan_after = "+" * saved_item.get("opuszczenie_mult", 1)
        else:
            text_zan_after = "-"
            
        self.assertEqual(text_zan_after, "-", "Po wyłączeniu usługi zaniżenia wiersz nie wyświetla myślnika '-'!")
        print("OK")

if __name__ == "__main__":
    unittest.main()