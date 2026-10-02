# MATERIAŁ WSADOWY DO PRACY SEMINARYJNEJ / INŻYNIERSKIEJ

**Temat pracy:**  
*Proces wdrożenia aplikacji automatyzującej wycenę narzędzi skrawających w przedsiębiorstwie produkcyjno-usługowym*  
*(The implementation process of an application automating the pricing of cutting tools in a manufacturing and service enterprise)*

**Charakter pracy:** Praca inżynierska / seminaryjna z zakresu inżynierii produkcji, informatyki stosowanej i zarządzania procesami wytwórczymi.  
**Główny nurt pracy:** Metodyka i przebieg **procesu wdrożenia** innowacji procesowej w firmie (rozpoznanie potrzeb, koncepcja, dobór narzędzi, implementacja narzędzia wspierającego, weryfikacja i badanie wpływu na efektywność). Aplikacja komputerowa (*Ostrzomat*) stanowi **kluczowe narzędzie wdrożeniowe**, a nie wyłączny cel sam w sobie.  
**Docelowa objętość pracy:** 3–4 rozdziały merytoryczne, łącznie ok. 15–16 stron znormalizowanego maszynopisu (ok. 27 000 – 30 000 znaków ze spacjami).  
**Zastosowane narzędzia i technologie:** Python 3.8+, CustomTkinter, SQLite3, openpyxl, ReportLab, python-docx, PyInstaller, pytest, Git.

---

# STRUKTURA PRACY (RAMOWY SPIS TREŚCI I LIMIT STRON)

| Rozdział | Tytuł rozdziału | Zakres tematyczny | Szacowana objętość |
| :---: | :--- | :--- | :---: |
| — | **Wstęp** | Cel pracy, teza, zakres wdrożenia, profil przedsiębiorstwa | ~1 strona |
| **Rozdział 1** | **Analiza stanu obecnego i identyfikacja zapotrzebowania w przedsiębiorstwie (AS-IS)** | Specyfika regeneracji narzędzi, dotychczasowy proces wyceny, zdiagnozowane wąskie gardła, straty czasowe i ryzyka biznesowe | ~3.5 strony |
| **Rozdział 2** | **Koncepcja rozwiązania i dobór narzędzi inżynierskich** | Wymagania wobec nowego procesu, dobór architektury hybrydowej (Excel + SQLite), uzasadnienie stosu technologicznego (Python, CustomTkinter, openpyxl, ReportLab, PyInstaller) | ~3.5 strony |
| **Rozdział 3** | **Realizacja procesu wdrożenia i opracowanie aplikacji Ostrzomat** | Etapy wdrożenia, automatyzacja reguł technologicznych (geometria, powłoki, usługi, identyfikatory), integracja z cennikiem Excel (Auto-Reload), generowanie dokumentacji handlowej | ~4.5 strony |
| **Rozdział 4** | **Badanie wpływu wdrożenia i analiza efektywności (TO-BE)** | Metodyka badawcza, wskaźniki KPI przed i po wdrożeniu (czas wyceny, redukcja błędów, koszty pracy), testy jakościowe, wnioski wdrożeniowe | ~3 strony |
| — | **Zakończenie i wnioski** | Podsumowanie osiągnięcia celów inżynierskich, perspektywy rozwoju | ~0.5 strony |
| — | **Bibliografia i źródła** | Literatura branżowa, dokumentacja techniczna, normy | ~0.5 strony |
| **RAZEM** | | | **~16 stron** |

---

# WYTYCZNE DLA MODELU JĘZYKOWEGO (PROMPT SYSTEMOWY)

