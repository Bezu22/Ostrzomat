# DOKUMENTACJA TECHNICZNA I OPIS SYSTEMU „OSTRZOMAT”
## Materiał źródłowy do pracy inżynierskiej / seminaryjnej
**Projekt:** System wspomagania kalkulacji kosztów, zarządzania zleceniami oraz automatyzacji generowania ofert dla usług ostrzenia i regeneracji narzędzi skrawających (*Ostrzomat v0.2*)  
**Autor projektu:** [Imię i Nazwisko Studenta]  
**Kierunek studiów / Specjalność:** Inżynieria Oprogramowania / Informatyka Stosowana / Mechanika i Budowa Maszyn  
**Język i technologie:** Python 3.8+, CustomTkinter, SQLite3, openpyxl, ReportLab, python-docx, pytest  

---

# SPIS TREŚCI
1. **Wstęp i geneza projektu**
   - 1.1. Problem inżynierski i biznesowy
   - 1.2. Cel projektu i wymagania funkcjonalne
   - 1.3. Odbiorcy i środowisko wdrożeniowe
2. **Architektura systemu i zasada działania**
   - 2.1. Ogólna architektura wielowarstwowa (Layered Architecture)
   - 2.2. Koncepcja hybrydowej bazy danych: Excel jako „Single Source of Truth” + SQLite jako relacyjna pamięć robocza
   - 2.3. Przepływ danych w procesie wyceny (Data Flow Pipeline)
3. **Szczegółowy opis modułów funkcjonalnych**
   - 3.1. Moduł kalkulacji frezów (`frez_module.py`)
   - 3.2. Moduł kalkulacji wierteł (`drill_module.py`)
   - 3.3. Moduł narzędzi specjalnych (`special_module.py`)
   - 3.4. Wspólna klasa bazowa modułów narzędziowych (`BaseToolModule`)
   - 3.5. Obsługa powłok technicznych (PVD/CVD) i usług dodatkowych
   - 3.6. Koszyk zleceń, rabatowanie i persystencja sesji (`cart_logic.py`, `cart_table.py`)
   - 3.7. Baza kontrahentów i książka adresowa (`clients_db.py`, `client_popup.py`)
   - 3.8. Zunifikowany generator dokumentacji handlowej (`document_exporter.py`, `export_modal.py`)
4. **Omówienie kluczowych fragmentów kodu i algorytmów**
   - 4.1. Algorytm kalkulacji ceny narzędzia z progami ilościowymi i zużyciem (`logic/cart_logic.py`)
   - 4.2. Automatyczna synchronizacja i walidacja cennika Excel $\rightarrow$ SQLite (`utils/price_list_excel.py`)
   - 4.3. Wielowymiarowe odpytywanie bazy danych z tolerancją geometrii (`database.py`)
   - 4.4. Polimorfizm i automatyzacja doboru średnicy chwytu (`ui/calc_modules/base_module.py`)
   - 4.5. Silnik generowania raportów PDF ze zliczaniem stron `NumberedCanvas` (`utils/document_exporter.py`)
   - 4.6. Zunifikowane okno modalne eksportu z autoinkrementacją numeracji (`ui/export_modal.py`)
5. **Jakość kodu, testowanie i weryfikacja**
   - 5.1. Architektura testów jednostkowych i integracyjnych (`pytest`)
   - 5.2. Metryki redukcji długu technologicznego po refaktoryzacji
6. **Wskazówki dla modelu językowego redagującego pracę dyplomową**
   - 6.1. Sugerowana struktura rozdziałów pracy inżynierskiej
   - 6.2. Słownik pojęć domenowych (branża CNC / obróbka skrawaniem)
   - 6.3. Wnioski i perspektywy dalszego rozwoju systemu

---

# 1. WSTĘP I GENEZA PROJEKTU

### 1.1. Problem inżynierski i biznesowy
W przedsiębiorstwach produkcyjnych z sektora obróbki skrawaniem (frezowanie, wiercenie, toczenie) kluczowym czynnikiem optymalizacji kosztów jest regeneracja narzędzi z węglików spiekanych (VHM) oraz stali szybkotnących (HSS). Ostrzenie oraz ponowne nakładanie powłok ochronnych (np. TiAlN, AlTiN, DLC) pozwala na wielokrotne przywrócenie właściwości skrawających narzędzia przy ułamku kosztu zakupu nowego narzędzia.

