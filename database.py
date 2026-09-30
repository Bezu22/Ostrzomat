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

_initialized_db_path = None

def init_db(connection=None):
    """
    Inicjalizuje i weryfikuje schemat bazy cennika SQLite.
    Wykonuje ewentualne migracje kolumn i tabel raz przy starcie aplikacji
    lub po zmianie pliku bazy, eliminując kosztowne operacje DDL z zapytań o cenę.
    """
    global _initialized_db_path
    should_close = False
    if connection is None:
        if not is_db_accessible():
            return
        connection = get_connection()
        should_close = True
    try:
        ensure_tool_blade_columns(connection)
        ensure_quantity_discounts_table(connection)
        ensure_tool_ranges_table(connection)
        connection.commit()
        _initialized_db_path = DB_PATH
    finally:
        if should_close:
            connection.close()

def ensure_schema_ready():
    """Upewnia się, że schemat bazy pod aktualną ścieżką DB_PATH został zainicjalizowany."""
    global _initialized_db_path
    if _initialized_db_path != DB_PATH:
        init_db()

def ensure_quantity_discounts_table(connection):
    connection.execute("""
        CREATE TABLE IF NOT EXISTS pricelist_quantity_discounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            qty_min INTEGER NOT NULL,
            qty_max INTEGER NOT NULL,
            discount_pct REAL NOT NULL
        )
    """)

def ensure_tool_ranges_table(connection):
    connection.execute("""
        CREATE TABLE IF NOT EXISTS pricelist_tool_ranges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tool_type TEXT NOT NULL,
            blades_min INTEGER NOT NULL,
            blades_max INTEGER NOT NULL,
            diam_min REAL NOT NULL,
            diam_max REAL NOT NULL,
            qty_min INTEGER NOT NULL,
            qty_max INTEGER NOT NULL,
            price REAL NOT NULL
        )
    """)
    columns = {row[1] for row in connection.execute("PRAGMA table_info(pricelist_tool_ranges)")}
    if "blades_min" not in columns:
        connection.execute("ALTER TABLE pricelist_tool_ranges ADD COLUMN blades_min INTEGER")
        connection.execute("ALTER TABLE pricelist_tool_ranges ADD COLUMN blades_max INTEGER")
    if "blades" in columns:
        connection.execute("""
            UPDATE pricelist_tool_ranges SET blades_min=CASE
                WHEN blades IN ('2-4', '1-4') OR blades_min IN ('2-4', '1-4') THEN 1
                WHEN blades IN ('pozostałe', '5-99') OR blades_min IN ('pozostałe', '5-99', '0-99') THEN 5
                ELSE CAST(blades_min AS INTEGER) END,
                blades_max=CASE
                WHEN blades IN ('2-4', '1-4') OR blades_min IN ('2-4', '1-4') THEN 4
                WHEN blades IN ('pozostałe', '5-99') OR blades_min IN ('pozostałe', '5-99', '0-99') THEN 99
                ELSE CAST(blades_max AS INTEGER) END
                WHERE blades_min IS NULL OR blades_max IS NULL
                    OR typeof(blades_min) != 'integer' OR typeof(blades_max) != 'integer'
        """)

def ensure_tool_blade_columns(connection):
    columns = {row[1] for row in connection.execute("PRAGMA table_info(pricelist_tools)")}
    if "blades_min" not in columns:
        connection.execute("ALTER TABLE pricelist_tools ADD COLUMN blades_min INTEGER")
    if "blades_max" not in columns:
        connection.execute("ALTER TABLE pricelist_tools ADD COLUMN blades_max INTEGER")
    if "price_base" not in columns:
        connection.execute("ALTER TABLE pricelist_tools ADD COLUMN price_base REAL")
        if "price_1" in columns:
            connection.execute("UPDATE pricelist_tools SET price_base = price_1 WHERE price_base IS NULL")
    connection.execute("""
        UPDATE pricelist_tools SET blades_min=CASE
            WHEN blades IN ('2-4', '1-4') THEN 1
            WHEN blades IN ('pozostałe', '5-99', '0-99') OR (blades_min=0 AND blades_max IN (0, 99)) THEN 5
            ELSE CAST(blades AS INTEGER) END,
            blades_max=CASE
            WHEN blades IN ('2-4', '1-4') THEN 4
            WHEN blades IN ('pozostałe', '5-99', '0-99') OR (blades_min=0 AND blades_max IN (0, 99)) THEN 99
            ELSE CAST(blades AS INTEGER) END
        WHERE blades_min IS NULL OR blades_max IS NULL OR (blades_min=0 AND blades_max IN (0, 99))
    """)

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
    Cena bazowa jest pobierana z pricelist_tools, a rabat ilościowy z pricelist_quantity_discounts.
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
        
        ensure_schema_ready()
        conn = get_connection()
        cursor = conn.cursor()

        # Sprawdzenie obecności kolumny price_base lub starszej price_1
        columns = {row[1] for row in cursor.execute("PRAGMA table_info(pricelist_tools)")}
        base_col = "price_base" if "price_base" in columns else "price_1"

        # Próba 1: Dokładne szukanie według typu, liczby ostrzy oraz zakresu średnic
        query_exact = f"""
            SELECT {base_col} FROM pricelist_tools 
            WHERE tool_type=? AND blades_min <= ? AND blades_max >= ? AND diam_min <= ? AND diam_max >= ?
            LIMIT 1
        """
        cursor.execute(query_exact, (clean_type, int(blades_key), int(blades_key), d_val, d_val))
        res = cursor.fetchone()
        
        # Próba 2 (Fallback dla frezów): Jeśli brak dokładnego wpisu dla danej liczby ostrzy w bazie,
        # szukamy wpisu bez uwzględniania konkretnej liczby ostrzy
        if not res or res[0] is None:
            query_fallback = f"""
                SELECT {base_col} FROM pricelist_tools 
                WHERE tool_type=? AND diam_min <= ? AND diam_max >= ?
                LIMIT 1
            """
            cursor.execute(query_fallback, (clean_type, d_val, d_val))
            res = cursor.fetchone()

        if not res or res[0] is None or float(res[0]) <= 0:
            conn.close()
            return 0.0

        base_price = float(res[0])

        # Pobranie rabatu ilościowego z tabeli pricelist_quantity_discounts
        has_disc_table = cursor.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='pricelist_quantity_discounts'"
        ).fetchone()[0] > 0

        discount_pct = 0.0
        if has_disc_table:
            cursor.execute("""
                SELECT discount_pct FROM pricelist_quantity_discounts
                WHERE qty_min <= ? AND qty_max >= ?
                ORDER BY qty_min DESC LIMIT 1
            """, (q_val, q_val))
            disc_row = cursor.fetchone()
            if disc_row and disc_row[0] is not None:
                discount_pct = float(disc_row[0])

        conn.close()

        discounted_price = base_price * (1.0 - (discount_pct / 100.0))
        return round(max(discounted_price, 0.0), 2)
        
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
    """Zwraca jednostkową cenę nałożenia powłoki."""
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