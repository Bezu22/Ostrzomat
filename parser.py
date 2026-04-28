import sqlite3
import json
import os

def parse_json_to_sql(json_file_path, db_name='ostrzomat.db'):
    # 1. Wczytanie danych z pliku JSON
    if not os.path.exists(json_file_path):
        print(f"Błąd: Plik {json_file_path} nie istnieje!")
        return

    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 2. Połączenie z bazą danych
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # 3. Przygotowanie struktury tabeli
    cursor.execute('DROP TABLE IF EXISTS pricelist')
    cursor.execute('''
        CREATE TABLE pricelist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tool_type TEXT,        -- np. Frez prosty
            blades TEXT,           -- np. 2-4 lub pozostałe
            diam_range TEXT,       -- np. do 6.0
            price_1 REAL,          -- Cena za 1 szt.
            price_2_4 REAL,        -- Cena za 2-4 szt.
            price_5_10 REAL,       -- Cena za 5-10 szt.
            price_11_20 REAL       -- Cena za 11-20 szt.
        )
    ''')

    # 4. Iteracja przez zagnieżdżoną strukturę JSON
    try:
        for tool_name, tool_data in data.items():
            # Wchodzimy w poziom "ilosc_ostrzy"
            blades_dict = tool_data.get('ilosc_ostrzy', {})
            
            for blade_group, content in blades_dict.items():
                # Pobieramy listę z cennikiem dla danej grupy ostrzy
                cennik_list = content.get('cennik', [])
                
                for entry in cennik_list:
                    zakres = entry.get('zakres_srednicy')
                    ceny = entry.get('ceny', {})

                    # Wstawienie rekordu do bazy
                    cursor.execute('''
                        INSERT INTO pricelist (
                            tool_type, blades, diam_range, 
                            price_1, price_2_4, price_5_10, price_11_20
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        tool_name,
                        blade_group,
                        zakres,
                        ceny.get('1'),
                        ceny.get('2-4'),
                        ceny.get('5-10'),
                        ceny.get('11-20')
                    ))

        conn.commit()
        print(f"Sukces! Dane z pliku '{json_file_path}' zostały zaimportowane do '{db_name}'.")

    except Exception as e:
        print(f"Wystąpił błąd podczas parsowania: {e}")
        conn.rollback()
    finally:
        conn.close()

# --- URUCHOMIENIE ---
if __name__ == "__main__":
    # Upewnij się, że nazwa pliku zgadza się z Twoim plikiem na dysku
    parse_json_to_sql('cennik_frezy.json')