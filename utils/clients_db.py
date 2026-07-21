import sqlite3
import os

# Ścieżka do osobnej bazy klientów
CLIENTS_DB_PATH = os.path.join('data', 'clients.db')

def _ensure_data_dir():
    """Upewnia się, że katalog 'data' istnieje."""
    if not os.path.exists('data'):
        os.makedirs('data')

def get_clients_connection():
    """Tworzy połączenie z bazą klientów (i tworzy plik, jeśli nie istnieje)."""
    _ensure_data_dir()
    conn = sqlite3.connect(CLIENTS_DB_PATH)
    conn.row_factory = sqlite3.Row  # Dostęp do kolumn jak w słowniku
    return conn

def init_clients_db():
    """Inicjalizuje tabelę klientów, jeśli jeszcze nie istnieje."""
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

# --- FUNKCJE CRUD KLIENTÓW ---

def add_client(name, phone="", nip="", email="", address="", notes=""):
    """Dodaje nowego klienta i zwraca jego nowe ID."""
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

def get_all_clients():
    """Zwraca listę wszystkich klientów posortowanych po nazwie."""
    init_clients_db()
    conn = get_clients_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients ORDER BY name ASC")
    clients = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return clients

def search_clients(query):
    """Szuka klientów po nazwie, telefonie lub NIP-ie."""
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
    """Pobiera dane konkretnego klienta po ID."""
    if not client_id:
        return None
    init_clients_db()
    conn = get_clients_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None