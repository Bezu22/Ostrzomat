import threading
import utils.clients_db as clients_db

# --- CENTRALNA PAMIĘĆ PODRĘCZNA (RAM) ---
_CACHE = {
    "clients": [],
    "is_clients_loading": False
}

# Blokada wątków (Thread Lock) zapobiegająca jednoczesnym modyfikacjom
_lock = threading.Lock()


# --- OBSŁUGA BAZY KLIENTÓW ---

def preload_all_cache():
    """
    Główna funkcja wywoływana przy starcie aplikacji. 
    Inicjalizuje ładowanie wszystkich zasobów w tle.
    """
    preload_clients()


def preload_clients():
    """Pobiera klientów z bazy do pamięci RAM w osobnym wątku."""
    if _CACHE["is_clients_loading"]:
        return

    _CACHE["is_clients_loading"] = True

    def _fetch():
        try:
            # Pobieramy dane za pomocą istniejącej funkcji z clients_db
            data = clients_db.get_all_clients()
            with _lock:
                _CACHE["clients"] = data
        except Exception as e:
            print(f"Błąd podczas ładowania cache klientów: {e}")
        finally:
            _CACHE["is_clients_loading"] = False

    # Uruchomienie w tle (daemon=True sprawia, że wątek zamknie się razem z aplikacją)
    thread = threading.Thread(target=_fetch, daemon=True)
    thread.start()


def get_cached_clients():
    """Zwraca gotową listę klientów z pamięci RAM."""
    with _lock:
        return _CACHE["clients"]


def is_clients_loading():
    """Sprawdza, czy trwa wczytywanie klientów."""
    return _CACHE["is_clients_loading"]


def refresh_clients():
    """Wymusza ponowne pobranie danych z bazy (np. po dodaniu/edycji klienta)."""
    preload_clients()