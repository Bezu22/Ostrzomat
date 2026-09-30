# System Ostrzomat v0.2 — Podręcznik Użytkownika & Instrukcja Obsługi Cennika

**Wersja:** 0.2 (Wydanie produkcyjne)  
**Data opracowania:** Wrzesień 2026 r.  
**Format dokumentu:** Podręcznik stanowiskowy / Dokumentacja operacyjna  
**Plik PDF z wersją do druku:** [`docs/Instrukcja_Uzytkownika_Ostrzomat.pdf`](file:///c:/Users/User/Documents/Repository/Ostrzomat/docs/Instrukcja_Uzytkownika_Ostrzomat.pdf)

---

## Spis treści
1. [Wprowadzenie i architektura systemu](#1-wprowadzenie-i-architektura-systemu)
2. [Interfejs użytkownika i obsługa wyceny](#2-interfejs-użytkownika-i-obsługa-wyceny)
3. [Moduły kalkulacyjne narzędzi — Parametry i funkcje](#3-moduły-kalkulacyjne-narzędzi--parametry-i-funkcje)
4. [Instrukcja edycji pliku cennika (data/cennik.xlsx)](#4-instrukcja-edycji-pliku-cennika-datacennikxlsx)
5. [Generowanie ofert i eksport dokumentów](#5-generowanie-ofert-i-eksport-dokumentów)
6. [FAQ & Rozwiązywanie problemów (Troubleshooting)](#6-faq--rozwiązywanie-problemów-troubleshooting)

---

## 1. Wprowadzenie i architektura systemu

### 1.1. Przeznaczenie programu
System **Ostrzomat** to specjalistyczna aplikacja stworzona w celu automatyzacji, standaryzacji oraz przyspieszenia procesu kalkulacji kosztów ostrzenia, modyfikacji, regeneracji i powlekania narzędzi skrawających z węglika spiekanego (VHM) oraz stali szybkotnącej (HSS).

Aplikacja eliminuje konieczność ręcznego przeliczania stawek z papierowych lub rozproszonych tabel cennikowych, automatyzuje obliczenia matematyczne (np. regułę parzystości chwytów, strefy powlekania, mnożniki podszlifów szyjki czy rabatowanie ilościowe) i pozwala w kilka sekund wygenerować spójną ofertę handlową w formatach **PDF** oraz **Microsoft Word (.docx)**.

### 1.2. Struktura plików i katalogów
Aplikacja działa w modelu lokalnym (baza danych i cennik znajdują się na stanowisku roboczym):

| Plik / Katalog | Opis i przeznaczenie |
| :--- | :--- |
| `Ostrzomat.exe` (lub `main.py`) | Główny plik uruchomieniowy programu. |
| `icon.ico` | Ikona aplikacji (wersja wielorozdzielcza od 16x16 do 256x256 px). |
| `data/` | **Kluczowy katalog danych.** Musi znajdować się w tym samym folderze co plik wykonywalny! |
| `data/cennik.xlsx` | Arkusz kalkulacyjny ze stawkami ostrzenia, powłok, usług i rabatów. Użytkownik ma pełną swobodę jego edycji. |
| `data/ostrzomat.db` | Baza SQLite przechowująca zindeksowany cennik, bazę klientów i historię. |
| `data/cart_state.json` | Automatycznie zapisywany stan bieżącego koszyka (zapobiega utracie danych przy przypadkowym zamknięciu). |

---

## 2. Interfejs użytkownika i obsługa wyceny

Ekran programu podzielony jest na logiczne obszary robocze:
1. **Pasek boczny (Sidebar)** — menu wyboru modułów kalkulacyjnych oraz narzędzia zarządzania plikiem cennika.
2. **Pasek górny (Nagłówek kontrahenta)** — wybór i podgląd aktywnego klienta.
3. **Tabela wyceny (Koszyk)** — centralny obszar roboczy prezentujący listę wycenianych pozycji.
4. **Stopka koszyka (Pasek akcji)** — operacje na zaznaczonych pozycjach, zapis/czyszczenie koszyka, eksport dokumentów i podsumowanie finansowe.

### 2.1. Pasek boczny (Sidebar)
* **[➕ DODAJ FREZ]**: Otwiera kalkulator dedykowany frezom walcowo-czołowym, z czołem kulistym, promieniowym oraz frezom zgrubnym.
* **[➕ DODAJ WIERTŁO]**: Otwiera kalkulator wierteł krętych monolitycznych oraz wierteł wielostopniowych (od 2 do 4 stopni średnic).
* **[➕ DODAJ INNE]**: Moduł dedykowany fazownikom, pogłębiaczom stożkowym i frezom z promieniem wewnętrznym (wklęsłym).
* **[➕ DODAJ SPECJALNE]**: Umożliwia wycenę narzędzi niestandardowych, zmodyfikowanych i prototypów z ręcznym określeniem stawki jednostkowej.
* **[⚙ CENNIK]**: Bezpośrednio otwiera plik `data/cennik.xlsx` w programie Microsoft Excel w celu edycji stawek.
* **[↻ SPRAWDŹ I PRZEŁADUJ CENNIK]**: Ręczne wymuszenie ponownej walidacji i załadowania cennika do pamięci podręcznej programu.

### 2.2. Pasek górny (Wybór kontrahenta)
* **Przycisk [👤 Klient: ...]**: Znajduje się w górnej belce nad tabelą koszyka. Kliknięcie otwiera wyszukiwarkę kontrahentów z bazy danych z możliwością natychmiastowego dodania nowej firmy (Nazwa, NIP, Adres, Telefon, E-mail).

### 2.3. Tabela wyceny i operacje w stopce (Koszyk pozycji)
Tabela w centralnej części okna prezentuje listę wszystkich skalkulowanych narzędzi. Każdy wiersz zawiera dokładne rozbicie kosztów: cenę jednostkową i łączną za ostrzenie, powłokę oraz usługi dodatkowe.

**Zasady obsługi pozycji w koszyku:**
1. **Edycja pozycji:** Aby edytować pozycję, zaznacz dany wiersz w tabeli (klikając na niego), a następnie kliknij przycisk **[Edytuj pozycję]** znajdujący się w stopce pod tabelą. Wszystkie parametry narzędzia zostaną załadowane z powrotem do formularza kalkulatora.
2. **Usuwanie pozycji:** Zaznacz pozycję i kliknij przycisk **[Usuń zaznaczone]** lub czerwoną ikonę usuwania na końcu wiersza.
3. **Uwagi techniczne [📝 Uwagi]:** Zaznacz pozycję i kliknij przycisk uwag, aby wprowadzić uwagi technologiczne. Wprowadzone uwagi znajdą się bezpośrednio na raporcie końcowym obok nazwy pozycji.
4. **Zarządzanie koszykiem:** W stopce dostępne są przyciski **[Nowy koszyk]** (czyszczenie aktualnej kalkulacji) oraz **[Zapisz koszyk]** (zapis bieżącego stanu).
5. **Pasek podsumowania (Stopka):** Na dole ekranu wyświetla w czasie rzeczywistym łączną wartość netto, naliczony podatek VAT (23%), kwotę brutto oraz sumaryczną liczbę sztuk w zleceniu.

---

## 3. Moduły kalkulacyjne narzędzi — Parametry i funkcje

### 3.1. Pole identyfikatora / taga (max 6 znaków)
> **Wskazówka:** W każdym module obok wyboru typu narzędzia znajduje się kompaktowe pole tekstowe o stałym limicie 6 znaków. Umożliwia ono natychmiastowe spersonalizowanie i rozróżnienie pozycji:
> * **Dla fazowników:** określenie kąta stożka, np. `K90`, `K60`, `K120`.
> * **Dla frezów promieniowych:** określenie promienia naroża, np. `R0.5`, `R1.0`, `R2.5`.
> * **Dla rozróżnienia przeznaczenia materiałowego:** np. `ALU`, `INOX`, `STAL`, `GRAF`.
> * **Dla narzędzi specjalnych:** np. `KORP1`, `MOD02`.  
> Wartość wpisana w tagu automatycznie łączy się z nazwą narzędzia w koszyku i na wydruku raportu (np. *„Fazownik K90”*, *„Frez walcowo-czołowy ALU”*).

### 3.2. Reguła parzystości chwytu
* Program automatycznie zaokrągla średnicę chwytu ($D$) w górę do najbliższej **parzystej liczby całkowitej** względem średnicy roboczej ($d$):
  * $d = 5.0\text{ mm} \rightarrow D = 6\text{ mm}$
  * $d = 6.2\text{ mm} \rightarrow D = 8\text{ mm}$
  * $d = 10.0\text{ mm} \rightarrow D = 10\text{ mm}$
  * $d = 11.5\text{ mm} \rightarrow D = 12\text{ mm}$
* Jeśli narzędzie posiada nietypowy chwyt (np. redukowany), zaznacz pole nadpisania i wpisz pożądaną wartość.

### 3.3. Wiertła wielostopniowe
Po wybraniu w module wierteł opcji *„Wiertło stopniowe”* pojawia się wybór liczby stopni (2, 3 lub 4) oraz dynamiczne pola średnic ($d_1..d_4$). Program automatycznie wyznacza największą średnicę ($d_{max}$), która stanowi bazę do kalkulacji powłoki, chwytu i ostrzenia.

### 3.4. Powłoki PVD i strefy powlekania
Użytkownik wybiera rodzaj powłoki (np. *TiN*, *TiAlN*, *AlTiN*, *DLC*) oraz długość strefy powlekania (*50 mm*, *100 mm*, *150 mm*, *200 mm*). Koszt powłoki wyliczany jest precyzyjnie na podstawie średnicy chwytu i długości strefy.

### 3.5. Usługi dodatkowe i mnożnik opuszczenia szyjki
Każda usługa dodatkowa (Cięcie, Opuszczenie średnicy / podszlifowanie szyjki, Ciężkie zużycie, Korekta czoła) posiada **własne, niezależne pole ilości sztuk**. Pozwala to przypisać daną operację tylko do części partii.

**Zasada działania mnożnika opuszczenia szyjki (1x .. 5x):**
* Mnożnik dotyczy **liczby wcięć / wejść szlifierskich**.
* Klient płaci stawkę bazową za jedno wejście szlifierskie (głębokość opuszczenia do 10 mm).
* Każde kolejne wejście (np. 20 mm, 30 mm) jest dodatkowo płatne jako kolejna wielokrotność stawki bazowej.

---

## 4. Instrukcja edycji pliku cennika (`data/cennik.xlsx`)

### 4.1. Dostęp do pliku
Plik znajduje się w katalogu: `data/cennik.xlsx`.  
Można go otworzyć bezpośrednio z poziomu aplikacji klikając przycisk **[⚙ CENNIK]** w menu bocznym.

### 4.2. Automatyczne wykrywanie zmian (Auto-Reload)
Program Ostrzomat monitoruje plik Excel w czasie rzeczywistym. **Nie trzeba restartować programu po zmianie cen!**
1. Otwórz plik w programie Excel (klikając `⚙ CENNIK`).
2. Wprowadź zmiany i naciśnij **Zapisz** (`Ctrl + S`) w Excelu.
3. Program w tle zweryfikuje poprawność pliku, zaktualizuje pamięć podręczną RAM i natychmiast przeliczy pozycje w otwartym koszyku.

### 4.3. Struktura arkuszy

#### Arkusz 1: `Narzędzia`
Definiuje stawki bazowe za ostrzenie narzędzi. Przedziały ilościowe zostały wydzielone do osobnego arkusza rabatów!

| Kolumna | Typ danych | Przykładowa wartość | Opis |
| :--- | :--- | :--- | :--- |
| `Kategoria` | Tekst | `Frezy`, `Wiertla`, `Inne` | Określa moduł, w którym pojawi się narzędzie. |
| `Typ narzędzia` | Tekst | `Frez walcowo-czołowy`, `Fazownik` | Dokładna nazwa narzędzia widoczna na listach wyboru. |
| `Ostrza min` | Liczba | `1`, `2`, `4` | Dolny zakres liczby ostrzy (włącznie). |
| `Ostrza max` | Liczba | `2`, `4`, `99` | Górny zakres liczby ostrzy (dla narzędzi uniwersalnych np. `99`). |
| `Średnica min` | Liczba | `1.0` | Początek przedziału średnicy roboczej (włącznie). |
| `Średnica max` | Liczba | `6.0` | Koniec przedziału średnicy roboczej (włącznie). |
| `Cena bazowa` | Liczba (PLN) | `35.00` | Stawka bazowa netto za sztukę w danym przedziale średnic. |

#### Arkusz 2: `Rabaty ilościowe`
Centralna tabela progów rabatowych pozwalająca definiować zniżki procentowe dla łącznej partii zamawianych narzędzi.

| Kolumna | Typ danych | Przykładowa wartość | Opis |
| :--- | :--- | :--- | :--- |
| `Ilość min` | Liczba całkowita | `1`, `4`, `11` | Dolny próg ilości sztuk w partii. |
| `Ilość max` | Liczba całkowita | `3`, `10`, `999` | Górny próg ilości sztuk (dla ostatniego wpisz np. `999`). |
| `Rabat %` | Liczba (%) | `0.0`, `5.0`, `10.0` | Procentowy upust od ceny bazowej za sztukę. |

#### Arkusz 3: `Powłoki`
Definiuje stawki za nakładanie powłok ochronnych PVD w zależności od średnicy i długości strefy.

| Kolumna | Typ danych | Przykładowa wartość | Opis |
| :--- | :--- | :--- | :--- |
| `Nazwa powłoki` | Tekst | `TiAlN`, `DLC`, `AlTiN` | Nazwa handlowa powłoki. |
| `Średnica max` | Liczba | `12.0` | Górna granica średnicy chwytu. |
| `Długość` | Liczba | `100` | Maksymalna długość strefy powlekania (50, 100, 150, 200 mm). |
| `Cena` | Liczba (PLN) | `22.50` | Stawka netto za powlekanie jednej sztuki. |

#### Arkusz 4: `Usługi`
Definiuje stawki operacji dodatkowych.

| Kolumna | Typ danych | Przykładowa wartość | Opis |
| :--- | :--- | :--- | :--- |
| `Nazwa usługi` | Tekst | `Cięcie`, `Opuszczenie średnicy` | Identyfikator operacji technologicznej. |
| `Parametr min` | Liczba | `1.0` | Dolna granica średnicy roboczej. |
| `Parametr max` | Liczba | `32.0` | Górna granica średnicy roboczej. |
| `Cena` | Liczba (PLN) | `15.00` | Stawka bazowa za wykonanie operacji. |

### 4.4. Odporność na błędy i zachowanie w przypadku luk (Fallback)
* **Co się stanie w przypadku luki w cenniku?**  
  Program Ostrzomat posiada inteligentny mechanizm fallbacków. Jeśli wprowadzono parametry niepokrywające się idealnie z żadnym przedziałem, system automatycznie dobierze stawkę z najbliższego niższego progu. Aplikacja nigdy nie zawiesza się z powodu braku dokładnego rekordu.
* **Co się stanie w przypadku błędnego formatu danych w Excelu?**  
  Jeśli w komórce z ceną wpisany zostanie tekst, usunięty zostanie nagłówek kolumny lub komórka kluczowa pozostanie pusta, program wyświetli okno dialogowe z dokładnym numerem wiersza i nazwą błędnej kolumny. Baza programu nie zostanie uszkodzona — system kontynuuje pracę na ostatnich poprawnych stawkach.

---

## 5. Generowanie ofert i eksport dokumentów

Kliknięcie przycisku **[Generuj wycenę (PDF)]** lub **[Generuj wycenę (Word)]** w stopce koszyka uruchamia eksport:
1. **Format PDF:** Tworzy gotowy do druku i wysłania dokument ofertowy z pełnym formatowaniem graficznym, tabelarycznym rozbiciem kosztów oraz stopką z miejscem na podpis.
2. **Format Word (.docx):** Tworzy edytowalny dokument, umożliwiający dopisanie dodatkowych klauzul handlowych, terminów realizacji czy indywidualnych ustaleń.

---

## 6. FAQ & Rozwiązywanie problemów (Troubleshooting)

**Q: Czy po edycji pliku Excel muszę restartować aplikację?**  
**A:** Nie. Ostrzomat automatycznie wykrywa moment zapisania pliku `cennik.xlsx` i przeładowuje cennik w pamięci programu w ułamku sekundy.

**Q: Jak dodać do programu zupełnie nowy typ narzędzia?**  
**A:** Wystarczy otworzyć `data/cennik.xlsx`, w arkuszu `Narzędzia` dopisać wiersz z kategorią (np. `Frezy`), nową nazwą w kolumnie `Typ narzędzia` (np. *„Frez baryłkowy”*) oraz stawkami. Po zapisaniu pliku nowy typ od razu pojawi się w programie.

**Q: Jak przenieść program na inny komputer?**  
**A:** Wystarczy skopiować cały folder z plikiem `Ostrzomat.exe` oraz podfolderem `data/`. Program jest w pełni przenośny (portable) i nie wymaga instalacji żadnych dodatkowych bibliotek ani praw administratora.

**Q: Gdzie zapisywane są dane klientów?**  
**A:** W pliku bazy danych SQLite `data/ostrzomat.db`. Można go bezpiecznie archiwizować lub kopiować między stanowiskami.

---
*Dokumentacja opracowana dla systemu Ostrzomat v0.2. Wszelkie prawa zastrzeżone.*
