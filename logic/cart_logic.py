import database as database

def calculate_tool_price(tool_type, blades, diam, qty, heavy_wear_qty=0):
    """
    Oblicza cenę jednostkową bazową oraz łączną dla narzędzia.
    Uwzględnia dopłatę 5% za ciężkie zużycie wyłącznie dla określonej liczby sztuk (heavy_wear_qty).
    """
    try:
        d_val = float(str(diam).replace(',', '.').strip())
        q_val = int(str(qty).strip())
        hw_qty = int(str(heavy_wear_qty).strip()) if heavy_wear_qty else 0
        
        if d_val <= 0.0 or q_val <= 0:
            return 0.0, 0.0

    except (ValueError, TypeError):
        return 0.0, 0.0

    # Pobranie ceny bazowej ostrzenia jednostkowego z bazy danych
    base_price = database.get_tool_price(tool_type, blades, d_val, q_val)
    
    if base_price <= 0.0:
        return 0.0, 0.0

    # Normalne sztuki (bez zużycia) + sztuki z dopłatą 5%
    hw_qty = min(hw_qty, q_val)
    normal_qty = q_val - hw_qty

    total_price = (normal_qty * base_price) + (hw_qty * base_price * 1.05)
    unit_avg = total_price / q_val if q_val > 0 else base_price

    return round(unit_avg, 2), round(total_price, 2)

def calculate_extra_services(services_vars, services_qty, diam, total_qty, opuszczenie_multiplier=1):
    """
    Oblicza sumaryczną cenę usług dodatkowych z uwzględnieniem indywidualnej liczby sztuk dla każdej usługi.
    """
    try:
        d_val = float(str(diam).replace(',', '.'))
        tot_q = int(total_qty)
    except:
        return 0.0, 0.0, []

    total_extra_sum = 0.0
    active_labels = []

    name_map = {
        "ciecie": "Cięcie",
        "opuszczenie": "Zaniżenie średnicy",
        "polerowanie": "Polerowanie rowka"
    }

    for key, var in services_vars.items():
        if key == "zuzycie":
            continue
            
        if var.get():
            db_name = name_map.get(key)
            if db_name:
                unit_service_price = database.get_service_price_refined(db_name, d_val)
                
                if key == "opuszczenie":
                    unit_service_price *= int(opuszczenie_multiplier)
                
                # Pobranie liczby sztuk przypisanej do tej usługi
                s_qty = int(services_qty.get(key, tot_q))
                s_qty = min(s_qty, tot_q) # Zabezpieczenie przed wpisaniem wartości większej niż łączna ilość

                service_total_cost = unit_service_price * s_qty
                total_extra_sum += service_total_cost

                active_labels.append(f"{db_name} ({s_qty} szt.)")

    extra_unit_avg = total_extra_sum / tot_q if tot_q > 0 else 0.0
    return round(extra_unit_avg, 2), round(total_extra_sum, 2), active_labels

def calculate_coating_price(coating, diam, length, qty):
    try:
        if coating == "Brak" or not coating:
            return 0.0, 0.0
        p_unit = database.get_coating_price(coating, diam, length)
        q_val = int(qty)
        return p_unit, round(p_unit * q_val, 2)
    except Exception as e:
        print(f"Błąd w cart_logic (coating): {e}")
        return 0.0, 0.0