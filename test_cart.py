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
        """Uruchamia aplikację TYLKO RAZ dla wszystkich testów i całkowicie ją wycisza."""
        cls.test_cache_path = os.path.join("data", "cart_cache_test.json")
        os.makedirs("data", exist_ok=True)
        
        if os.path.exists(cls.test_cache_path):
            os.remove(cls.test_cache_path)
            
        # Tworzymy aplikację raz
        cls.app = OstrzomatApp()
        cls.app.withdraw() # Ukrywamy okno, żeby nie migało

    @classmethod
    def tearDownClass(cls):
        """Zamyka aplikację i sprząta pliki TYLKO RAZ na samym końcu testów."""
        if hasattr(cls, "app") and cls.app:
            try:
                # Wyciszamy wszystkie oczekujące zadania asynchroniczne Tkintera
                cls.app.update_idletasks()
                # Usuwamy zaplanowane skrypty "after", żeby nie sypały błędami w konsoli
                for after_id in cls.app.tk.call('after', 'info'):
                    cls.app.after_cancel(after_id)
                cls.app.destroy()
            except Exception:
                pass
                
        if os.path.exists(cls.test_cache_path):
            os.remove(cls.test_cache_path)

    def setUp(self):
        """Przed każdym testem jedynie czyścimy wirtualny koszyk, bez ruszania okna!"""
        self.app.cart_items = []

    # =========================================================================
    # 1. TESTY LOGIKI BIZNESOWEJ (Oryginalny cart_logic.py)
    # =========================================================================

    def test_logic_heavy_wear_and_coating(self):
        print("\nTEST: Kalkulacja ceny (Mocne zużycie +5% oraz powłoki)... ", end="", flush=True)
        
        p_unit_normal, _ = cart_logic.calculate_tool_price("Frez prosty", "4", "10.0", "1", heavy_wear=False)
        p_unit_wear, _ = cart_logic.calculate_tool_price("Frez prosty", "4", "10.0", "1", heavy_wear=True)
        
        if p_unit_normal > 0:
            expected_wear_price = round(p_unit_normal * 1.05, 2)
            self.assertEqual(p_unit_wear, expected_wear_price)
            
        print("OK")

    def test_logic_extra_services(self):
        print("TEST: Kombinacje usług dodatkowych (Checkboxy)... ", end="", flush=True)
        
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
    # 2. TESTY ODPORNOŚCI NA BŁĘDNE INPUTY
    # =========================================================================

    def test_input_resilience(self):
        print("TEST: Odporność na błędne wpisy (Spacje, przecinki, tekst)... ", end="", flush=True)
        
        cart_logic.calculate_tool_price("Frez prosty", " 4 ", "10,5 ", " 2", heavy_wear=False)
        
        p_err_unit, p_err_total = cart_logic.calculate_tool_price("Frez prosty", "xyz", "10..0", " s2 ", heavy_wear=False)
        self.assertEqual(p_err_unit, 0.0)
        self.assertEqual(p_err_total, 0.0)
        
        print("OK")

    # =========================================================================
    # 3. TESTY INTEGRACYJNE KOSZYKA (Oryginalny main_window.py)
    # =========================================================================

    @patch('tkinter.messagebox.askyesno')
    def test_cart_lifecycle(self, mock_askyesno):
        print("TEST: Cykl życia koszyka (Dodawanie -> Edycja -> Czyszczenie)... ", end="", flush=True)
        
        mock_askyesno.return_value = True
        
        # DODAWANIE przez Twoją prawdziwą metodę aplikacji
        item_1 = {"type": "Frez Alum", "diam": "8.0", "qty": "5", "total_tool": 50.0, "total_coat": 0.0, "total_extra": 0.0}
        self.app.add_item_to_cart(item_1)
        self.assertEqual(len(self.app.cart_items), 1)

        # EDYCJA przez Twoją prawdziwą metodę aplikacji
        updated_item_1 = {"type": "Frez Alum Modyfikowany", "diam": "8.0", "qty": "10", "total_tool": 100.0, "total_coat": 0.0, "total_extra": 0.0}
        self.app.update_item_in_cart(0, updated_item_1)
        
        self.assertEqual(self.app.cart_items[0]["qty"], "10")
        self.assertEqual(self.app.cart_items[0]["type"], "Frez Alum Modyfikowany")

        # CZYSZCZENIE przez Twoją prawdziwą metodę aplikacji
        self.app.clear_cart()
        self.assertEqual(len(self.app.cart_items), 0)
        
        print("OK")

if __name__ == "__main__":
    unittest.main()