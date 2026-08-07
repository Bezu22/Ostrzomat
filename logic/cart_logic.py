import database as database

def calculate_tool_price(tool_type, blades, diam, qty, heavy_wear=False):
    """
    Oblicza cenę jednostkową oraz łączną dla narzędzia.
    Gwarantuje powrót 0.0 dla nieprawidłowych danych (np. diam <= 0, qty <= 0).
    """
    try:
        # Konwersja i czyśczenie wprowadzonych danych
        d_val = float(str(diam).replace(',', '.').strip())
        q_val = int(str(qty).strip())
        
        # WALIDACJA WARTOŚCI BRZEGOWYCH:
        # Jeśli ilość lub średnica są równe 0 lub ujemne, cena musi wynosić 0.0
        if d_val <= 0.0 or q_val <= 0:
            return 0.0, 0.0

    except (ValueError, TypeError):
        # W przypadku podania tekstu zamiast liczby
        return 0.0, 0.0

    # Pobranie ceny bazowej z bazy danych
    base_price = database.get_tool_price(tool_type, blades, d_val, q_val)
    
    if base_price <= 0.0:
        return 0.0, 0.0

    # Doliczenie 5% w przypadku ciężkiego zużycia
    if heavy_wear:
        base_price = round(base_price * 1.05, 2)

    total_price = round(base_price * q_val, 2)
    return base_price, total_price

def calculate_extra_services(services_vars, diam, qty, opuszczenie_multiplier=1):
    """Oblicza sumaryczną cenę usług dodatkowych z uwzględnieniem mnożnika dla zaniżenia."""
    import database as database
    try:
        d_val = float(str(diam).replace(',', '.'))
        q_val = int(qty)
    except:
        return 0.0, 0.0, []

    total_unit = 0.0
    active_labels = []

    # Mapowanie techniczne nazw z bazy danych
    name_map = {
        "ciecie": "Cięcie",
        "opuszczenie": "Zaniżenie średnicy",
        "polerowanie": "Polerowanie rowka"
    }

    for key, var in services_vars.items():
        if key == "zuzycie":  # Zużycie to dopłata procentowa do ostrzenia, nie usługa stała
            continue
            
        if var.get():
            db_name = name_map.get(key)
            if db_name:
                price = database.get_service_price_refined(db_name, d_val)
                
                # Zastosowanie mnożnika wyłącznie dla usługi zaniżenia średnicy
                if key == "opuszczenie":
                    price = price * int(opuszczenie_multiplier)
                    label_suffix = f" (x{opuszczenie_multiplier})" if opuszczenie_multiplier > 1 else ""
                    active_labels.append(f"{db_name}{label_suffix}")
                else:
                    active_labels.append(db_name)
                    
                total_unit += price

    total_res = round(total_unit * q_val, 2)
    return round(total_unit, 2), total_res, active_labels

def calculate_coating_price(coating, diam, length, qty):
    try:
        if coating == "Brak" or not coating:
            return 0.0, 0.0
        p_unit = database.get_coating_price(coating, diam, length)
        q_val = int(qty)
        return p_unit, p_unit * q_val
    except Exception as e:
        print(f"Błąd w cart_logic (coating): {e}")
        return 0.0, 0.0