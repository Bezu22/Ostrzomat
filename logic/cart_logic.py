import database as database

def calculate_tool_price(t_type, blades, diam, qty, heavy_wear=False):
    """Logika obliczania ostrzenia z obsługą parametru mocnego zużycia."""
    try:
        b_val = int(blades)
        d_val = float(str(diam).replace(',', '.'))
        q_val = int(qty)
        
        b_key = "2-4" if 2 <= b_val <= 4 else "pozostałe"
        
        p_unit = database.get_tool_price(t_type, b_key, d_val, q_val)
        
        # DODATKOWA LOGIKA BIZNESOWA: Mocne zużycie (+5%)
        if heavy_wear:
            p_unit = round(p_unit * 1.05, 2)
            
        return p_unit, p_unit * q_val
    except Exception as e:
        print(f"Błąd logiki ostrzenia: {e}")
        return 0.0, 0.0

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