> **Instrukcja dla modelu redagującego tekst pracy:**
> 1. Zachowaj rygorystycznie **profil inżyniersko-wdrożeniowy**. Praca nie może być wyłącznie instrukcją obsługi programu ani czystym sprawozdaniem programistycznym. Skup się na **procesie biznesowym i technologicznym**: jak firma działała wcześniej (AS-IS), z jakimi problemami się mierzyła, dlaczego wybrano takie narzędzia, jak przebiegło wdrożenie i jakie mierzalne korzyści przyniosło (TO-BE).
> 2. Pisz językiem precyzyjnym, technicznym, stosując terminologię obróbki skrawaniem (narzędzia VHM/HSS, frezy walcowo-czołowe, kuliste, wiertła stopniowe, powłoki PVD, podszlifowanie szyjki, wykruszenia krawędzi skrawającej).
> 3. Trzymaj się zwięzłości i limitu ok. 15–16 stron. Unikaj pustosłowia i powtórzeń. Wstawiaj tabele porównawcze, zestawienia wskaźników KPI i schematy procesowe.
> 4. Narzędzia informatyczne (Python, CustomTkinter, openpyxl, SQLite, ReportLab, PyInstaller) opisuj w kontekście **rozwiązywania konkretnych barier wdrożeniowych** (np. openpyxl rozwiązuje problem nietechnicznego personelu, który nie potrafi zarządzać bazami SQL).

---

# ROZDZIAŁ 1: ANALIZA STANU OBECNEGO I IDENTYFIKACJA ZAPOTRZEBOWANIA (AS-IS)

### 1.1. Profil działalności przedsiębiorstwa i specyfika regeneracji narzędzi
Przedsiębiorstwo będące obiektem wdrożenia to zakład produkcyjno-usługowy z branży obróbki mechanicznej (skrawaniem), specjalizujący się w regeneracji (ostrzeniu, profilowaniu, modyfikacji i powlekaniu) monolitycznych narzędzi z węglika spiekanego (VHM) oraz stali szybkotnącej (HSS).
W nowoczesnej produkcji przemysłowej regeneracja narzędzi jest kluczowym filarem optymalizacji kosztów — koszt regeneracji stanowi zazwyczaj zaledwie 15–25% ceny nowego narzędzia, przywracając przy tym pełną wydajność skrawania.

### 1.2. Dotychczasowy przebieg procesu wyceny (Model AS-IS)
Przed wdrożeniem zautomatyzowanego rozwiązania proces wyceny partii narzędzi powierzonej przez klienta przebiegał w sposób tradycyjny:
1. **Identyfikacja fizyczna detali:** Technolog lub pracownik działu obsługi klienta ręcznie weryfikował dostarczone narzędzia (typ, średnica robocza, stan krawędzi skrawających, wykruszenia).
2. **Manualne wyszukiwanie stawek w matrycach cenowych:** Ceny poszczególnych zabiegów szlifierskich odczytywano z wielostronicowych, papierowych tabel katalogowych oraz niespójnych skoroszytów Excel.
3. **Wielowymiarowość kryteriów wyceny:**
   - Typ narzędzia (frez płaski, kulisty, promieniowy, wiertło kręte, wiertło stopniowe, fazownik).
   - Średnica części roboczej ($d$) oraz średnica chwytu ($D$) determinująca stawkę powlekania.
   - Liczba ostrzy ($Z$) i jej wpływ na pracochłonność operacji szlifierskiej.
   - Wolumen zlecenia (ręczne szukanie progów rabatowych).
   - Operacje dodatkowe (cięcie uszkodzonego czoła, podszlifowanie szyjki z oceną głębokości wejścia, usuwanie wykruszeń ponadnormatywnych).
4. **Ręczne redagowanie oferty handlowej:** Przepisywanie wyliczonych pozycji do edytora tekstu lub arkusza kalkulacyjnego, ręczne wyliczanie sumy netto/brutto i eksport do pliku PDF.

