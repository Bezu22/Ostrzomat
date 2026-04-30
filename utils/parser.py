import sqlite3
import json
import re
import os

DB_NAME = 'ostrzomat.db'

def internal_parse_range(range_str):
    """
    Uniwersalny parser: zamienia 'do 6.0', '6.1-10', '≤ 10 mm', 'od 12' 
    na krotkę liczb (min, max).
    """
    if not range_str:
        return 0.0, 999.0
    
    # Czyszczenie tekstu
    s = range_str.lower().replace(',', '.').replace('mm', '').strip()
    numbers = re.findall(r"\d+\.\d+|\d+", s)
    
    if not numbers:
        return 0.0, 999.0
    
    val1 = float(numbers[0])
    
    if "do" in s or "≤" in s:
        return 0.0, val1
    elif "od" in s or ">" in s:
        return val1, 999.0
    elif len(numbers) == 2:
        return val1, float(numbers[1])
    elif len(numbers) == 1:
        # Przypadek typu '32+' lub '12.0' bez kontekstu
        return val1, 999.0
    
    return 0.0, 999.0

def run_full_migration():
    print("--- ROZPOCZĘCIE MIGRACJI BAZY DANYCH OSTRZOMAT 2.0 ---")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. PRZYGOTOWANIE STRUKTURY TABEL
    cursor.execute('DROP TABLE IF EXISTS pricelist_tools')
    cursor.execute('DROP TABLE IF EXISTS pricelist_coatings')
    cursor.execute('DROP TABLE IF EXISTS pricelist_services')

    # Tabela narzędzi (Frezy, Wiertła, Fazowniki)
    cursor.execute('''CREATE TABLE pricelist_tools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        tool_type TEXT,
        blades TEXT,
        diam_min REAL,
        diam_max REAL,
        price_1 REAL,
        price_2_4 REAL,
        price_5_10 REAL,
        price_11_20 REAL
    )''')

    # Tabela powłok (z uwzględnieniem długości)
    cursor.execute('''CREATE TABLE pricelist_coatings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        coating_name TEXT,
        diam_max REAL,
        length REAL,
        price REAL
    )''')

    # Tabela usług (Cięcie, Polerowanie, Zaniżanie)
    cursor.execute('''CREATE TABLE pricelist_services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_name TEXT,
        param_min REAL,
        param_max REAL,
        price REAL
    )''')

    # --- 2. IMPORT NARZĘDZI (JSONY: frezy, wiertla, pozostale) ---
    tool_files = {
        'cennik_frezy.json': 'Frezy',
        'cennik_wiertla.json': 'Wiertła',
        'cennik_pozostale.json': 'Inne'
    }

    for filename, category in tool_files.items():
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for tool_name, tool_content in data.items():
                    # Obsługa struktury z podziałem na ostrza lub bezpośrednim zakresem
                    if 'ilosc_ostrzy' in tool_content:
                        for blade_group, content in tool_content['ilosc_ostrzy'].items():
                            for entry in content['cennik']:
                                d_min, d_max = internal_parse_range(entry['zakres_srednicy'])
                                p = entry['ceny']
                                cursor.execute('INSERT INTO pricelist_tools VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                    (category, tool_name, blade_group, d_min, d_max, 
                                     float(str(p.get('1', p.get('1 szt.', 0))).replace(',','.')),
                                     float(str(p.get('2-4', p.get('2-4 szt.', 0))).replace(',','.')),
                                     float(str(p.get('5-10', p.get('5-10 szt.', 0))).replace(',','.')),
                                     float(str(p.get('11-20', p.get('11-20 szt.', 0))).replace(',','.'))))
                    
                    elif 'zakres_srednicy' in tool_content:
                        # Dla wierteł, które nie mają podziału na ostrza w Twoim JSONIE
                        for entry in tool_content['zakres_srednicy']:
                            d_min, d_max = internal_parse_range(entry['zakres_srednicy'])
                            p = entry['ceny']
                            cursor.execute('INSERT INTO pricelist_tools VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                (category, tool_name, 'standard', d_min, d_max,
                                 float(str(p.get('1 szt.', 0)).replace(',','.')),
                                 float(str(p.get('2-4 szt.', 0)).replace(',','.')),
                                 float(str(p.get('5-10 szt.', 0)).replace(',','.')),
                                 float(str(p.get('11-20 szt.', 0)).replace(',','.'))))
            print(f" Zaimportowano: {filename}")

    # --- 3. IMPORT POWŁOK ---
    if os.path.exists('cennik_powloki.json'):
        with open('cennik_powloki.json', 'r', encoding='utf-8') as f:
            powloki = json.load(f)
            for coating_name, content in powloki.items():
                for entry in content['zakres_srednicy']:
                    d_max = float(entry['srednica_max'])
                    for len_item in entry['dlugosc_calkowita']:
                        cursor.execute('INSERT INTO pricelist_coatings VALUES (NULL, ?, ?, ?, ?)',
                            (coating_name, d_max, float(len_item['dlugosc']), float(len_item['cena_jednostkowa'])))
        print(" Zaimportowano: cennik_powloki.json")

    # --- 4. IMPORT USŁUG ---
    if os.path.exists('cennik_uslugi.json'):
        with open('cennik_uslugi.json', 'r', encoding='utf-8') as f:
            uslugi = json.load(f)
            for service_name, content in uslugi.items():
                key = 'zakres_srednicy' if 'zakres_srednicy' in content else 'szerokosc'
                for item in content[key]:
                    raw_range = item.get('zakres_srednicy') or item.get('szerokosc')
                    p_min, p_max = internal_parse_range(raw_range)
                    cursor.execute('INSERT INTO pricelist_services VALUES (NULL, ?, ?, ?, ?)',
                        (service_name, p_min, p_max, float(item['cena_jednostkowa'])))
        print(" Zaimportowano: cennik_uslugi.json")

    conn.commit()
    conn.close()
    print("\n--- MIGRACJA ZAKOŃCZONA: Baza 'ostrzomat.db' jest gotowa ---")

if __name__ == "__main__":
    run_full_migration()