import sqlite3
import os
import json

# --- ŚCIEŻKI ---
DB_PATH = os.path.join('data', 'ostrzomat.db')
SETTINGS_PATH = os.path.join('data', 'user_settings.json')
CART_CACHE_PATH = os.path.join('data', 'cart_cache.json')

# Pamięć podręczna ustawień w RAM
_SETTINGS_CACHE = None

def is_db_accessible():
    return os.path.exists(DB_PATH)

def get_connection():
    if not is_db_accessible():
        raise FileNotFoundError(f"Brak bazy w {DB_PATH}")
    return sqlite3.connect(f"file:{DB_PATH}?mode=rw", uri=True)

# --- ZARZĄDZANIE USTAWIENIAMI (ZOPTOWANE - RAM CACHE) ---

def get_user_settings():
    global _SETTINGS_CACHE
    if _SETTINGS_CACHE is not None:
        return _SETTINGS_CACHE

    if not os.path.exists(SETTINGS_PATH):
        _SETTINGS_CACHE = {}
        return _SETTINGS_CACHE
    try:
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
            _SETTINGS_CACHE = json.load(f)
            return _SETTINGS_CACHE
    except:
        _SETTINGS_CACHE = {}
        return _SETTINGS_CACHE

def save_user_settings(new_settings, flush_to_disk=False):
    """Zapisuje ustawienia do RAM, a opcjonalnie na dysk."""
    global _SETTINGS_CACHE
    settings = get_user_settings()
    settings.update(new_settings)
    _SETTINGS_CACHE = settings
    
    # Zapis na dysk tylko gdy explicite wymuszony (np. przy zamknięciu okna)
    if flush_to_disk:
        try:
            if not os.path.exists('data'): os.makedirs('data')
            with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Błąd zapisu ustawień: {e}")

# --- FUNKCJE DLA FILTRÓW I CEN (BEZ ZMIAN W LOGICE) ---

def get_unique_tool_types(category="Wszystkie"):
    if not is_db_accessible(): return []
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if category == "Wszystkie":
            cursor.execute("SELECT DISTINCT tool_type FROM pricelist_tools")
        else:
            cursor.execute("SELECT DISTINCT tool_type FROM pricelist_tools WHERE category=?", (category,))
        types = [r[0] for r in cursor.fetchall()]
        conn.close()
        return types
    except: return []

def get_unique_coating_names():
    if not is_db_accessible(): return []
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT coating_name FROM pricelist_coatings")
        names = [r[0] for r in cursor.fetchall()]
        conn.close()
        return names
    except: return []

def get_unique_service_names():
    if not is_db_accessible(): return []
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT service_name FROM pricelist_services")
        names = [r[0] for r in cursor.fetchall()]
        conn.close()
        return names
    except: return []

def get_tool_price(tool_type, blades_key, diam, qty):
    if not is_db_accessible(): return 0.0
    try:
        d_val = float(diam)
        q_val = int(qty)
        
        conn = get_connection()
        cursor = conn.cursor()
        
        if q_val >= 11: price_col = "price_11_20"
        elif q_val >= 5: price_col = "price_5_10"
        elif q_val >= 2: price_col = "price_2_4"
        else: price_col = "price_1"

        query = f"""
            SELECT {price_col} FROM pricelist_tools 
            WHERE tool_type=? AND blades=? AND diam_min < ? AND diam_max >= ?
        """
        cursor.execute(query, (tool_type, blades_key, d_val, d_val))
        res = cursor.fetchone()
        conn.close()
        
        return float(res[0]) if (res and res[0] is not None) else 0.0
    except Exception as e:
        return 0.0

def get_unique_coating_lengths(coating_name):
    if not is_db_accessible(): return []
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if coating_name == "Brak" or coating_name is None:
            cursor.execute("SELECT DISTINCT length FROM pricelist_coatings ORDER BY length ASC")
        else:
            cursor.execute("SELECT DISTINCT length FROM pricelist_coatings WHERE coating_name=? ORDER BY length ASC", (coating_name,))
            
        lengths = [str(r[0]) for r in cursor.fetchall()]
        conn.close()
        return lengths
    except: return []

def get_coating_price(name, diam, length):
    if not is_db_accessible() or name == "Brak": return 0.0
    try:
        d_val = float(str(diam).replace(',', '.'))
        l_val = float(str(length).replace(',', '.'))
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT price FROM pricelist_coatings 
            WHERE coating_name=? AND diam_max >= ? AND length >= ?
            ORDER BY diam_max ASC, length ASC LIMIT 1
        """, (name, d_val, l_val))
        
        res = cursor.fetchone()
        conn.close()

        return float(res[0]) if res else 0.0
    except Exception as e:
        return 0.0

def get_service_price_refined(name, param_val):
    if not is_db_accessible(): return 0.0
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT price FROM pricelist_services 
            WHERE service_name=? AND param_min <= ? AND param_max >= ?
        """, (name, param_val, param_val))
        res = cursor.fetchone()
        conn.close()
        return float(res[0]) if res else 0.0
    except: return 0.0

def get_filtered_tools(tool_type="Wszystkie", category="Wszystkie"):
    if not is_db_accessible(): return []
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM pricelist_tools WHERE 1=1"
    params = []
    if tool_type != "Wszystkie":
        query += " AND tool_type=?"
        params.append(tool_type)
    if category != "Wszystkie":
        query += " AND category=?"
        params.append(category)
    cursor.execute(query, params)
    res = cursor.fetchall()
    conn.close()
    return res

def get_filtered_coatings(name="Wszystkie"):
    if not is_db_accessible(): return []
    conn = get_connection()
    cursor = conn.cursor()
    if name == "Wszystkie":
        cursor.execute("SELECT * FROM pricelist_coatings")
    else:
        cursor.execute("SELECT * FROM pricelist_coatings WHERE coating_name=?", (name,))
    res = cursor.fetchall()
    conn.close()
    return res

def get_filtered_services(name="Wszystkie"):
    if not is_db_accessible(): return []
    conn = get_connection()
    cursor = conn.cursor()
    if name == "Wszystkie":
        cursor.execute("SELECT * FROM pricelist_services")
    else:
        cursor.execute("SELECT * FROM pricelist_services WHERE service_name=?", (name,))
    res = cursor.fetchall()
    conn.close()
    return res

def save_cart_to_file(cart_items, client_name="Nieokreślony", path=CART_CACHE_PATH):
    data = {
        "client": client_name,
        "items": cart_items
    }
    try:
        if not os.path.exists('data'): os.makedirs('data')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Błąd zapisu koszyka: {e}")

def load_cart_from_file(path=CART_CACHE_PATH):
    if not os.path.exists(path):
        return "Nieokreślony", []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("client", "Nieokreślony"), data.get("items", [])
    except:
        return "Nieokreślony", []