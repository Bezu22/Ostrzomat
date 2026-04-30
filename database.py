import sqlite3

DB_NAME = 'ostrzomat.db'

def get_connection():
    return sqlite3.connect(DB_NAME)

def find_unit_price(category, tool_type, input_blades, diameter, total_quantity):
    """
    Ujednolicona funkcja wyceny.
    input_blades: liczba przekazana z interfejsu (np. int lub string)
    """
    # Wybór kolumny ceny na podstawie ilości
    if total_quantity >= 11: col = "price_11_20"
    elif total_quantity >= 5: col = "price_5_10"
    elif total_quantity >= 2: col = "price_2_4"
    else: col = "price_1"

    # Mapowanie wejścia na klucze bazy danych
    search_blades = str(input_blades)
    
    # Logika ujednolicona:
    try:
        val = int(input_blades)
        if val == 2:
            search_blades = "2"
        elif 2 < val <= 4:
            search_blades = "2-4"
        elif val > 4:
            search_blades = "pozostałe" # Tutaj musi być polski znak!
    except ValueError:
        # Jeśli wpisano tekst (np. "pozostałe"), zostawiamy jak jest
        pass

    conn = get_connection()
    cursor = conn.cursor()
    
    query = f"""
        SELECT {col} FROM pricelist_tools 
        WHERE category=? AND tool_type=? AND blades=? 
        AND ? > diam_min AND ? <= diam_max
    """
    
    cursor.execute(query, (category, tool_type, search_blades, diameter, diameter))
    result = cursor.fetchone()
    conn.close()
    
    return float(result[0]) if result else 0.0

# --- POBIERANIE UNIKALNYCH WARTOŚCI DLA FILTRÓW ---
def get_unique_tool_types(category="Wszystkie"):
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
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT coating_name FROM pricelist_coatings")
    names = [r[0] for r in cursor.fetchall()]
    conn.close()
    return names

def get_unique_service_names():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT service_name FROM pricelist_services")
    names = [r[0] for r in cursor.fetchall()]
    conn.close()
    return names

# --- POBIERANIE DANYCH ---
def get_filtered_tools(category, tool_type):
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
    conn = get_connection()
    cursor = conn.cursor()
    if name == "Wszystkie":
        cursor.execute("SELECT * FROM pricelist_services ORDER BY service_name")
    else:
        cursor.execute("SELECT * FROM pricelist_services WHERE service_name=? ORDER BY param_min", (name,))
    data = cursor.fetchall()
    conn.close()
    return data

# --- ZAPIS I USUWANIĘ ---
def update_tool_row(row_id, vals):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''UPDATE pricelist_tools SET category=?, tool_type=?, blades=?, 
                      diam_min=?, diam_max=?, price_1=?, price_2_4=?, price_5_10=?, price_11_20=? 
                      WHERE id=?''', (*vals, row_id))
    conn.commit()
    conn.close()

def add_tool_row(vals):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO pricelist_tools (category, tool_type, blades, diam_min, diam_max, 
                      price_1, price_2_4, price_5_10, price_11_20) 
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', vals)
    conn.commit()
    conn.close()

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

def delete_row(table, row_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table} WHERE id=?", (row_id,))
    conn.commit()
    conn.close()