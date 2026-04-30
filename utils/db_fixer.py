import sqlite3

def run_database_fixer():
    # Połączenie z bazą danych Ostrzomat
    conn = sqlite3.connect('ostrzomat.db')
    cursor = conn.cursor()
    
    print("--- ROZPOCZĘCIE NAPRAWY I UJEDNOLICANIA BAZY ---")

    try:
        # 1. Naprawa Wierteł: 'standard' -> '2'[cite: 1]
        cursor.execute("""
            UPDATE pricelist_tools 
            SET blades = '2' 
            WHERE category = 'Wiertła' AND blades = 'standard'
        """)
        print(f"1. Wiertła: Zaktualizowano {cursor.rowcount} wierszy.")

        # 2. Naprawa literówek: 'pozostale' -> 'pozostałe'[cite: 3]
        cursor.execute("""
            UPDATE pricelist_tools 
            SET blades = 'pozostałe' 
            WHERE blades = 'pozostale'
        """)
        print(f"2. Literówki: Zaktualizowano {cursor.rowcount} wierszy (pozostale -> pozostałe).")

        # 3. Ujednolicenie Fazowników i Frezów: '>4' -> 'pozostałe'[cite: 3, 4]
        cursor.execute("""
            UPDATE pricelist_tools 
            SET blades = 'pozostałe' 
            WHERE blades = '>4'
        """)
        print(f"3. Zakresy: Zaktualizowano {cursor.rowcount} wierszy (>4 -> pozostałe).")

        # Zatwierdzenie wszystkich zmian w pliku bazy[cite: 1]
        conn.commit()
        print("\n--- SUKCES: Baza danych została ujednolicona! ---")

    except sqlite3.Error as e:
        # W razie błędu wycofaj zmiany, aby nie uszkodzić bazy[cite: 1]
        print(f"BŁĄD: Wystąpił problem z bazą danych: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    run_full_fix = True # Flaga bezpieczeństwa
    if run_full_fix:
        run_database_fixer()