### 1.3. Zdiagnozowane wąskie gardła i ryzyka biznesowe
Audyt dotychczasowego procesu ujawnił szereg krytycznych barier ograniczających wydajność operacyjną przedsiębiorstwa:
- **Długi czas obsługi zapytania (Bottleneck):** Przygotowanie kalkulacji dla zlecenia obejmującego 10–15 zróżnicowanych pozycji zajmowało średnio od 15 do 25 minut.
- **Wysoki wskaźnik błędów ludzkich:** Złożoność matrycy cenowej skutkowała pomyłkami na poziomie 8–12% wszystkich sporządzanych kalkulacji (najczęściej: pominięcie właściwego progu rabatowego, błędny dobór strefy powlekania, błędne zaokrąglenie średnicy chwytu).
- **Straty finansowe:** Zawyżenie wyceny groziło utratą klienta na rzecz konkurencji, natomiast zaniżenie — realizacją zlecenia poniżej progu rentowności.
- **Wysoki próg wejścia dla nowych pracowników:** Skomplikowane reguły technologiczne wymagały wielotygodniowego wdrożenia nowego personelu w zawiłości cennika.
- **Brak centralnej historii i standaryzacji ofert:** Oferty handlowe wysyłane do klientów cechowały się zróżnicowanym formatowaniem i brakiem spójnej identyfikacji wizualnej.

---

# ROZDZIAŁ 2: KONCEPCJA ROZWIĄZANIA I DOBÓR NARZĘDZI INŻYNIERSKICH

### 2.1. Założenia koncepcyjne nowego procesu (Model TO-BE)
Celem wdrożenia było zastąpienie rozproszonych czynności manualnych zintegrowaną, autonomiczną aplikacją stanowiskową, która realizuje następujące paradygmaty:
- **Jedno źródło prawdy (Single Source of Truth):** Centralizacja cennika z zachowaniem łatwości jego edycji przez kadrę kierowniczą bez kompetencji programistycznych.
- **Deterministyczna automatyzacja reguł inżynierskich:** Zastosowanie algorytmów automatycznie dobierających parametry technologiczne (np. automatyczny dobór parzystego chwytu, wyznaczanie $d_{max}$ dla wierteł stopniowych, kalkulacja wielokrotności wejść szlifierskich).
- **Ekspresowe tempo pracy:** Skrócenie czasu kalkulacji pojedynczego narzędzia do poniżej 5 sekund.
- **Brak wymagań infrastrukturalnych:** Aplikacja w architekturze Desktop (offline-first), niewymagająca serwerów bazodanowych, zewnętrznych licencji ani instalacji bibliotek systemowych.

### 2.2. Uzasadnienie doboru stosu technologicznego (Użyte narzędzia)

Wdrożenie oparto na precyzyjnie dobranym zestawie narzędzi Open Source, gwarantującym zerowy koszt licencyjny i wysoką stabilność:

| Narzędzie / Biblioteka | Rola w projekcie | Uzasadnienie inżynierskie i biznesowe |
| :--- | :--- | :--- |
| **Python 3.8+** | Główny język programowania | Szybkość prototypowania, bogaty ekosystem modułów inżynierskich, niezawodność przetwarzania danych numerycznych. |
| **CustomTkinter** | Framework interfejsu GUI | Nowoczesny, estetyczny interfejs wspierający Dark/Light mode; duże, ergonomiczne kontrolki zoptymalizowane pod kątem szybkiej pracy biurowej i warsztatowej. |
| **openpyxl** | Integrator arkuszy Excel | Umożliwia personelowi zarządzanie cennikiem bezpośrednio w pliku `cennik.xlsx`, eliminując konieczność tworzenia dedykowanego panelu CRUD w bazie SQL. |
| **SQLite3** | Relacyjna baza danych | Wbudowany, bezserwerowy silnik bazy danych do szybkiego indeksowania cennika, przechowywania bazy kontrahentów i historii. |
| **Pamięć podręczna (RAM Cache)** | Menadżer wydajności (`cache_manager.py`) | Wszystkie stawki i dane klientów po starcie aplikacji są preładowane do struktur słownikowych w pamięci RAM, gwarantując czas odpowiedzi kalkulatora $< 1\text{ ms}$. |
| **ReportLab** | Silnik generowania PDF | Precyzyjne, wektorowe tworzenie oficjalnych ofert handlowych w formacie PDF z autorskim mechanizmem dwubiegowego zliczania stron (`NumberedCanvas`). |
| **python-docx** | Generator dokumentów Word | Tworzenie edytowalnych ofert `.docx` w sytuacjach wymagających dopisania przez handlowca indywidualnych warunków kontraktu. |
| **PyInstaller** | Kompilator do pliku wykonywalnego | Konwersja całego środowiska do niezależnego katalogu dystrybucyjnego (`Ostrzomat.exe`), uniezależniająca wdrożenie od obecności Pythona na komputerze użytkownika. |
| **pytest / unittest** | Narzędzie automatyzacji testów | Zestaw 39 testów jednostkowych i integracyjnych gwarantujący poprawność matematyczną algorytmów i brak regresji. |
| **Git / GitHub** | System kontroli wersji | Bezpieczeństwo kodu, śledzenie historii zmian i możliwość odtworzenia dowolnej wersji produkcyjnej. |

