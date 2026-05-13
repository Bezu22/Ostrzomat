import database as database

def calculate_tool_price(t_type, blades, diam, qty):
    """Logika obliczania ostrzenia - JEDYNE miejsce walidacji."""
    try:
        # Konwersja surowych danych na typy liczbowe
        b_val = int(blades)
        d_val = float(str(diam).replace(',', '.'))
        q_val = int(qty)
        
        # Logika biznesowa (progi ostrzy)
        b_key = "2-4" if 2 <= b_val <= 4 else "pozostałe"
        
        # Zapytanie do bazy
        p_unit = database.get_tool_price(t_type, b_key, d_val, q_val)
        return p_unit, p_unit * q_val
    except Exception as e:
        print(f"Błąd logiki ostrzenia: {e}")
        return 0.0, 0.0

def calculate_extra_services(service_vars, diam, qty):
    """Oblicza sumę usług dodatkowych (Cięcie, Zaniżenie, Polerowanie)."""
    try:
        d_val = float(str(diam).replace(',', '.'))
        q_val = int(qty)
        total_unit = 0.0
        active_labels = []
        
        # Mapowanie kluczy na nazwy w bazie
        mapping = {
            "ciecie": ("Cięcie", "Cięcie"),
            "opuszczenie": ("Zaniżenie", "Zaniżenie średnicy"),
            "polerowanie": ("Polerowanie", "Polerowanie rowka")
        }

        for key, (label, db_name) in mapping.items():
            if service_vars.get(key) and service_vars[key].get():
                price = database.get_service_price_refined(db_name, d_val)
                total_unit += price
                active_labels.append(label)
        
        return total_unit, total_unit * q_val, active_labels
    except:
        return 0.0, 0.0, []

def calculate_coating_price(coating, diam, length, qty):
    """Oblicza cenę powłoki, przyjmując 4 wymagane argumenty."""
    try:
        if coating == "Brak" or not coating:
            return 0.0, 0.0
        
        # Wywołanie funkcji z database.py (tej z Twoimi printami)
        p_unit = database.get_coating_price(coating, diam, length)
        
        q_val = int(qty)
        return p_unit, p_unit * q_val
    except Exception as e:
        print(f"Błąd w cart_logic (coating): {e}") # Dodaj ten print!
        return 0.0, 0.0