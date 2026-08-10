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
    """
    Zwraca cenę jednostkową ostrzenia z bazy danych.
    Dla wierteł zawsze wymusza wartość ostrzy = '2'.
    Dla frezów pobiera stawkę dla liczby ostrzy podanej przez użytkownika.
    """
    if not is_db_accessible(): 
        return 0.0
    try:
        d_val = float(diam)
        q_val = int(qty)
        
        # Wyczyszczenie nazwy typu z przedrostków (np. 'Frez promieniowy R0.5' -> 'Frez promieniowy')
        clean_type = str(tool_type).split(" R")[0].strip()
        
        # Zgodnie z założeniem: dla wierteł zawsze wymuszamy liczbę ostrzy Z = 2
        wiertla_typy = ["Wiertla", "Wiertła", "Wiertlo", "Wiertło", "Wiertła stopniowe", "Wiertło stopniowe"]
        if any(w.lower() in clean_type.lower() for w in wiertla_typy):
            blades_key = "2"
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Dobór kolumny cenowej w zależności od progu ilościowego
        if q_val >= 11: 
            price_col = "price_11_20"
        elif q_val >= 5: 
            price_col = "price_5_10"
        elif q_val >= 2: 
            price_col = "price_2_4"
        else: 
            price_col = "price_1"

        print(f"DEBUG BAZY -> Szukam: typ='{clean_type}', ostrza='{blades_key}', srednica={d_val}, kolumna={price_col}")

        # Próba 1: Dokładne szukanie według typu, liczby ostrzy oraz zakresu średnic
        query_exact = f"""
            SELECT {price_col} FROM pricelist_tools 
            WHERE tool_type=? AND blades=? AND diam_min <= ? AND diam_max >= ?
        """
        cursor.execute(query_exact, (clean_type, str(blades_key), d_val, d_val))
        res = cursor.fetchone()
        
        # Próba 2 (Fallback dla frezów): Jeśli brak dokładnego wpisu dla danej liczby ostrzy w bazie,
        # szukamy wpisu bez uwzględniania konkretnej liczby ostrzy
        if not res or res[0] is None:
            query_fallback = f"""
                SELECT {price_col} FROM pricelist_tools 
                WHERE tool_type=? AND diam_min <= ? AND diam_max >= ?
                LIMIT 1
            """
            cursor.execute(query_fallback, (clean_type, d_val, d_val))
            res = cursor.fetchone()

        conn.close()
        
        if res and res[0] is not None:
            print(f"DEBUG BAZY -> Znaleziono cenę: {float(res[0])}")
            return float(res[0])
        else:
            print("DEBUG BAZY -> Nic nie znaleziono! Baza zwróciła pusty wynik.")
            return 0.0
        
    except Exception as e:
        print(f"Błąd bazy (get_tool_price): {e}")
        return 0.0

def get_unique_coating_lengths(coating_name):
    """Pobiera dostępne długości dla konkretnej powłoki lub wszystkie dostępne, gdy brak powłoki."""
    if not is_db_accessible(): 
        return []
        
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
    except: 
        return []

def get_coating_price(name, diam, length):
    """Zwraca jednostkową cenę nałożenia powłoki. (Oczyszczona z komunikatów debugowania)"""
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

def save_cart_to_file(cart_items, client_id=None, client_name="Nieokreślony", path=CART_CACHE_PATH):
    """Zapisuje koszyk, ID klienta oraz jego nazwę do JSON."""
    data = {
        "client_id": client_id,
        "client_name": client_name,
        "items": cart_items
    }
    try:
        if not os.path.exists('data'): os.makedirs('data')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Błąd zapisu koszyka: {e}")

def load_cart_from_file(path=CART_CACHE_PATH):
    """
    Wczytuje koszyk. Zawsze zwraca słownik: 
    {"client_id": ID, "client_name": Name, "items": [...]}
    """
    default_res = {"client_id": None, "client_name": "Nieokreślony", "items": []}
    if not os.path.exists(path):
        return default_res
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Obsługa struktur obecnych oraz starszych (kompatybilność)
            if isinstance(data, dict):
                return {
                    "client_id": data.get("client_id", None),
                    "client_name": data.get("client_name", data.get("client", "Nieokreślony")),
                    "items": data.get("items", [])
                }
            return default_res
    except:
        return default_res