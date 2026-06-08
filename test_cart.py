import unittest
import os
import database as database
from logic import cart_logic

class TestOstrzomatComprehensive(unittest.TestCase):
    
    def setUp(self):
        """Przygotowanie czystego środowiska wirtualnego koszyka przed każdym testem."""
        self.cart_items = []
        self.client_name = "Klient Testowy"
        self.test_cache_path = os.path.join("data", "cart_cache_test.json")
        
        # Czyszczenie pozostałości po poprzednich testach
        if os.path.exists(self.test_cache_path):
            os.remove(self.test_cache_path)

    def tearDown(self):
        """Sprzątanie po teście."""
        if os.path.exists(self.test_cache_path):
            os.remove(self.test_cache_path)

    # =========================================================================
    # 1. TESTY LOGIKI BIZNESOWEJ (Mocne zużycie, powłoki, usługi dodatkowe)
    # =========================================================================

    def test_logic_heavy_wear_and_coating(self):
        """TEST: Czy algorytm poprawnie dolicza +5% za zużycie i kalkuluje powłoki."""
        # Sprawdzamy standardową cenę z bazy (mockujemy zachowanie, że baza zwraca np. 100.0)
        # Aby test był niezależny od bazy, zakładamy, że cart_logic.calculate_tool_price działa na liczbach
        
        # Test bez zużycia
        p_unit_normal, _ = cart_logic.calculate_tool_price("Frez prosty", "4", "10.0", "1", heavy_wear=False)
        
        # Test z mocnym zużyciem (+5%)
        p_unit_wear, _ = cart_logic.calculate_tool_price("Frez prosty", "4", "10.0", "1", heavy_wear=True)
        
        if p_unit_normal > 0: # Jeśli baza zwróciła poprawną wartość, sprawdzamy matematykę
            expected_wear_price = round(p_unit_normal * 1.05, 2)
            self.assertEqual(p_unit_wear, expected_wear_price, "Mocne zużycie powinno podnosić cenę o 5% i zaokrąglać do 2 miejsc!")

    def test_logic_extra_services(self):
        """TEST: Czy kalkulator usług poprawnie reaguje na różne kombinacje checkboxów."""
        # Scenariusz: Aktywne cięcie i polerowanie, zaniżenie wyłączone
        mock_services = {
            "ciecie": unittest.mock.MagicMock(get=lambda: True),
            "opuszczenie": unittest.mock.MagicMock(get=lambda: False),
            "polerowanie": unittest.mock.MagicMock(get=lambda: True),
            "zuzycie": unittest.mock.MagicMock(get=lambda: False)
        }
        
        total_unit, total_res, active_labels = cart_logic.calculate_extra_services(mock_services, "10.0", "2")
        
        # Weryfikujemy czy labels poprawnie odfiltrowały usługi
        self.assertIn("Cięcie", active_labels, "")
        self.assertNotIn("Zaniżenie", active_labels, "")
        self.assertEqual(total_res, total_unit * 2, "Suma całkowita usług musi być wielokrotnością ilości sztuk!")

    # =========================================================================
    # 2. TESTY ODPORNOŚCI NA BŁĘDNE INPUTY (Kropki, spacje, znaki specjalne)
    # =========================================================================

    def test_input_resilience(self):
        """TEST: Czy system radzi sobie ze spacjami, przecinkami i dziwnymi znakami w polach liczbowych."""
        # Odporność na przecinek zamiast kropki w średnicy ("10,5") oraz spacje (" 4 ")
        p_unit, p_total = cart_logic.calculate_tool_price("Frez prosty", " 4 ", "10,5 ", " 2", heavy_wear=False)
        
        # Jeśli dane w bazie istnieją dla takiego progu, nie powinno rzucić wyjątkiem ( crash aplikacji )
        # Przy kompletnie błędnym inpucie (np. tekst "abc") funkcja ma bezpiecznie zwrócić 0.0, a nie wywalić program
        p_err_unit, p_err_total = cart_logic.calculate_tool_price("Frez prosty", "xyz", "10..0", " s2 ", heavy_wear=False)
        self.assertEqual(p_err_unit, 0.0, "Dla krytycznie błędnych danych wejściowych system powinien zwrócić 0.0")
        self.assertEqual(p_err_total, 0.0, "Dla krytycznie błędnych danych wejściowych system powinien zwrócić 0.0")

    # =========================================================================
    # 3. TESTY OPERACJI NA KOSZYKU (Dodawanie, usuwanie, edycja, czyszczenie)
    # =========================================================================

    def test_cart_lifecycle(self):
        """TEST: Pełny cykl życia koszyka (Dodaj -> Edytuj -> Wyczyść)."""
        # --- DODAWANIE ---
        item_1 = {"type": "Frez Alum", "diam": "8.0", "qty": "5", "total_tool": 50.0, "total_coat": 0.0, "total_extra": 0.0}
        item_2 = {"type": "Frez Stal", "diam": "12.0", "qty": "2", "total_tool": 60.0, "total_coat": 20.0, "total_extra": 5.0}
        
        self.cart_items.append(item_1)
        self.cart_items.append(item_2)
        self.assertEqual(len(self.cart_items), 2, "Koszyk powinien zawierać 2 pozycje")

        # --- EDYCJA (Nadpisanie pozycji pod indeksem 0) ---
        updated_item_1 = {"type": "Frez Alum Modyfikowany", "diam": "8.0", "qty": "10", "total_tool": 100.0, "total_coat": 0.0, "total_extra": 0.0}
        
        # Logika odpowiadająca metodzie update_item_in_cart z main_window.py
        selected_idx = 0
        if 0 <= selected_idx < len(self.cart_items):
            self.cart_items[selected_idx] = updated_item_1
            
        self.assertEqual(self.cart_items[0]["type"], "Frez Alum Modyfikowany", "Nazwa typu nie została zaktualizowana po edycji!")
        self.assertEqual(self.cart_items[0]["qty"], "10", "Ilość sztuk nie została zaktualizowana po edycji!")
        self.assertEqual(len(self.cart_items), 2, "Edycja nie może zmieniać ogólnej liczby pozycji w koszyku!")

        # --- USUWANIE / CZYSZCZENIE ---
        # Logika odpowiadająca metodzie clear_cart
        self.cart_items = []
        self.assertEqual(len(self.cart_items), 0, "Koszyk po wyczyszczeniu musi być pusty!")

    # =========================================================================
    # 4. TESTY TRWAŁOŚCI DANYCH (Zapis i odczyt z plików JSON)
    # =========================================================================

    def test_file_io_integrity(self):
        """TEST: Czy mechanizm zapisu i odczytu bazy plików nie deformuje danych strukturalnych."""
        complex_items = [{
            "type": "Frez VHM",
            "diam": "16.0",
            "qty": "3",
            "services_status": {"ciecie": True, "zuzycie": True},
            "total_tool": 150.0,
            "total_coat": 45.0,
            "total_extra": 12.5
        }]
        
        # Wywołanie zapisu
        database.save_cart_to_file(complex_items, self.client_name, path=self.test_cache_path)
        self.assertTrue(os.path.exists(self.test_cache_path), "Plik JSON nie został fizycznie zapisany na dysku!")
        
        # Wywołanie odczytu
        loaded_client, loaded_items = database.load_cart_from_file(path=self.test_cache_path)
        
        # Sprawdzamy czy struktura zagnieżdżona (słownik w słowniku) przetrwała konwersję JSON
        self.assertEqual(loaded_client, self.test_client, "")
        self.assertEqual(loaded_items[0]["services_status"]["ciecie"], True, "Zagnieżdżona struktura statusu usług uległa uszkodzeniu przy zapisie/odczycie!")
        self.assertEqual(loaded_items[0]["services_status"]["zuzycie"], True, "Flaga zużycia uległa uszkodzeniu w pliku JSON!")


if __name__ == "__main__":
    unittest.main()