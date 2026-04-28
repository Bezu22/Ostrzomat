import sqlite3
import os

DB_NAME = 'ostrzomat.db'

def get_connection():
    """Tworzy i zwraca połączenie z bazą."""
    return sqlite3.connect(DB_NAME)

def get_all_prices():
    """Pobiera cały cennik dla edytora."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pricelist")
    data = cursor.fetchall()
    conn.close()
    return data

def update_entire_pricelist(data_list):
    """Zastępuje obecny cennik nowymi danymi z edytora."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM pricelist")
        cursor.executemany('''
            INSERT INTO pricelist (tool_type, blades, diam_range, price_1, price_2_4, price_5_10, price_11_20)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', data_list)
        conn.commit()
        return True
    except Exception as e:
        print(f"Błąd bazy danych: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def find_price(tool_type, blades, diameter, quantity):
    """
    LOGIKA WYCENY:
    Szuka odpowiedniej ceny na podstawie parametrów.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Pobieramy wszystkie zakresy dla danego typu freza i ilości ostrzy
    cursor.execute('''
        SELECT diam_range, price_1, price_2_4, price_5_10, price_11_20 
        FROM pricelist 
        WHERE tool_type = ? AND blades = ?
    ''', (tool_type, blades))
    
    rows = cursor.fetchall()
    conn.close()

    # Tutaj w przyszłości dodamy logikę parsującą tekst "do 6.0" lub "6.1 - 10.0"
    # na liczby, aby dopasować wpisaną przez użytkownika średnicę.
    return rows