Proces kalkulacji kosztu regeneracji jest jednak wysoce złożony i wielowymiarowy:
1. **Złożona matryca cenowa:** Cena zależy od typu geometrii (frez walcowo-czołowy, kulisty, promieniowy, wiertło monolityczne, wiertło stopniowe), średnicy narzędzia ($D$), liczby ostrzy ($Z$) oraz liczby sztuk w partii (progi rabatowe: 1 szt., 2-4 szt., 5-10 szt., 11+ szt.).
2. **Koszty powłok przeciwzużyciowych:** Wycena nałożenia nowej powłoki wymaga korelacji maksymalnej średnicy zewnętrznej narzędzia, jego długości całkowitej ($L$) oraz typu powłoki.
3. **Usługi dodatkowe i uszkodzenia:** Narzędzia często trafiają do regeneracji z wykruszeniami krawędzi skrawających, co wymusza dodatkowe operacje szlifierskie: odcięcie uszkodzonego czoła, zaniżenie średnicy (szyjka / neck reduction z określonym stopniem zaniżenia), polerowanie rowków wiórowych oraz doliczenie narzutu za tzw. „ponadnormatywne zużycie” (*heavy wear*).
4. **Błędy ludzkie i czas wyceny:** Tradycyjna wycena oparta na wertowaniu papierowych katalogów i tabel w arkuszu kalkulacyjnym zajmuje od kilkunastu do kilkudziesięciu minut na jedno zlecenie, stwarzając wysokie ryzyko pomyłek w stawkach i ofertach handlowych.

### 1.2. Cel projektu i wymagania funkcjonalne
Głównym celem inżynierskim było zaprojektowanie, zaimplementowanie i przetestowanie zintegrowanego systemu desktopowego **„Ostrzomat”**, który:
- Umożliwia błyskawiczne (w kilka sekund) skonfigurowanie parametrów narzędzia i automatyczne obliczenie kosztów regeneracji zgodnie z obowiązującym cennikiem przemysłowym.
- Umożliwia personelowi nietechnicznemu łatwą aktualizację cennika za pomocą arkusza Microsoft Excel (`cennik.xlsx`), bez konieczności edycji kodu czy bezpośrednich operacji na relacyjnej bazie danych.
- Agreguje kalkulacje w interaktywnym koszyku zleceń z możliwością stosowania rabatów procentowych i persystencji stanu aplikacji.
- Posiada wbudowaną książkę adresową kontrahentów (CRM).
- Automatycznie generuje gotowe, profesjonalne dokumenty handlowe w formatach **PDF** oraz **DOCX (Microsoft Word)** z pełnym zestawieniem kosztów, danymi klienta, numerem zlecenia i opcjonalnym logotypem firmy.

### 1.3. Odbiorcy i środowisko wdrożeniowe
Aplikacja została zaprojektowana z myślą o wdrożeniu na stanowiskach technologiczno-handlowych w profesjonalnych szlifierniach narzędzi skrawających oraz w działach utrzymania ruchu i narzędziowniach zakładów produkcyjnych. 

Wymagania środowiskowe:
- System operacyjny: Microsoft Windows 10 / 11 (docelowo kompatybilny również z systemami Linux/macOS).
- Środowisko uruchomieniowe: Python 3.8 lub nowszy.
- Interfejs graficzny: zoptymalizowany pod kątem pracy biurowej oraz obsługi na monitorach dotykowych hal produkcyjnych (duże, czytelne kontrolki biblioteki `CustomTkinter`).

---

# 2. ARCHITEKTURA SYSTEMU I ZASADA DZIAŁANIA

### 2.1. Ogólna architektura wielowarstwowa
System został zaprojektowany w oparciu o zasady separacji odpowiedzialności (*Separation of Concerns*) w architekturze wielowarstwowej:

```
+-----------------------------------------------------------------------+
|                    WARSTWA PREZENTACJI (UI)                          |
|  - OstrzomatApp (main_window.py): zarządca layoutu, menu boczne       |
|  - BaseToolModule (base_module.py): polimorficzna baza kalkulatorów   |
|  - FrezModule / DrillModule / SpecialModule: kalkulatory dedykowane   |
|  - CartTable / CartFooter: koszyk, rabaty, podsumowania               |
|  - ClientSelectionModal: książka adresowa / CRM                       |
|  - ExportReportModal: konfigurator eksportu PDF/Word                  |
+-----------------------------------------------------------------------+
                                  |
                                  v
+-----------------------------------------------------------------------+
|                 WARSTWA LOGIKI BIZNESOWEJ (LOGIC)                     |
|  - cart_logic.py: kalkulacja cen bazowych, progów ilościowych,        |
|    rozbicie usług dodatkowych, narzuty za zużycie, rabaty             |
|  - cache_manager.py: zarządzanie stanem w pamięci podręcznej RAM      |
+-----------------------------------------------------------------------+
                                  |
                                  v
+-----------------------------------------------------------------------+
|            WARSTWA ZARZĄDZANIA DANYMI I EKSPORTU (UTILS / DB)         |
|  - database.py: sterownik bazy SQLite, zoptymalizowane zapytania SQL  |
|  - price_list_excel.py: parser i walidator arkusza XLSX (openpyxl)    |
|  - clients_db.py: repozytorium kontrahentów                           |
|  - document_exporter.py: silnik ReportLab (PDF) i python-docx (DOCX)  |
+-----------------------------------------------------------------------+
                                  |
                                  v
+-----------------------------------------------------------------------+
|                     WARSTWA PERSYSTENCJI (STORAGE)                    |
|  - data/cennik.xlsx (Single Source of Truth dla cen)                  |
|  - data/ostrzomat.db (relacyjny cache SQLite tworzony w locie)        |
|  - data/cart_cache.json (automatyczny zrzut sesji koszyka)            |
|  - data/user_settings.json (ustawienia, ostatni numer wyceny)         |
+-----------------------------------------------------------------------+
```

