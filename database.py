import sqlite3
import os
import json

# --- ŚCIEŻKI ---
DB_PATH = os.path.join('data', 'ostrzomat.db')
SETTINGS_PATH = os.path.join('data', 'user_settings.json')
CART_CACHE_PATH = os.path.join('data', 'cart_cache.json')

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
    """Pobiera unikalne nazwy powłok."""
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
    """Pobiera unikalne nazwy usług dla filtrów edytora."""
    if not is_db_accessible(): return []
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT service_name FROM pricelist_services")
        names = [r[0] for r in cursor.fetchall()]
        conn.close()
        return names
    except: return []

# --- POBIERANIE CEN (LOGIKA KALKULATORA) ---

def get_tool_price(tool_type, blades_key, diam, qty):
    """Zwraca cenę jednostkową ostrzenia na podstawie typu, ostrzy, średnicy i ilości."""
    if not is_db_accessible(): return 0.0
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Wybór kolumny ceny na podstawie ilości
        price_col = "price_1"
        if 2 <= qty <= 4: price_col = "price_2_4"
        elif 5 <= qty <= 10: price_col = "price_5_10"
        elif qty >= 11: price_col = "price_11_20"

        cursor.execute(f"""
            SELECT {price_col} FROM pricelist_tools 
            WHERE tool_type=? AND blades=? AND diam_min <= ? AND diam_max >= ?
        """, (tool_type, blades_key, diam, diam))
        
        res = cursor.fetchone()
        conn.close()
        return float(res[0]) if res else 0.0
    except: return 0.0

def get_unique_coating_lengths(coating_name):
    """Pobiera dostępne długości dla konkretnej powłoki."""
    if not is_db_accessible() or coating_name == "Brak": return []
    try:
        conn = get_connection()
        cursor = conn.cursor()
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
        
        # DEBUG: To powie nam, co program wysyła do bazy
        print(f"DEBUG: Szukam powłoki: {name}, Fi <= {d_val}, L <= {l_val}")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT price, diam_max, length FROM pricelist_coatings 
            WHERE coating_name=? AND diam_max >= ? AND length >= ?
            ORDER BY diam_max ASC, length ASC LIMIT 1
        """, (name, d_val, l_val))
        
        res = cursor.fetchone()
        conn.close()

        if res:
            print(f"DEBUG: Znaleziono! Cena: {res[0]} (Dopasowano do progu Fi: {res[1]}, L: {res[2]})")
            return float(res[0])
        else:
            print(f"DEBUG: BRAK DOPASOWANIA w bazie dla {name} przy Fi {d_val} i L {l_val}")
            return 0.0
    except Exception as e:
        print(f"Błąd bazy (coating): {e}")
        return 0.0

def get_service_price_refined(name, param_val):
    """Zwraca cenę usługi dodatkowej na podstawie parametru (np. średnicy)."""
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

# --- FUNKCJE DLA EDYTORA (FILTROWANIE LISTY) ---

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

# --- OPERACJE CRUD (DODAWANIE / EDYCJA / USUWANIE) ---

def delete_row(table_name, row_id):
    """Usuwa rekord z bazy."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name} WHERE id=?", (row_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Błąd usuwania: {e}")

def add_tool_row(vals):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO pricelist_tools 
        (category, tool_type, blades, diam_min, diam_max, price_1, price_2_4, price_5_10, price_11_20) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", vals)
    conn.commit()
    conn.close()

def update_tool_row(row_id, vals):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""UPDATE pricelist_tools SET 
        category=?, tool_type=?, blades=?, diam_min=?, diam_max=?, 
        price_1=?, price_2_4=?, price_5_10=?, price_11_20=? WHERE id=?""", (*vals, row_id))
    conn.commit()
    conn.close()

def add_coating_row(vals):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pricelist_coatings (coating_name, diam_max, length, price) VALUES (?, ?, ?, ?)", vals)
    conn.commit()
    conn.close()

def update_coating_row(row_id, vals):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE pricelist_coatings SET coating_name=?, diam_max=?, length=?, price=? WHERE id=?", (*vals, row_id))
    conn.commit()
    conn.close()

def add_service_row(vals):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pricelist_services (service_name, param_min, param_max, price) VALUES (?, ?, ?, ?)", vals)
    conn.commit()
    conn.close()

def update_service_row(row_id, vals):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE pricelist_services SET service_name=?, param_min=?, param_max=?, price=? WHERE id=?", (*vals, row_id))
    conn.commit()
    conn.close()

# --- ZARZĄDZANIE USTAWIENIAMI (JSON) ---

def get_user_settings():
    if not os.path.exists(SETTINGS_PATH):
        return {}
    try:
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return {}

def save_user_settings(new_settings):
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
            return data.get("client", "Nieokreślony"), data.get("items", [])
    except:
        return "Nieokreślony", []