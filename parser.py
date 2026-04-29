import sqlite3
import json
import re
import os

def internal_parse_range(range_str):
    """Konwertuje tekst 'do 6.0' lub '6.1-10' na krotkę (min, max)."""
    range_str = range_str.lower().replace(',', '.')
    numbers = re.findall(r"\d+\.\d+|\d+", range_str)
    
    if "do" in range_str:
        return 0.0, float(numbers[0])
    elif len(numbers) == 2:
        return float(numbers[0]), float(numbers[1])
    elif len(numbers) == 1:
        return float(numbers[0]), 999.0
    return 0.0, 0.0

def run_full_migration(json_path='cennik_frezy.json'):
    if not os.path.exists(json_path):
        print(f"Błąd: Brak pliku {json_path}")
        return

    conn = sqlite3.connect('ostrzomat.db')
    cursor = conn.cursor()
    
    # Tworzenie nowej struktury (V3)
    cursor.execute('DROP TABLE IF EXISTS pricelist')
    cursor.execute('''
        CREATE TABLE pricelist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tool_type TEXT,
            blades TEXT,
            diam_min REAL,
            diam_max REAL,
            price_1 REAL,
            price_2_4 REAL,
            price_5_10 REAL,
            price_11_20 REAL
        )
    ''')

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for tool, content in data.items():
        for b_group, c_data in content['ilosc_ostrzy'].items():
            for entry in c_data['cennik']:
                d_min, d_max = internal_parse_range(entry['zakres_srednicy'])
                p = entry['ceny']
                cursor.execute('''
                    INSERT INTO pricelist (tool_type, blades, diam_min, diam_max, 
                                          price_1, price_2_4, price_5_10, price_11_20)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (tool, b_group, d_min, d_max, 
                      float(str(p['1']).replace(',', '.')), 
                      float(str(p['2-4']).replace(',', '.')), 
                      float(str(p['5-10']).replace(',', '.')), 
                      float(str(p['11-20']).replace(',', '.'))))
    
    conn.commit()
    conn.close()
    print("Migracja do modelu numerycznego zakończona sukcesem!")

if __name__ == "__main__":
    run_full_migration()