import sqlite3
import os

# Ścieżka do bazy w folderze data/
DB_PATH = os.path.join('data', 'ostrzomat.db')

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