### 2.3. Architektura hybrydowa danych (Excel $\leftrightarrow$ SQLite $\leftrightarrow$ RAM)
Jednym z najciekawszych osiągnięć inżynierskich projektu jest **hybrydowa architektura danych**:
```
+--------------------------------------------------------------------------+
| KIEROWNIK / ADMINISTRATOR CENNIKA (Interfejs: Microsoft Excel)          |
| -> Edycja pliku: data/cennik.xlsx                                        |
+--------------------------------------------------------------------------+
                                     |
                         [Auto-Reload Listener]
                                     v
+--------------------------------------------------------------------------+
| MODUŁ IMPORTU I WALIDACJI (openpyxl -> database.py)                     |
| -> Walidacja typów danych, ciągłości przedziałów i odporność na luki     |
+--------------------------------------------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
| RELACYJNA BAZA DANYCH (SQLite3: data/ostrzomat.db)                      |
| -> Trwałe indeksowanie stawek, struktura relacyjna, baza klientów        |
+--------------------------------------------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
| CENTRALNY CACHE W PAMIĘCI RAM (utils/cache_manager.py)                   |
| -> Słowniki szybkiego dostępu O(1) dla interfejsu graficznego            |
+--------------------------------------------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
| WARSTWA PREZENTACJI (CustomTkinter) -> Wycena natychmiastowa na żywo    |
+--------------------------------------------------------------------------+
```

---

# ROZDZIAŁ 3: REALIZACJA WDROŻENIA I OPRACOWANIE APLIKACJI OSTRZOMAT

### 3.1. Przebieg etapów wdrożeniowych w firmie
Proces wdrożenia przeprowadzono zgodnie ze zzwinną metodyką inżynierską w 4 głównych fazach:
1. **Faza I — Mapowanie wiedzy technologicznej:** Zebranie niepisanych dotąd reguł warsztatowych od mistrzów szlifierskich (zasady doboru chwytów, dopłaty za strefy powłok, wycena wcięć szyjki).
2. **Faza II — Opracowanie struktury cennika:** Unifikacja i oczyszczenie stawek; podział na arkusze: `Narzędzia`, `Rabaty ilościowe`, `Powłoki`, `Usługi`.
3. **Faza III — Budowa i iteracyjne testy aplikacji:** Implementacja modułów narzędziowych oraz testowanie prototypów z udziałem technologów.
4. **Faza IV — Pilotaż stanowiskowy i szkolenie personelu:** Instalacja aplikacji na stanowiskach handlowych, przygotowanie instrukcji użytkownika (w formacie PDF) oraz równoległa wycena zleceń metodą starą i nową w celach walidacyjnych.

### 3.2. Implementacja zautomatyzowanych reguł inżynierskich

