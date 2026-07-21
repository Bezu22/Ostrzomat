import sqlite3
import os

# Ścieżka do pliku bazy danych klientów
CLIENTS_DB_PATH = os.path.join('data', 'clients.db')

def _ensure_data_dir():
    """Upewnia się, że katalog 'data' istnieje na dysku."""
    if not os.path.exists('data'):
        os.makedirs('data')

def get_clients_connection():
    """
    Tworzy bezpieczne połączenie z bazą danych klientów.
    Automatycznie konfiguruje zwracanie wierszy jako słowniki.
    """
    _ensure_data_dir()
    conn = sqlite3.connect(CLIENTS_DB_PATH)
    conn.row_factory = sqlite3.Row  # Pozwala na dostęp do kolumn po nazwie (np. row['name'])
    return conn

def init_clients_db():
    """
    Tworzy tabelę 'clients' w bazie danych, jeśli jeszcze nie istnieje.
    """
    conn = get_clients_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            nip TEXT,
            email TEXT,
            address TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

# --- OPERACJE NA BAZIE DANYCH (CRUD) ---

def add_client(name, phone="", nip="", email="", address="", notes=""):
    """
    Dodaje nowego klienta do bazy i zwraca jego unikalne ID.
    """
    init_clients_db()  # Upewniamy się, że tabela istnieje
    conn = get_clients_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clients (name, phone, nip, email, address, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, phone, nip, email, address, notes))
    client_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return client_id

def update_client(client_id, name, phone="", nip="", email="", address="", notes=""):
    """
    Aktualizuje dane istniejącego klienta w bazie na podstawie jego ID.
    """
    init_clients_db()
    conn = get_clients_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE clients 
        SET name=?, phone=?, nip=?, email=?, address=?, notes=?
        WHERE id=?
    """, (name, phone, nip, email, address, notes, client_id))
    conn.commit()
    conn.close()

def get_all_clients():
    """
    Zwraca listę wszystkich klientów zapisanych w bazie,
    posortowanych alfabetycznie po nazwie.
    """
    init_clients_db()
    conn = get_clients_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients ORDER BY name ASC")
    clients = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return clients

def search_clients(query):
    """
    Wyszukuje klientów, których nazwa, numer telefonu lub NIP 
    zawierają wpisaną frazę (query).
    """
    init_clients_db()
    conn = get_clients_connection()
    cursor = conn.cursor()
    like_q = f"%{query}%"
    cursor.execute("""
        SELECT * FROM clients 
        WHERE name LIKE ? OR phone LIKE ? OR nip LIKE ?
        ORDER BY name ASC
    """, (like_q, like_q, like_q))
    clients = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return clients

def get_client_by_id(client_id):
    """
    Pobiera pełne dane jednego klienta na podstawie jego numeru ID.
    """
    if not client_id:
        return None
    init_clients_db()
    conn = get_clients_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None