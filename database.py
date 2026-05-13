import sqlite3
import os
import json

# --- ŚCIEŻKI ---
DB_PATH = os.path.join('data', 'ostrzomat.db')
SETTINGS_PATH = os.path.join('data', 'user_settings.json')
CART_CACHE_PATH = os.path.join('data', 'cart_cache.json') # Zmiana z basket na cart

def is_db_accessible():
    """Sprawdza czy plik bazy istnieje."""
    return os.path.exists(DB_PATH)

def get_connection():
    """Bezpieczne połączenie z bazą."""
    if not is_db_accessible():
        raise FileNotFoundError(f"Brak bazy w {DB_PATH}")
    return sqlite3.connect(f"file:{DB_PATH}?mode=rw", uri=True)

# --- FUNKCJE DLA FILTRÓW (COMBOBOXY) ---

def get_unique_tool_types(category="Wszystkie"):
    """Pobiera typy dla Narzędzi."""
    if not is_db_accessible(): return []
    conn = get_connection()
    cursor = conn.cursor()
    if category == "Wszystkie":
        cursor.execute("SELECT DISTINCT tool_type FROM pricelist_tools")
    else:
        cursor.execute("SELECT DISTINCT tool_type FROM pricelist_tools WHERE category=?", (category,))
    types = [r[0] for r in cursor.fetchall()]
    conn.close()
    return types

def get_unique_coating_names():
    """Pobiera unikalne nazwy powłok."""
    if not is_db_accessible(): return []
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT coating_name FROM pricelist_coatings")
    names = [r[0] for r in cursor.fetchall()]
    conn.close()
    return names

# --- POBIERANIE CEN (LOGIKA SILNIKA) ---

def get_tool_price(tool_type, blades_key, diameter, quantity):
    """Pobiera cenę ostrzenia na podstawie typu, klucza ostrzy, średnicy i ilości."""
    if not is_db_accessible(): return 0.0
    
    # Wybór kolumny cenowej na podstawie ilości
    if quantity >= 11: col = "price_11_20"
    elif quantity >= 5: col = "price_5_10"
    elif quantity >= 2: col = "price_2_4"
    else: col = "price_1"

    conn = get_connection()
    cursor = conn.cursor()
    
    # Szukamy przedziału średnic dla konkretnego typu i liczby ostrzy (blades_key: '2-4' lub 'pozostałe')
    query = f"SELECT {col} FROM pricelist_tools WHERE tool_type=? AND blades=? AND ? > diam_min AND ? <= diam_max"
    cursor.execute(query, (tool_type, blades_key, diameter, diameter))
    res = cursor.fetchone()
    
    # Jeśli średnica wykracza poza zakres, bierzemy najwyższą dostępną dla tego typu
    if not res:
        query_max = f"SELECT {col} FROM pricelist_tools WHERE tool_type=? AND blades=? ORDER BY diam_max DESC LIMIT 1"
        cursor.execute(query_max, (tool_type, blades_key))
        res = cursor.fetchone()
        
    conn.close()
    return float(res[0]) if res else 0.0

def get_coating_lengths(coating_name):
    """Pobiera dostępne progi długości dla konkretnej powłoki."""
    if not is_db_accessible() or coating_name == "Brak": return ["100"]
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT length FROM pricelist_coatings WHERE coating_name=? ORDER BY length ASC", (coating_name,))
    res = [str(r[0]) for r in cursor.fetchall()]
    conn.close()
    return res if res else ["100"]

def get_coating_price_refined(coating_name, diameter, length):
    """Pobiera cenę powłoki uwzględniając średnicę i wybraną długość."""
    if not is_db_accessible() or coating_name == "Brak": return 0.0
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT price FROM pricelist_coatings 
                      WHERE coating_name=? AND ? <= diam_max AND ? <= length 
                      ORDER BY diam_max ASC, length ASC LIMIT 1""", 
                   (coating_name, diameter, length))
    res = cursor.fetchone()
    conn.close()
    return float(res[0]) if res else 0.0

def get_service_price_refined(service_name, param_value):
    """Pobiera cenę usługi na podstawie nazwy i średnicy roboczej."""
    if not is_db_accessible(): return 0.0
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT price FROM pricelist_services 
                      WHERE service_name=? AND ? > param_min AND ? <= param_max 
                      LIMIT 1""", 
                   (service_name, param_value, param_value))
    res = cursor.fetchone()
    conn.close()
    return float(res[0]) if res and res[0] is not None else 0.0

# --- ZARZĄDZANIE USTAWIEŃAMI (CACHE) ---

def get_user_settings():
    """Wczytuje ostatnio używane parametry."""
    defaults = {
        "last_tool_type": "Frez prosty",
        "last_blades": "4",
        "last_diam": "10.0",
        "last_shank": "10.0"
    }
    if not os.path.exists(SETTINGS_PATH):
        return defaults
    try:
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return defaults

def save_user_settings(new_settings):
    """Zapisuje słownik ustawień do pliku, nadpisując tylko zmienione klucze."""
    settings = get_user_settings()
    settings.update(new_settings)
    try:
        if not os.path.exists('data'): os.makedirs('data')
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Błąd zapisu ustawień: {e}")

# --- ZARZĄDZANIE KOSZYKIEM (CART) ---

def save_cart_to_file(cart_items, client_name="Nieokreślony", path=CART_CACHE_PATH):
    """Zapisuje koszyk i klienta do JSON."""
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
    """Wczytuje koszyk. Zawsze zwraca (client_name, items)."""
    if not os.path.exists(path):
        return "Nieokreślony", []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data.get("client", "Nieokreślony"), data.get("items", [])
            elif isinstance(data, list):
                return "Nieokreślony", data
            return "Nieokreślony", []
    except Exception as e:
        print(f"Błąd odczytu koszyka: {e}")
        return "Nieokreślony", []