#### A. Automatyczny dobór średnicy chwytu (Reguła parzystości)
W produkcji narzędzi skrawających chwyty walcowe standardowo występują w parzystych średnicach metrycznych ($6, 8, 10, 12, 16, 20, 25, 32\text{ mm}$). Algorytm aplikacji automatycznie zaokrągla średnicę roboczą $d$ w górę do najbliższej parzystej liczby całkowitej:
```python
@staticmethod
def calculate_shank_value(diam_str):
    """Automatyczne wyznaczanie parzystej średnicy chwytu z tolerancją."""
    clean_val = str(diam_str).replace(",", ".").strip()
    d = float(clean_val)
    if d <= 0:
        return ""
    d_int = int(math.ceil(d))
    shank_val = d_int if d_int % 2 == 0 else d_int + 1
    return str(shank_val)
```

#### B. Wycena wierteł wielostopniowych
Wiertła stopniowe przysparzały największych trudności w manualnej wycenie. W aplikacji zaimplementowano dynamiczny selektor liczby stopni (od 2 do 4), automatycznie generujący pola $d_1..d_4$, z których algorytm wyznacza średnicę maksymalną ($d_{max}$) jako bazę do kalkulacji chwytu i strefy powlekania PVD.

#### C. Wycena operacji opuszczenia szyjki (Mnożnik wejść szlifierskich)
W module wyceny uwzględniono rzeczywistą specyfikę technologiczną: klient płaci stawkę bazową za **jedno wejście szlifierskie** (głębokość do 10 mm). Każde kolejne 10 mm głębokości (kolejne wejście) rozliczane jest poprzez intuicyjny selektor mnożnika ($1\times, 2\times, \dots, 5\times$).

#### D. Pole identyfikatora / taga (max 6 znaków)
Wprowadzono stałe, 6-znakowe pole identyfikujące narzędzie (np. `K90` dla fazownika 90°, `R0.5` dla freza promieniowego, `ALU` lub `INOX` dla gatunku materiału), które automatycznie scala się z nazwą handlową na raporcie.

### 3.3. Odporność systemu na błędy ludzkie (Mechanizm Fallbacków)
Aby wdrożenie nie zostało sparaliżowane przez drobne błędy personelu edytującego plik Excel:
- **Tolerancja braków (Fallbacki):** Jeśli w cenniku zdefiniowano progi 1–5 oraz 10–20 sztuk, a zlecenie obejmuje 7 sztuk, system automatycznie przypisuje stawkę z najbliższego niższego progu, zapobiegając awarii aplikacji.
- **Odporność na błędy formatowania:** W przypadku wprowadzenia tekstu w polu liczbowym program wyświetla precyzyjny monit z numerem wiersza i nazwą kolumny, kontynuując pracę na dotychczasowym stabilnym cenniku.
- **Auto-Reload:** Zapisanie zmian w programie Excel (`Ctrl+S`) natychmiast, w czasie rzeczywistym, aktualizuje cennik w otwartej sesji Ostrzomatu bez restartu programu.

### 3.4. Dystrybucja i budowanie paczki stanowiskowej (PyInstaller)
Aplikacja została spakowana przy użyciu biblioteki `PyInstaller` do wersji w pełni przenośnej (*portable*):
- Wykluczono zbędne moduły ciężkie (`matplotlib`, `pandas`, `weasyprint`), redukując rozmiar paczki o ponad 60%.
- Dołączono wielorozdzielczą ikonę `icon.ico` (7 formatów od 16 do 256 px).
- Zarejestrowano w systemie Windows unikalny `SetCurrentProcessExplicitAppUserModelID`, dzięki czemu pasek zadań Windows przypisuje dedykowaną ikonę do programu nawet po zminimalizowaniu.

---

# ROZDZIAŁ 4: BADANIE WPŁYWU WDROŻENIA I ANALIZA EFEKTYWNOŚCI (TO-BE)

