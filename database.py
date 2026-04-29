import sqlite3

DB_NAME = 'ostrzomat.db'

def get_connection():
    """Zwraca aktywne połączenie z bazą danych."""
    return sqlite3.connect(DB_NAME)

def get_unique_tool_types():
    """Dla ComboBoxa w edytorze i menu głównym."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT tool_type FROM pricelist")
    types = [r[0] for r in cursor.fetchall()]
    conn.close()
    return types

def get_filtered_prices(tool_type=None):
    """Pobiera dane z uwzględnieniem filtra typu."""
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
    """Aktualizuje pojedynczy rekord z poziomu formularza edycji."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''UPDATE pricelist SET tool_type=?, blades=?, diam_min=?, diam_max=?, 
                      price_1=?, price_2_4=?, price_5_10=?, price_11_20=? WHERE id=?''', 
                   (*vals, row_id))
    conn.commit()
    conn.close()

def delete_price_row(row_id):
    """Usuwa wiersz z cennika na podstawie ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pricelist WHERE id = ?", (row_id,))
    conn.commit()
    conn.close()

def add_price_row(vals):
    """Dodaje nowy rekord do cennika."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO pricelist (tool_type, blades, diam_min, diam_max, 
                      price_1, price_2_4, price_5_10, price_11_20) 
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', vals)
    conn.commit()
    conn.close()

def find_unit_price(tool_type, input_blades, diameter, total_quantity):
    """
    Inteligentnie znajduje cenę, obsługując konkretne liczby, 
    zakresy i wartości domyślne.
    """
    # 1. Wybór kolumny ceny (bez zmian)
    if total_quantity >= 11: col = "price_11_20"
    elif total_quantity >= 5: col = "price_5_10"
    elif total_quantity >= 2: col = "price_2_4"
    else: col = "price_1"

    conn = get_connection()
    cursor = conn.cursor()
    
    # Zamieniamy wejście na string, żeby pasowało do bazy
    str_blades = str(input_blades)

    # --- KROK 1: Szukanie dokładnego dopasowania (np. dla "6") ---
    query_exact = f"SELECT {col} FROM pricelist WHERE tool_type=? AND blades=? AND ? > diam_min AND ? <= diam_max"
    cursor.execute(query_exact, (tool_type, str_blades, diameter, diameter))
    res = cursor.fetchone()
    
    if res:
        conn.close()
        return res[0]

    # --- KROK 2: Szukanie w standardowym zakresie "2-4" ---
    if 2 <= int(input_blades) <= 4:
        cursor.execute(query_exact, (tool_type, "2-4", diameter, diameter))
        res = cursor.fetchone()
        if res:
            conn.close()
            return res[0]

    # --- KROK 3: Szukanie w kategorii "pozostałe" ---
    cursor.execute(query_exact, (tool_type, "pozostałe", diameter, diameter))
    res = cursor.fetchone()
    
    conn.close()
    return res[0] if res else 0.0