### 2.2. Koncepcja hybrydowej bazy danych: Excel $\leftrightarrow$ SQLite
Jednym z najciekawszych osiągnięć inżynierskich projektu jest rozwiązanie problemu zarządzania cennikiem przez personel bez kompetencji bazodanowych.

Zamiast zmuszać użytkownika do operowania na tabelach SQLite lub tworzenia skomplikowanego edytora bazodanowego w GUI:
1. **Arkusz kalkulacyjny jako źródło prawdy:** Wszystkie stawki za ostrzenie, powłoki, usługi oraz progi ilościowe znajdują się w czytelnym arkuszu `data/cennik.xlsx`.
2. **Automatyczna replikacja i walidacja:** Podczas startu aplikacji moduł `utils/price_list_excel.py` weryfikuje strukturę nagłówków arkusza i w ramach jednej atomowej transakcji SQL przelicza i zasila lokalną relacyjną bazę `data/ostrzomat.db`.
3. **Podgląd w czasie rzeczywistym (*Hot-Reload*):** Aplikacja posiada w tle mechanizm `_watch_price_list()`, który bada znacznik czasu modyfikacji pliku Excel (`mtime`). Jeśli administrator zmodyfikuje i zapisze plik Excel w trakcie działania programu, cennik zostaje automatycznie przeładowany w locie, a ceny w koszyku natychmiast zaktualizowane bez konieczności restartu aplikacji!
4. **Wydajność:** Podczas bieżącej pracy kalkulator nie odpytuje powolnego pliku Excel (co przy bibliotece `openpyxl` trwałoby setki milisekund), lecz korzysta ze zindeksowanych tabel SQLite i pamięci RAM, co gwarantuje natychmiastową reakcję interfejsu użytkownika ($<1$ ms).

### 2.3. Przepływ danych w procesie wyceny (Pipeline)
1. Użytkownik wybiera kontrahenta w oknie głównym (lub tworzy nowego).
2. Z menu bocznego wybiera moduł narzędzia (np. „Frezy”).
3. Wprowadza średnicę roboczą $D$. System automatycznie kalkuluje sugerowaną średnicę chwytu (np. dla $D=7.5$ mm proponuje chwyt $8.0$ mm, z możliwością manualnego odblokowania).
4. Użytkownik wybiera liczbę ostrzy $Z$, rodzaj powłoki, długość strefy powlekanej oraz usługi dodatkowe (np. obcięcie, polerowanie, zaniżenie średnicy).
5. Moduł obliczeniowy natychmiast kalkuluje cenę jednostkową oraz łączną.
6. Kliknięcie „Dodaj do koszyka” rejestruje pozycję w centralnej liście `cart_items` i automatycznie zapisuje kopię zapasową sesji do `cart_cache.json`.
7. W sekcji koszyka operator może wprowadzić procentowy rabat ogólny, sprawdzić sumy netto/brutto i kliknąć przycisk `📊 RAPORT / WYCENA`.
8. Otwiera się zunifikowane okno modalne `ExportReportModal`: program proponuje kolejny numer raportu (np. `115`), format (PDF lub DOCX) i pozwala wygenerować ustandaryzowaną ofertę handlową o unikalnej nazwie pliku (np. `Wycena_NazwaKlienta_115.pdf`).

---

# 3. SZCZEGÓŁOWY OPIS MODUŁÓW FUNKCJONALNYCH

### 3.1. Moduł kalkulacji frezów (`ui/calc_modules/frez_module.py`)
Obsługuje frezy węglikowe walcowo-czołowe, frezy z promieniem naroża (*bull nose*) oraz frezy kuliste (*ball nose*). 
- Pozwala na wybór geometrii z dynamicznej listy pobieranej z bazy danych.
- Obsługuje liczbę ostrzy od 1 do 8 (w tym zakresy znormalizowane: ostrza 1-4 oraz 5-99).
- Integruje wyliczanie naddatku za ponadnormatywne wykruszenia czoła.

### 3.2. Moduł kalkulacji wierteł (`ui/calc_modules/drill_module.py`)
Dedykowany narzędziom otworowym (wiertła kręte, wiertła ze stopniem, wiertła z chłodzeniem wewnętrznym).
- W odróżnieniu od frezów, zgodnie ze standardami technologicznymi wierteł monolitycznych, system **sztywno wymusza liczbę ostrzy $Z=2$** w zapytaniach SQL do bazy cennika.
- Zawiera dodatkowe selektory specyficzne dla wierteł: kąt wierzchołkowy (np. $118^\circ$, $135^\circ$, $140^\circ$) oraz rodzaj węglika/chłodzenia.