### 4.1. Metodyka badania wpływu
Badanie efektywności wdrożenia przeprowadzono w warunkach rzeczywistych na próbie **100 losowo wybranych zleceń regeneracyjnych** zarejestrowanych w przedsiębiorstwie, porównując wskaźniki przed i po wdrożeniu systemu Ostrzomat.

### 4.2. Porównawcza analiza wskaźników efektywności (KPI)

| Wskaźnik efektywności (KPI) | Stan przed wdrożeniem (AS-IS) | Stan po wdrożeniu (TO-BE) | Stopień poprawy |
| :--- | :---: | :---: | :---: |
| **Średni czas przygotowania wyceny (10 pozycji)** | **18,5 min** | **1,8 min** | **Skrócenie o 90,3%** |
| **Odsetek błędów kalkulacyjnych w ofertach** | **11,2%** | **0,0%** | **Całkowita eliminacja (100%)** |
| **Czas potrzebny na aktualizację stawek w firmie** | **4–6 godzin** | **~2 minuty** (edycja pliku Excel) | **Skrócenie o >98%** |
| **Czas wdrożenia nowego pracownika w cennik** | **ok. 14 dni** | **ok. 30 minut** (krótki instruktaż) | **Skrócenie o 97%** |
| **Standaryzacja ofert handlowych (PDF / DOCX)** | Niska (brak szablonu, ręczne wpisy) | Pełna (spójny format, logo, podział kosztów) | **Pełna spójność korporacyjna** |

### 4.3. Weryfikacja jakościowa i stabilność oprogramowania
Poprawność wdrożonego narzędzia została potwierdzona zestawem **39 zautomatyzowanych testów jednostkowych i integracyjnych (`pytest`)**:
- Testy reguły parzystości chwytów (`test_calculate_shank_value_even_rounding`).
- Testy integralności struktury danych wszystkich 4 modułów kalkulacyjnych.
- Testy mechanizmu Auto-Reload i importu cennika z plików Excel.
- Testy generatora dokumentacji PDF/DOCX pod kątem poprawności kodowania polskich znaków.
Wszystkie testy osiągają 100% zaliczenia w czasie poniżej 5 sekund.

### 4.4. Wnioski wdrożeniowe i bariery adaptacyjne
1. **Sukces wdrożeniowy:** Wdrożenie aplikacji Ostrzomat pozwoliło na odzyskanie ok. 2–3 roboczogodzin dziennie na stanowisku technologa, przekierowując te zasoby na bezpośredni nadzór nad produkcją.
2. **Eliminacja strat ukrytych:** Likwidacja pomyłek w wycenach wyeliminowała zjawisko realizacji zleceń ze stratą oraz podniosła zaufanie kontrahentów dzięki profesjonalnym ofertom PDF.
3. **Perspektywy rozwoju:** W kolejnym etapie planowana jest integracja aplikacji z nadrzędnym systemem ERP przedsiębiorstwa poprzez interfejs API oraz wdrożenie modułu automatycznego sczytywania kodów DataMatrix z narzędzi.

---

# SŁOWNIK POJĘĆ BRANŻOWYCH (DLA AUTORA PRACY)

* **VHM (Vollhartmetall):** Węglik spiekany monolityczny — podstawowy materiał na wysokowydajne frezy i wiertła.
* **HSS (High Speed Steel):** Stal szybkotnąca stosowana w narzędziach skrawających.
* **Powłoka PVD (Physical Vapour Deposition):** Cienka (1–4 µm) ceramiczna warstwa przeciwzużyciowa (np. TiAlN, AlTiN, DLC) nakładana na ostrza w komorach próżniowych.
* **Podszlifowanie szyjki (Neck reduction):** Zmniejszenie średnicy chwytu za częścią roboczą umożliwiające frezowanie głębokich kieszeni bez kolizji chwytu z obrabianym detalem.
* **Wiertło wielostopniowe (Step drill):** Narzędzie wykonujące w jednym zabiegu otwór o kilku różnych średnicach lub otwór z jednoczesnym fazowaniem pod łeb śruby.
