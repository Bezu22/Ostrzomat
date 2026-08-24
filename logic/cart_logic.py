import database as database


def calculate_tool_price(tool_type, blades, diam, qty, heavy_wear=False, heavy_wear_qty=0, **kwargs):
    """
    Oblicza cenę jednostkową bazową oraz łączną dla narzędzia.
    Obsługuje zarówno nowy format z heavy_wear_qty, jak i starszy z bool heavy_wear.
    """
    try:
        d_val = float(str(diam).replace(',', '.').strip())
        q_val = int(str(qty).strip())

        if isinstance(heavy_wear, str):
            heavy_wear = heavy_wear.strip().lower() in {"1", "true", "yes", "y", "tak"}

        if heavy_wear:
            hw_qty = q_val
        else:
            hw_qty = int(str(heavy_wear_qty).strip()) if heavy_wear_qty else 0

        if d_val <= 0.0 or q_val <= 0:
            return 0.0, 0.0

    except (ValueError, TypeError):
        return 0.0, 0.0

    base_price = database.get_tool_price(tool_type, blades, d_val, q_val)

    if base_price <= 0.0:
        return 0.0, 0.0

    hw_qty = min(max(hw_qty, 0), q_val)
    normal_qty = q_val - hw_qty

    total_price = (normal_qty * base_price) + (hw_qty * base_price * 1.05)
    unit_avg = total_price / q_val if q_val > 0 else base_price

    return round(unit_avg, 2), round(total_price, 2)


def calculate_extra_services(services_vars, services_qty, diam=None, total_qty=None, opuszczenie_multiplier=1):
    """
    Oblicza sumaryczną cenę usług dodatkowych.
    Obsługuje oba style API:
    - nowy: calculate_extra_services(services_vars, services_qty, diam, total_qty, ...)
    - stary: calculate_extra_services(services_vars, diam, total_qty)
    """
    if total_qty is None and diam is not None and isinstance(services_qty, (str, int, float)):
        total_qty = diam
        diam = services_qty
        services_qty = {}

    try:
        d_val = float(str(diam).replace(',', '.'))
        tot_q = int(total_qty)
    except (TypeError, ValueError):
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

                s_qty = tot_q
                if isinstance(services_qty, dict):
                    s_qty = int(services_qty.get(key, tot_q))
                s_qty = min(max(s_qty, 0), tot_q)

                service_total_cost = unit_service_price * s_qty
                total_extra_sum += service_total_cost

                active_labels.append(db_name)

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