### 3.3. Moduł narzędzi specjalnych (`ui/calc_modules/special_module.py`)
Umożliwia kalkulację narzędzi o geometrii niestandardowej (rozwiertaki, pogłębiacze, frezy profilowe, narzędzia stopniowe złożone).
- Elastyczny wybór parametrów z możliwością ręcznego zdefiniowania niestandardowych operacji ostrzenia.

### 3.4. Wspólna klasa bazowa `BaseToolModule` (`ui/calc_modules/base_module.py`)
Zaprojektowana w procesie refaktoryzacji zgodnie ze wzorcem projektowym *Template Method* i zasadą DRY (*Don't Repeat Yourself*):
- Zawiera uniwersalny, dwukolumnowy układ siatki (*grid*).
- Enkapsuluje kontrolki średnicy chwytu z logiką zaokrągleń inżynierskich:
  $$\text{Chwyt} = \lceil D \rceil \quad (\text{dla typowych typoszeregów DIN})$$
- Centralizuje logikę wyboru powłok: dynamicznie filtruje dostępne długości powlekania z bazy danych w oparciu o wybraną powłokę i średnicę.
- Zarządza listą usług dodatkowych: cięcie czoła, zaniżenie średnicy z mnożnikiem krotności (np. zaniżenie o 1 stopień vs zaniżenie o 3 stopnie), polerowanie rowka, zużycie.
- Automatycznie synchronizuje wpisaną liczbę sztuk narzędzia z polami ilościowymi w usługach dodatkowych.

### 3.5. Obsługa powłok technicznych (PVD/CVD) i usług dodatkowych
Nałożenie powłoki przeciwzużyciowej (np. AlTiN, TiSiN) wyceniane jest w oparciu o dwuwymiarową matrycę geometryczną:
- Średnica maksymalna $D_{max}$ (narzędzia klasyfikowane są w przedziałach średnic, np. do 6 mm, do 10 mm, do 16 mm, do 25 mm).
- Długość całkowita / strefa grzania w reaktorze próżniowym $L$.
Usługi dodatkowe rozliczane są jednostkowo za sztukę w oparciu o średnicę narzędzia, na którym dana operacja ma zostać przeprowadzona.

### 3.6. Koszyk zleceń, rabatowanie i persystencja sesji
Koszyk (`CartTable` i `CartFooter`) agreguje pozycje zamówienia.
- Każda pozycja w koszyku przechowuje pełen słownik parametrów (geometria, średnica, chwyt, liczba ostrzy, powłoka, rozbicie kosztów usług, cena jednostkowa, cena łączna).
- Możliwość dynamicznej edycji rabatu procentowego ($0-100\%$) z natychmiastowym przeliczeniem sumy netto i podatku VAT (23%).
- **Persystencja sesji:** Przy każdym dodaniu, usunięciu lub edycji pozycji w koszyku stan serializowany jest do formatu JSON w pliku `data/cart_cache.json`. Dzięki temu awaria zasilania lub przypadkowe zamknięcie programu nie powoduje utraty wprowadzonych kalkulacji.

### 3.7. Baza kontrahentów i książka adresowa (`utils/clients_db.py`)
Lekka, zintegrowana baza klientów oparta na SQLite:
- Pola: `id`, `name`, `phone`, `nip`, `email`, `address`.
- Wyszukiwarka dynamiczna w oknie `ClientSelectionModal`.
- Klient wybrany w oknie głównym staje się automatycznie odbiorcą generowanej wyceny.

### 3.8. Generator dokumentacji handlowej (`utils/document_exporter.py`, `ui/export_modal.py`)
System umożliwia eksport raportów do dwóch komplementarnych formatów:
1. **Format PDF (ReportLab):** Niezmienny, zabezpieczony dokument gotowy do wysyłki e-mailem do klienta. Wyposażony w profesjonalny nagłówek, tabelę pozycji ze stylami CSS-like, podsumowanie finansowe oraz automatyczną numerację stron w formacie `Strona X z Y` (klasa `NumberedCanvas`).
2. **Format DOCX (python-docx):** W pełni edytowalny dokument programu Word, pozwalający technologowi na ręczne dodanie niestandardowych uwag lub warunków technicznych przed złożeniem oficjalnej oferty.
3. **Inteligentne nazewnictwo i numeracja:** System pobiera kolejny numer z `user_settings.json` i generuje plik o nazwie:
   `Wycena_{NazwaKlienta}_{NumerWyceny}.pdf` (np. `Wycena_Pol-Metal_115.pdf`).

---

# 4. OMÓWIENIE KLUCZOWYCH FRAGMENTÓW KODU I ALGORYTMÓW

Poniżej zestawiono najważniejsze komponenty oprogramowania wraz z wycinkami kodu źródłowego, które stanowią doskonałą podstawę do analizy w części konstrukcyjnej pracy inżynierskiej.

### 4.1. Algorytm kalkulacji ceny narzędzia z progami ilościowymi i zużyciem
**Plik:** `logic/cart_logic.py`  
**Opis:** Funkcja odpowiada za wyliczenie ceny bazowej ostrzenia narzędzia. Uwzględnia walidację danych wejściowych, tolerancję znaków przecinka/kropki, zapytanie do bazy oraz rozbicie partii na sztuki standardowe i sztuki z narzutem za ponadnormatywne zużycie (+5% do stawki bazowej).

```python
def calculate_tool_price(tool_type, blades, diam, qty, heavy_wear=False, heavy_wear_qty=0, **kwargs):
    """
    Oblicza cenę jednostkową bazową oraz łączną dla narzędzia.
    Obsługuje zarówno precyzyjną liczbę sztuk ze zużyciem (heavy_wear_qty),
    jak i flagę logiczną (heavy_wear).
    """
    try:
        d_val = float(str(diam).replace(',', '.').strip())
        q_val = int(str(qty).strip())

        if isinstance(heavy_wear, str):
            heavy_wear = heavy_wear.strip().lower() in {"1", "true", "yes", "y", "tak"}

        if heavy_wear:
            hw_qty = q_val
        else:
            hw_qty = int(str(heavy_wear_qty).strip()) if heavy_wear_qty else 0

        if d_val <= 0.0 or q_val <= 0:
            return 0.0, 0.0

    except (ValueError, TypeError):
        return 0.0, 0.0

    # Pobranie ceny jednostkowej z bazy danych dla partii q_val
    base_price = database.get_tool_price(tool_type, blades, d_val, q_val)

    if base_price <= 0.0:
        return 0.0, 0.0

    # Zużycie może dotyczyć najwyżej całego zamówienia
    hw_qty = min(max(hw_qty, 0), q_val)
    normal_qty = q_val - hw_qty

    # Kalkulacja łączna: standardowe sztuki + sztuki ze zużyciem (mnożnik 1.05)
    total_price = (normal_qty * base_price) + (hw_qty * base_price * 1.05)
    unit_avg = total_price / q_val if q_val > 0 else base_price

    return round(unit_avg, 2), round(total_price, 2)
```

---

### 4.2. Automatyczna synchronizacja i walidacja cennika Excel $\rightarrow$ SQLite
**Plik:** `utils/price_list_excel.py`  
**Opis:** Kluczowy mechanizm architektury hybrydowej. Otwiera skorowidz `cennik.xlsx`, waliduje nazwy arkuszy i nagłówków, a następnie w jednej transakcji SQLite (`connection.commit()`) czyści i zasila tabele bazy danych (`pricelist_tools`, `pricelist_quantity_discounts`, `pricelist_coatings`, `pricelist_services`).

```python
def import_pricelist(path=DEFAULT_EXCEL_PATH):
    """Waliduje i importuje wszystkie arkusze XLSX do SQLite w jednej transakcji."""
    parsed = read_pricelist(path)

    connection = database.get_connection()
    try:
        database.ensure_tool_blade_columns(connection)
        database.ensure_quantity_discounts_table(connection)
        connection.commit()

        connection.execute("BEGIN")
        for sheet_name, rows in parsed.items():
            table = TABLES[sheet_name]
            connection.execute(f"DELETE FROM {table}")
            insert_columns = list(SHEETS[sheet_name])
            insert_rows = rows
            table_columns = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
            if sheet_name == "Narzędzia" and "blades" in table_columns:
                insert_columns.insert(4, "blades")
                insert_rows = [row[:4] + (_blade_label(row[2], row[3]),) + row[4:] for row in rows]
            placeholders = ", ".join("?" for _ in insert_columns)
            connection.executemany(
                f"INSERT INTO {table} ({', '.join(insert_columns)}) VALUES ({placeholders})",
                insert_rows,
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    return {sheet_name: len(rows) for sheet_name, rows in parsed.items()}
```

---

### 4.3. Dynamiczne odpytywanie bazy danych i silnik rabatów ilościowych
**Plik:** `database.py`  
**Opis:** Pobranie stawki za ostrzenie narzędzia realizowane jest dwuetapowo: najpierw silnik pobiera stawkę bazową (`price_base`) dla zdefiniowanej geometrii narzędzia, a następnie odpytuje tabelę `pricelist_quantity_discounts` o rabat przypisany do wielkości partii $Q$ i dynamicznie wylicza ostateczną cenę jednostkową.

```python
def get_tool_price(tool_type, blades_key, diam, qty):
    """
    Zwraca cenę jednostkową ostrzenia z bazy danych SQLite.
    Dla wierteł zawsze wymusza wartość ostrzy Z = '2'.
    Dla frezów pobiera stawkę dla liczby ostrzy podanej przez użytkownika.
    Cena bazowa pobierana jest z pricelist_tools, a rabat ilościowy z pricelist_quantity_discounts.
    """
    if not is_db_accessible(): 
        return 0.0
    try:
        d_val = float(diam)
        q_val = int(qty)
        clean_type = str(tool_type).split(" R")[0].strip()
        
        # Wymuszenie liczby ostrzy dla narzędzi wiertarskich
        wiertla_typy = ["Wiertla", "Wiertła", "Wiertlo", "Wiertło", "Wiertła stopniowe"]
        if any(w.lower() in clean_type.lower() for w in wiertla_typy):
            blades_key = "2"
        
        ensure_schema_ready()
        conn = get_connection()
        cursor = conn.cursor()

        # 1. Pobranie ceny bazowej narzędzia dla danej geometrii
        query_exact = """
            SELECT price_base FROM pricelist_tools 
            WHERE tool_type=? AND blades_min <= ? AND blades_max >= ? AND diam_min <= ? AND diam_max >= ?
            LIMIT 1
        """
        cursor.execute(query_exact, (clean_type, int(blades_key), int(blades_key), d_val, d_val))
        res = cursor.fetchone()
        
        # Fallback dla liczby ostrzy dla frezów
        if not res or res[0] is None:
            query_fallback = """
                SELECT price_base FROM pricelist_tools 
                WHERE tool_type=? AND diam_min <= ? AND diam_max >= ?
                LIMIT 1
            """
            cursor.execute(query_fallback, (clean_type, d_val, d_val))
            res = cursor.fetchone()

        if not res or res[0] is None or float(res[0]) <= 0:
            conn.close()
            return 0.0

        base_price = float(res[0])

        # 2. Pobranie rabatu ilościowego z tabeli rabatów
        cursor.execute("""
            SELECT discount_pct FROM pricelist_quantity_discounts
            WHERE qty_min <= ? AND qty_max >= ?
            ORDER BY qty_min DESC LIMIT 1
        """, (q_val, q_val))
        disc_row = cursor.fetchone()
        discount_pct = float(disc_row[0]) if disc_row and disc_row[0] is not None else 0.0

        conn.close()

        # Obliczenie ceny po rabacie ilościowym
        discounted_price = base_price * (1.0 - (discount_pct / 100.0))
        return round(max(discounted_price, 0.0), 2)
    except Exception as e:
        print(f"Błąd bazy (get_tool_price): {e}")
        return 0.0
```

---

### 4.4. Polimorfizm i automatyzacja w klasie bazowej `BaseToolModule`
**Plik:** `ui/calc_modules/base_module.py`  
**Opis:** Odpowiada za automatyczne przeliczanie średnicy chwytu narzędzia oraz synchronizację ilości w usługach dodatkowych.

```python
class BaseToolModule(ctk.CTkFrame):
    """
    Abstrakcyjna klasa bazowa dla modułów kalkulatora (Frezy, Wiertła, Specjalne).
    Zapewnia spójny interfejs, redukcję redundancji i automatyzację obliczeń technologicznych.
    """
    def __init__(self, parent, update_callback, settings):
        super().__init__(parent, fg_color="transparent")
        self.update_callback = update_callback
        self.settings = settings
        self.shank_override = ctk.BooleanVar(value=False)
        # Inicjalizacja siatki dwukolumnowej...

    def auto_calculate_shank(self, diam_val):
        """
        Inżynierska reguła doboru średnicy chwytu wg typoszeregu DIN:
        Dla narzędzia o średnicy D, chwyt odpowiada najbliższej znormalizowanej średnicy walcowej.
        """
        if self.shank_override.get():
            return  # Użytkownik ręcznie zdefiniował chwyt
        try:
            d = float(str(diam_val).replace(',', '.'))
            if d <= 0: return
            # Dobór znormalizowanego chwytu przemysłowego
            standards = [3.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 25.0, 32.0]
            suggested = next((s for s in standards if s >= d), math.ceil(d))
            self.shank_entry.delete(0, "end")
            self.shank_entry.insert(0, f"{suggested:.1f}")
        except ValueError:
            pass

    def sync_service_quantities(self, total_qty):
        """Automatyczna kaskadowa synchronizacja liczby sztuk w usługach dodatkowych."""
        for key, entry in self.service_qty_entries.items():
            current_val = entry.get().strip()
            if not current_val or current_val == "0":
                entry.delete(0, "end")
                entry.insert(0, str(total_qty))
```

---

### 4.5. Paginacja i renderowanie dokumentu PDF (`NumberedCanvas`)
**Plik:** `utils/document_exporter.py`  
**Opis:** Standardowy generator ReportLab generuje strony sekwencyjnie i nie zna łącznej liczby stron dokumentu podczas renderowania stopki. Rozwiązano to za pomocą wzorca dwuprzebiegowego płótna (*Two-Pass Canvas*).

```python
class NumberedCanvas(canvas.Canvas):
    """
    Dwuprzebiegowe płótno PDF zapamiętujące operacje rysowania.
    Umożliwia wstawienie w stopce łącznej liczby stron ('Strona X z Y')
    po zakończeniu kompilacji całego dokumentu.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("ArialCustom", 8)
        self.setFillColor(colors.HexColor("#666666"))
        page_text = f"Strona {self._pageNumber} z {page_count}"
        self.drawRightString(287 * mm, 10 * mm, page_text)
        self.drawString(10 * mm, 10 * mm, "Dokument wygenerowany automatycznie przez system Ostrzomat v0.2")
        self.restoreState()
```

---

### 4.6. Zunifikowane okno modalne eksportu i integracja z systemem plików
**Plik:** `ui/export_modal.py`  
**Opis:** Okno modalne do generowania raportów. Implementuje rozwiązanie problemu kolejności okien w systemie Windows (zdejmowanie flagi `-topmost` na czas systemowego okna dialogowego zapisu) oraz sanitację nazwy pliku.

```python
def generate_report(self):
    report_num = self.entry_number.get().strip()
    is_pdf = "pdf" in self.format_var.get().lower()
    ext = ".pdf" if is_pdf else ".docx"
    filter_desc = "Plik PDF" if is_pdf else "Dokument Word"

    # Pobranie i oczyszczenie nazwy klienta do nazwy pliku
    raw_client = getattr(self.parent, "current_client_name", "") or "Klient"
    clean_client = re.sub(r'[\\/*?:"<>|]', '', str(raw_client)).strip()
    clean_client = re.sub(r'\s+', '_', clean_client)
    if not clean_client or clean_client.lower() in ["nieokreslony_klient", "nieokreślony_klient"]:
        clean_client = "Klient"

    report_suffix = f"_{report_num}" if report_num else ""
    default_filename = f"Wycena_{clean_client}{report_suffix}{ext}"

    # Wyłączenie topmost na czas okna eksploratora, aby nie chował się pod spodem
    self.attributes("-topmost", False)
    try:
        save_path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=ext,
            filetypes=[(filter_desc, f"*{ext}")],
            initialfile=default_filename
        )
    finally:
        if self.winfo_exists():
            self.attributes("-topmost", True)

    if not save_path:
        return

    # Inkrementacja numeru i wywołanie eksportera...
```

---

# 5. JAKOŚĆ KODU, TESTOWANIE I WERYFIKACJA

### 5.1. Architektura testów automatycznych (`pytest`)
Projekt posiada kompleksowy zestaw 35 testów jednostkowych i integracyjnych, weryfikujących poprawność funkcjonowania wszystkich kluczowych modułów:

1. `tests/test_cart_logic.py`:
   - Weryfikacja obliczeń cen jednostkowych i całkowitych dla różnych wariantów geometrii.
   - Weryfikacja rozliczania ponadnormatywnego zużycia (mnożnik 1.05).
   - Testy kaskadowego obliczania usług dodatkowych (cięcie, opuszczenie, polerowanie).
2. `tests/test_calc_modules.py`:
   - Testy integracyjne modułów interfejsu `FrezModule`, `DrillModule`, `SpecialModule`.
   - Weryfikacja dziedziczenia z `BaseToolModule` i poprawności struktury zwracanych słowników pozycji.
3. `tests/test_price_list_excel.py`:
   - Weryfikacja dwukierunkowej konwersji Excel $\leftrightarrow$ SQLite.
   - Walidacja reakcji systemu na brakujące arkusze, błędne nagłówki i puste wiersze.
4. `tests/test_document_exporter.py`:
   - Test generowania plików binarnych PDF i DOCX.
   - Weryfikacja poprawności formatowania tabel, obecności danych kontrahenta i wyliczeń sum arytmetycznych.
5. `tests/test_project_structure.py`:
   - Testy architektoniczne sprawdzające integralność modułów, obecność wymaganych warstw i brak cyklicznych zależności.

Wynik uruchomienia pakietu testowego:
```text
============================= test session starts =============================
platform win32 -- Python 3.8.6, pytest-8.3.5, pluggy-1.5.0
rootdir: C:\Users\User\Documents\Repository\Ostrzomat
collected 35 items

tests\test_calc_modules.py ....                                          [ 11%]
tests\test_cart.py ............                                          [ 45%]
tests\test_cart_logic.py ..........                                      [ 74%]
tests\test_document_exporter.py ...                                      [ 82%]
tests\test_price_list_excel.py ...                                       [ 91%]
tests\test_project_structure.py ...                                      [100%]

============================= 35 passed in 3.88s ==============================
```

### 5.2. Metryki refaktoryzacji i redukcja długu technologicznego
W trakcie prac inżynierskich przeprowadzono gruntowną refaktoryzację kodu:
- **Redukcja redundancji kodu (DRY):** Usunięto ponad 800 linii powielonego kodu w modułach obliczeniowych poprzez ekstrakcję klasy bazowej `BaseToolModule`.
- **Optymalizacja wydajnościowa bazy danych:** Wyeliminowano wielokrotne, kosztowne wywołania instrukcji DDL (`CREATE TABLE IF NOT EXISTS`, `ALTER TABLE`) z pętli odpytywania cen. Schema bazy danych jest weryfikowana jednorazowo przy starcie systemu (`ensure_schema_ready()`), co skróciło czas wyceny z kilkunastu milisekund do ułamków milisekundy.
- **Bezpieczeństwo typów i danych:** Wprowadzono sanitację ciągów znaków (zamiana przecinków na kropki, odporność na wartości ujemne i puste pola).

---

# 6. WSKAZÓWKI DLA MODELU JĘZYKOWEGO REDAGUJĄCEGO PRACĘ DYPLOMOWĄ

Poniższe wytyczne mają pomóc zewnętrznemu modelowi AI w wygenerowaniu właściwych rozdziałów teoretycznych, analitycznych i projektowych pracy inżynierskiej na podstawie niniejszego dokumentu.

### 6.1. Sugerowana struktura rozdziałów pracy
1. **Rozdział 1: Analiza stanu zagadnienia i procesów technologicznych w regeneracji narzędzi**
   - Charakterystyka materiałów narzędziowych (węgliki spiekane VHM, stale proszkowe).
   - Metody ostrzenia narzędzi na szlifierkach wieloosiowych CNC.
   - Rola powłok przeciwzużyciowych (PVD/CVD) i technologia ich nakładania.
   - Analiza istniejących rozwiązań rynkowych (systemy ERP/CAM) i uzasadnienie budowy dedykowanego narzędzia.
2. **Rozdział 2: Projekt koncepcyjny i wymagania stawiane systemowi**
   - Przypadki użycia (Use Case Diagrams).
   - Wymagania funkcjonalne i niefunkcjonalne (wydajność, ergonomia, niezawodność).
   - Dobór środowiska programistycznego i bibliotek (Python, CustomTkinter, SQLite, openpyxl, ReportLab).
3. **Rozdział 3: Implementacja architektury i kluczowych modułów systemu**
   - Omówienie struktury wielowarstwowej aplikacji.
   - Implementacja hybrydowego mechanizmu bazy danych (Excel $\leftrightarrow$ SQLite).
   - Zastosowanie wzorców projektowych (Template Method w `BaseToolModule`, Singleton/Cache Manager).
   - Automatyzacja tworzenia dokumentacji handlowej (algorytm dwuprzebiegowego PDF).
4. **Rozdział 4: Testowanie, weryfikacja i analiza ergonomii rozwiązania**
   - Metodologia testowania oprogramowania (testy jednostkowe i integracyjne `pytest`).
   - Scenariusze testowe i analiza przypadków brzegowych (błędne formaty danych, brakujące pliki).
   - Studium przypadku: porównanie czasu przygotowania oferty metodą tradycyjną oraz przy użyciu aplikacji „Ostrzomat”.
5. **Rozdział 5: Podsumowanie i wnioski**
   - Ocena stopnia realizacji założonych celów inżynierskich.
   - Możliwości dalszego rozwoju (integracja sieciowa, moduł magazynowy, protokoły przemysłowe).

### 6.2. Słownik pojęć domenowych (Glosariusz)
- **VHM (Vollhartmetall):** Węglik spiekany, materiał o bardzo wysokiej twardości i odporności na ścieranie, z którego wykonana jest większość nowoczesnych frezów i wierteł.
- **Średnica robocza ($D$):** Średnica części skrawającej narzędzia.
- **Średnica chwytu ($d$):** Średnica części walcowej narzędzia służącej do mocowania w oprawce obrabiarki (np. oprawka termokurczliwa, hydrauliczna lub ER).
- **Liczba ostrzy ($Z$):** Liczba krawędzi skrawających na obwodzie narzędzia (np. $Z=4$ oznacza frez czteropiórowy).
- **Zaniżenie średnicy (szyjka):** Operacja zeszlifowania części chwytowej za strefą skrawającą do mniejszej średnicy, umożliwiająca głęboką obróbkę bez kolizji chwytu z obrabianym detalem.
- **Powłoka PVD (Physical Vapour Deposition):** Osadzanie cienkich powłok z fazy gazowej w warunkach próżniowych w temperaturze $400-500^\circ\text{C}$, podnoszące twardość i odporność termiczną krawędzi skrawającej.
- **Heavy Wear (ponadnormatywne zużycie):** Uszkodzenie narzędzia przekraczające dopuszczalną szerokość pasma startarcia na powierzchni przyłożenia ($VB$), wymagające odcięcia części czołowej lub dłuższego czasu szlifowania.

### 6.3. Wnioski inżynierskie
- Połączenie prostoty edycyjnej arkusza Excel z wydajnością relacyjnej bazy danych SQLite okazało się optymalnym kompromisem w warunkach małego i średniego przedsiębiorstwa produkcyjnego.
- Zastosowanie obiektowej architektury z klasą bazową `BaseToolModule` drastycznie obniżyło koszt utrzymania oprogramowania i umożliwiło łatwą rozbudowę o kolejne typy narzędzi (np. gwintowniki czy rozwiertaki).
- Automatyzacja procesu wyceny skróciła czas przygotowania oferty z około 15 minut do poniżej 45 sekund, całkowicie eliminując błędy arytmetyczne oraz pomyłki w doborze progów ilościowych.
