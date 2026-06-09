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
        """Przed każdym testem jedynie czyścimy wirtualny koszyk aplikacji."""
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
    # 2. TESTY ODPORNOŚCI NA INPUTY
    # =========================================================================

    def test_input_resilience(self):
        print("TEST: Spacje, przecinki, tekst... ", end="", flush=True)
        cart_logic.calculate_tool_price("Frez prosty", " 4 ", "10,5 ", " 2", heavy_wear=False)
        p_err_unit, p_err_total = cart_logic.calculate_tool_price("Frez prosty", "xyz", "10..0", " s2 ", heavy_wear=False)
        self.assertEqual(p_err_unit, 0.0)
        self.assertEqual(p_err_total, 0.0)
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

        # --- POPRAWKA MOCKA DLA CLEAR_CART ---
        from ui.components import OstrzomatPopup
        def mock_popup_clear(shadow_self, parent, title, message, type="info", on_confirm=None):
            if type == "confirm" and on_confirm:
                on_confirm() # Automatycznie zatwierdza czyszczenie koszyka w teście
                
        with patch.object(OstrzomatPopup, '__init__', mock_popup_clear):
            self.app.clear_cart()
            
        self.assertEqual(len(self.app.cart_items), 0)
        print("OK")

    # =========================================================================
    # NEW: 4. SCENARIUSZE ZAAWANSOWANE (Wielopozycyjność, precyzja edycji, finanse)
    # =========================================================================

    def test_advanced_multiple_items_and_totals(self):
        print("TEST: Łączenie wielu cen i podsumowanie stopki... ", end="", flush=True)
        
        # Wrzucamy 3 różne, skomplikowane cenowo pozycje
        item_a = {"type": "Frez 1", "total_tool": 120.55, "total_coat": 45.20, "total_extra": 10.00}
        item_b = {"type": "Frez 2", "total_tool": 80.00, "total_coat": 0.00, "total_extra": 15.50}
        item_c = {"type": "Frez 3", "total_tool": 210.13, "total_coat": 85.00, "total_extra": 0.00}
        
        self.app.add_item_to_cart(item_a)
        self.app.add_item_to_cart(item_b)
        self.app.add_item_to_cart(item_c)
        
        # Oczekiwana suma: 120.55+45.20+10.00 + 80.00+0.00+15.50 + 210.13+85.00+0.00 = 566.38
        self.assertEqual(len(self.app.cart_items), 3)
        
        # Pobieramy tekst z widżetu stopki, filtrujemy i sprawdzamy czy aplikacja dobrze policzyła total
        footer_text = self.app.cart_footer.total_label.cget("text")
        extracted_sum = float(footer_text.replace("ŁĄCZNIE DO ZAPŁATY: ", "").replace(" zł", "").strip())
        
        self.assertEqual(extracted_sum, 566.38, f"Błąd w stopce! Oczekiwano 566.38, wyszło {extracted_sum}")
        print("OK")

    def test_advanced_middle_item_edit_isolation(self):
        print("TEST: Izolacja edycji środkowej pozycji (Indeksy)... ", end="", flush=True)
        
        # Wrzucamy 3 pozycje
        pos_0 = {"type": "Pierwszy", "qty": "5", "total_tool": 50.0, "total_coat": 0.0, "total_extra": 0.0}
        pos_1 = {"type": "Do Edycji", "qty": "2", "total_tool": 40.0, "total_coat": 10.0, "total_extra": 0.0}
        pos_2 = {"type": "Trzeci", "qty": "1", "total_tool": 30.0, "total_coat": 0.0, "total_extra": 0.0}
        
        self.app.add_item_to_cart(pos_0)
        self.app.add_item_to_cart(pos_1)
        self.app.add_item_to_cart(pos_2)
        
        # Akcja: Edytujemy WYŁĄCZNIE element pod indeksem 1 (środkowy)
        edited_pos_1 = {"type": "Zmieniony Srodek", "qty": "5", "total_tool": 100.0, "total_coat": 25.0, "total_extra": 0.0}
        self.app.update_item_in_cart(1, edited_pos_1)
        
        # WERYFIKACJA 1: Czy struktura koszyka zachowała rozmiar 3
        self.assertEqual(len(self.app.cart_items), 3)
        
        # WERYFIKACJA 2: Czy sąsiednie pozycje (0 oraz 2) pozostały NIENARUSZONE (brak rozjechania indeksów)
        self.assertEqual(self.app.cart_items[0]["type"], "Pierwszy")
        self.assertEqual(self.app.cart_items[2]["type"], "Trzeci")
        
        # WERYFIKACJA 3: Czy środek przyjął nowe wartości
        self.assertEqual(self.app.cart_items[1]["type"], "Zmieniony Srodek")
        self.assertEqual(self.app.cart_items[1]["qty"], "5")
        
        # WERYFIKACJA 4: Czy stopka poprawnie przeliczyła nową wartość globalną
        # Pierwotna suma: 50 + 50 + 30 = 130
        # Nowa suma: 50 + 125 + 30 = 205
        footer_text = self.app.cart_footer.total_label.cget("text")
        extracted_sum = float(footer_text.replace("ŁĄCZNIE DO ZAPŁATY: ", "").replace(" zł", "").strip())
        self.assertEqual(extracted_sum, 205.00)
        
        print("OK")

    def test_advanced_delete_and_lp_recalculation(self):
        print("TEST: Usuwanie pozycji i przeliczanie L.p... ", end="", flush=True)
        
        # Wrzucamy 3 pozycje do koszyka aplikacji
        p0 = {"type": "Frez Pierwszy", "diam": "8.0", "total_tool": 10.0, "total_coat": 0.0, "total_extra": 0.0}
        p1 = {"type": "Frez Drugi (Do Usunięcia)", "diam": "10.0", "total_tool": 20.0, "total_coat": 0.0, "total_extra": 0.0}
        p2 = {"type": "Frez Trzeci", "diam": "12.0", "total_tool": 30.0, "total_coat": 0.0, "total_extra": 0.0}
        
        self.app.add_item_to_cart(p0)
        self.app.add_item_to_cart(p1)
        self.app.add_item_to_cart(p2)
        
        self.assertEqual(len(self.app.cart_items), 3)
        
        # 1. Wymuszamy, aby tabela zameldowała zaznaczenie indeksu 1 (L.p. 2)
        self.app.cart_table.get_selected_index = lambda: 1
        
        # 2. PANCERNY MOCK POPUPU: Przejmujemy kontrolę nad OstrzomatPopup w tym teście.
        # Gdy kod spróbuje stworzyć popup potwierdzający, ten mock automatycznie 
        # wyciągnie argument 'on_confirm' i od razu go wywoła (symulacja kliknięcia TAK)
        from ui.components import OstrzomatPopup
        
        def mock_popup_init(shadow_self, parent, title, message, type="info", on_confirm=None):
            if type == "confirm" and on_confirm:
                on_confirm()  # Wykonaj usuwanie natychmiast bez rysowania okna!
                
        with patch.object(OstrzomatPopup, '__init__', mock_popup_init):
            # Wywołujemy oryginalną funkcję usuwania z main_window.py
            self.app.delete_selected_item()
        
        # WERYFIKACJA 1: Koszyk musi mieć teraz długość 2
        self.assertEqual(len(self.app.cart_items), 2)
        
        # WERYFIKACJA 2: Sprawdzamy przesunięcie (dawny element 3 stał się elementem 2)
        self.assertEqual(self.app.cart_items[1]["type"], "Frez Trzeci")
        self.assertEqual(self.app.cart_items[0]["type"], "Frez Pierwszy")
        
        # WERYFIKACJA 3: Czy stopka poprawnie odliczyła kwotę (z 60.00 na 40.00)
        footer_text = self.app.cart_footer.total_label.cget("text")
        extracted_sum = float(footer_text.replace("ŁĄCZNIE DO ZAPŁATY: ", "").replace(" zł", "").strip())
        self.assertEqual(extracted_sum, 40.00)
        
        print("OK")

if __name__ == "__main__":
    unittest.main()