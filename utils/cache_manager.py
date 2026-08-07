import threading
import utils.clients_db as clients_db

# --- CENTRALNA PAMIĘĆ PODRĘCZNA (RAM) ---
# Słownik przechowywany w pamięci RAM całej aplikacji
_CACHE = {
    "clients": [],
    "is_clients_loading": False
}

# Blokada wielowątkowa gwarantująca bezpieczny odczyt i zapis
_lock = threading.Lock()


def preload_all_cache():
    """
    Główna funkcja wywoływana przy starcie aplikacji.
    Inicjalizuje pobieranie danych w tle.
    """
    preload_clients()


def preload_clients():
    """Pobiera listę klientów z bazy SQLite do pamięci RAM w osobnym wątku."""
    if _CACHE["is_clients_loading"]:
        return

    _CACHE["is_clients_loading"] = True

    def _fetch():
        try:
            # Bezpośrednie pobranie słowników klientów z bazy
            data = clients_db.get_all_clients()
            with _lock:
                _CACHE["clients"] = data
        except Exception as e:
            print(f"Błąd podczas ładowania cache klientów: {e}")
        finally:
            _CACHE["is_clients_loading"] = False

    # Tworzymy i uruchamiamy wątek działający w tle
    thread = threading.Thread(target=_fetch, daemon=True)
    thread.start()


def get_cached_clients():
    """Błyskawicznie zwraca listę klientów z pamięci RAM (bez odpytywania bazy)."""
    with _lock:
        return _CACHE["clients"]


def is_clients_loading():
    """Sprawdza, czy wczytywanie danych z bazy jeszcze trwa."""
    return _CACHE["is_clients_loading"]


def refresh_clients():
    """Wywoływane po dodaniu/edytowaniu klienta, aby odświeżyć dane w RAM."""
    preload_clients()