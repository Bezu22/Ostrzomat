import sqlite3
import os
import json

# Ścieżka do bazy w folderze data/
DB_PATH = os.path.join('data', 'ostrzomat.db')
SETTINGS_PATH = os.path.join('data', 'user_settings.json')

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
    """Pobiera unikalne nazwy powłok - TEGO BRAKOWAŁO."""
    if not is_db_accessible(): return []
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT coating_name FROM pricelist_coatings")
    names = [r[0] for r in cursor.fetchall()]
    conn.close()
    return names

def get_unique_service_names():
    """Pobiera unikalne nazwy usług - TEGO BRAKOWAŁO."""
    if not is_db_accessible(): return []
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT service_name FROM pricelist_services")
    names = [r[0] for r in cursor.fetchall()]
    conn.close()
    return names

# --- POWŁOKI ---
def update_coating_row(row_id, vals):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE pricelist_coatings SET coating_name=?, diam_max=?, length=?, price=? WHERE id=?', (*vals, row_id))
    conn.commit()
    conn.close()

def add_coating_row(vals):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO pricelist_coatings (coating_name, diam_max, length, price) VALUES (?, ?, ?, ?)', vals)
    conn.commit()
    conn.close()

# --- USŁUGI ---
def update_service_row(row_id, vals):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE pricelist_services SET service_name=?, param_min=?, param_max=?, price=? WHERE id=?', (*vals, row_id))
    conn.commit()
    conn.close()

def add_service_row(vals):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO pricelist_services (service_name, param_min, param_max, price) VALUES (?, ?, ?, ?)', vals)
    conn.commit()
    conn.close()

# --- FUNKCJE POBIERANIA DANYCH DO LISTY ---

def get_filtered_tools(category, tool_type):
    if not is_db_accessible(): return []
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM pricelist_tools WHERE 1=1"
    params = []
    if category != "Wszystkie":
        query += " AND category=?"
        params.append(category)
    if tool_type != "Wszystkie":
        query += " AND tool_type=?"
        params.append(tool_type)
    query += " ORDER BY tool_type, diam_min"
    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    return data

def get_filtered_coatings(name):
    if not is_db_accessible(): return []
    conn = get_connection()
    cursor = conn.cursor()
    if name == "Wszystkie":
        cursor.execute("SELECT * FROM pricelist_coatings ORDER BY coating_name, diam_max, length")
    else:
        cursor.execute("SELECT * FROM pricelist_coatings WHERE coating_name=? ORDER BY diam_max, length", (name,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_filtered_services(name):
    if not is_db_accessible(): return []
    conn = get_connection()
    cursor = conn.cursor()
    if name == "Wszystkie":
        cursor.execute("SELECT * FROM pricelist_services ORDER BY service_name")
    else:
        cursor.execute("SELECT * FROM pricelist_services WHERE service_name=? ORDER BY param_min", (name,))
    data = cursor.fetchall()
    conn.close()
    return data

# --- USUWANIE REKORDÓW ---
def delete_row(table, row_id):
    if not is_db_accessible(): return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table} WHERE id=?", (row_id,))
    conn.commit()
    conn.close()

def get_tool_price(tool_type, blades, diameter, quantity):
    if not is_db_accessible(): return 0.0
    
    # Wybór kolumny
    if quantity >= 11: col = "price_11_20"
    elif quantity >= 5: col = "price_5_10"
    elif quantity >= 2: col = "price_2_4"
    else: col = "price_1"

    conn = get_connection()
    cursor = conn.cursor()
    
    # KROK 1: Szukamy idealnego dopasowania
    query = f"SELECT {col} FROM pricelist_tools WHERE tool_type=? AND blades=? AND ? > diam_min AND ? <= diam_max"
    cursor.execute(query, (tool_type, blades, diameter, diameter))
    res = cursor.fetchone()
    
    # KROK 2: Jeśli nie znaleziono (średnica za duża), bierzemy ostatni rekord (najdroższy)
    if not res:
        query_max = f"SELECT {col} FROM pricelist_tools WHERE tool_type=? AND blades=? ORDER BY diam_max DESC LIMIT 1"
        cursor.execute(query_max, (tool_type, blades))
        res = cursor.fetchone()
        
    conn.close()
    return float(res[0]) if res else 0.0

def get_coating_price(coating_name, diameter):
    """Pobiera cenę powłoki dla danej średnicy."""
    if not is_db_accessible() or coating_name == "Brak": return 0.0
    
    conn = get_connection()
    cursor = conn.cursor()
    # Szukamy ceny dla danej powłoki, gdzie średnica <= diam_max
    cursor.execute("SELECT price FROM pricelist_coatings WHERE coating_name=? AND ? <= diam_max ORDER BY diam_max ASC LIMIT 1", 
                   (coating_name, diameter))
    res = cursor.fetchone()
    conn.close()
    
    return float(res[0]) if res else 0.0

def get_user_settings():
    """Wczytuje ustawienia z pliku JSON. Jeśli brak pliku, zwraca wartości domyślne."""
    defaults = {
        "last_tool_type": "Frez prosty",
        "last_blades": "4",
        "last_diam": "10.0"
    }
    if not os.path.exists(SETTINGS_PATH):
        return defaults
    
    try:
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return defaults

def save_user_settings(tool_type, blades, diam):
    """Zapisuje aktualne ustawienia do pliku."""
    settings = {
        "last_tool_type": tool_type,
        "last_blades": blades,
        "last_diam": diam
    }
    try:
        if not os.path.exists('data'):
            os.makedirs('data')
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Błąd zapisu ustawień: {e}")

def get_coating_lengths(coating_name):
    """Pobiera dostępne progi długości dla konkretnej powłoki."""
    if not is_db_accessible() or coating_name == "Brak": return ["100"]
    conn = get_connection()
    cursor = conn.cursor()
    # Zmieniono length_max na length
    cursor.execute("SELECT DISTINCT length FROM pricelist_coatings WHERE coating_name=? ORDER BY length ASC", (coating_name,))
    res = [str(r[0]) for r in cursor.fetchall()]
    conn.close()
    return res if res else ["100"]

def get_coating_price_refined(coating_name, diameter, length):
    """Pobiera cenę powłoki uwzględniając średnicę i wybraną długość."""
    if not is_db_accessible() or coating_name == "Brak": return 0.0
    conn = get_connection()
    cursor = conn.cursor()
    # Zmieniono length_max na length oraz diam_max na diam_max (zgodnie z tabelą)
    cursor.execute("""SELECT price FROM pricelist_coatings 
                      WHERE coating_name=? AND ? <= diam_max AND ? <= length 
                      ORDER BY diam_max ASC, length ASC LIMIT 1""", 
                   (coating_name, diameter, length))
    res = cursor.fetchone()
    conn.close()
    return float(res[0]) if res else 0.0