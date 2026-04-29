import sqlite3

DB_NAME = 'ostrzomat.db'

def get_connection():
    """Zwraca aktywne połączenie z bazą danych."""
    return sqlite3.connect(DB_NAME)

def get_unique_tool_types():
    """Pobiera listę unikalnych typów narzędzi dla filtrów ComboBox."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT tool_type FROM pricelist")
        types = [r[0] for r in cursor.fetchall()]
    except sqlite3.OperationalError:
        types = []
    finally:
        conn.close()
    return types

def get_filtered_prices(tool_type=None):
    """Pobiera dane z cennika z uwzględnieniem filtra typu."""
    conn = get_connection()
    cursor = conn.cursor()
    if not tool_type or tool_type == "Wszystkie":
        cursor.execute("SELECT * FROM pricelist ORDER BY tool_type, diam_min")
    else:
        cursor.execute("SELECT * FROM pricelist WHERE tool_type=? ORDER BY diam_min", (tool_type,))
    data = cursor.fetchall()
    conn.close()
    return data

def update_price_row(row_id, vals):
    """Aktualizuje rekord. vals to lista: [type, blades, d_min, d_max, p1, p2, p3, p4]"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''UPDATE pricelist SET tool_type=?, blades=?, diam_min=?, diam_max=?, 
                      price_1=?, price_2_4=?, price_5_10=?, price_11_20=? WHERE id=?''', 
                   (*vals, row_id))
    conn.commit()
    conn.close()

def add_price_row(vals):
    """Dodaje nową pozycję do bazy."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO pricelist (tool_type, blades, diam_min, diam_max, 
                      price_1, price_2_4, price_5_10, price_11_20) 
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', vals)
    conn.commit()
    conn.close()

def delete_price_row(row_id):
    """Trwale usuwa wiersz z cennika."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pricelist WHERE id = ?", (row_id,))
    conn.commit()
    conn.close()

def find_unit_price(tool_type, input_blades, diameter, total_quantity):
    """
    Inteligentna logika wyceny:
    1. Szuka konkretnej liczby ostrzy.
    2. Szuka w zakresie '2-4'.
    3. Szuka w kategorii 'pozostałe'.
    """
    if total_quantity >= 11: col = "price_11_20"
    elif total_quantity >= 5: col = "price_5_10"
    elif total_quantity >= 2: col = "price_2_4"
    else: col = "price_1"

    conn = get_connection()
    cursor = conn.cursor()
    str_blades = str(input_blades)
    
    # Podstawowe zapytanie
    query = f"SELECT {col} FROM pricelist WHERE tool_type=? AND blades=? AND ? > diam_min AND ? <= diam_max"

    # Próba 1: Dokładne dopasowanie
    cursor.execute(query, (tool_type, str_blades, diameter, diameter))
    res = cursor.fetchone()
    
    # Próba 2: Zakres 2-4
    if not res and 2 <= int(input_blades) <= 4:
        cursor.execute(query, (tool_type, "2-4", diameter, diameter))
        res = cursor.fetchone()

    # Próba 3: Pozostałe
    if not res:
        cursor.execute(query, (tool_type, "pozostałe", diameter, diameter))
        res = cursor.fetchone()

    conn.close()
    return float(res[0]) if res else 0.0