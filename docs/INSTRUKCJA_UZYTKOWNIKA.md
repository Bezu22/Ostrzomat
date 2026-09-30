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
| `icon.ico` | Ikona aplikacji wyświetlana w systemie i na pasku zadań. |
| `data/` | **Kluczowy katalog danych.** Musi znajdować się w tym samym folderze co plik wykonywalny! |
| `data/cennik.xlsx` | Arkusz kalkulacyjny ze stawkami ostrzenia, powłok i usług. Użytkownik ma pełną swobodę jego edycji. |
| `data/ostrzomat.db` | Baza SQLite przechowująca zindeksowany cennik, bazę klientów i historię. |
| `data/cart_state.json` | Automatycznie zapisywany stan bieżącego koszyka (zapobiega utracie danych przy przypadkowym zamknięciu). |

---

## 2. Interfejs użytkownika i obsługa wyceny

Ekran programu podzielony jest na dwa współpracujące obszary:
1. **Pasek boczny (Sidebar)** — menu wyboru modułów narzędziowych oraz operacji globalnych.
2. **Tabela wyceny (Koszyk)** — centralny obszar roboczy prezentujący aktualnie skalkulowane pozycje i podsumowanie finansowe.

### 2.1. Przyciski paska bocznego (Sidebar)
* **[👤 Klient: ...]**: Otwiera okno wyboru kontrahenta z bazy danych. Wyszukiwarka pozwala na filtrowanie po nazwie, NIP lub mieście, a także dodanie nowej firmy do bazy.
* **[Frezy]**: Otwiera moduł wyceny frezów walcowo-czołowych, z czołem kulistym, promieniowych i zgrubnych.
* **[Wiertła]**: Otwiera moduł wyceny wierteł krętych monolitycznych oraz wierteł wielostopniowych (2, 3 lub 4 stopnie).
* **[Inne]**: Moduł narzędzi uzupełniających: fazowniki, pogłębiacze, frezy z promieniem wewnętrznym (wklęsłym).
* **[Specjale]**: Moduł kalkulacji narzędzi niestandardowych, modyfikacji i prototypów z ręcznie wprowadzaną stawką jednostkową.
* **[📊 Edytuj cennik]**: Bezpośrednio otwiera plik `data/cennik.xlsx` w programie Microsoft Excel.
* **[🗑️ Nowy koszyk]**: Czyści listę narzędzi i zeruje kalkulację po uprzednim potwierdzeniu.
* **[📄 Generuj ofertę]**: Uruchamia kreator generowania gotowej oferty handlowej (PDF / DOCX).

### 2.2. Zarządzanie pozycjami w koszyku
* **Edycja pozycji:** Kliknij dwukrotnie (**Double-Click**) lewym przyciskiem myszy na wierszu w tabeli. Dane pozycji zostaną automatycznie załadowane do formularza modułu, umożliwiając zmianę ilości, parametrów lub usług.
* **Usuwanie pozycji:** Kliknij czerwoną ikonę usuwania na końcu wybranego wiersza.
* **Dodawanie uwag technicznych [📝 Uwagi]:** Zaznacz pozycję i kliknij przycisk uwag, aby dopisać wytyczne technologiczne (np. *"Skrócić część roboczą o 3mm"*, *"Promień R0.5"*, *"Powlekać tylko do połowy rowka"*). Uwagi te trafią bezpośrednio do generowanego dokumentu.
* **Pasek podsumowania (Stopka):** W czasie rzeczywistym aktualizuje wartość netto zlecenia, stawkę VAT (23%), kwotę brutto oraz sumaryczną liczbę narzędzi.

---

## 3. Moduły kalkulacyjne narzędzi — Parametry i funkcje

### 3.1. Uniwersalne pole identyfikatora / taga (max 6 znaków)
W każdym module obok listy wyboru typu narzędzia znajduje się uniwersalne pole tekstowe z limitem **6 znaków**. Pozwala ono na szybką i trwałą identyfikację detalu:
* **Dla fazowników:** określenie kąta stożka, np. `K90`, `K60`, `K120`.
* **Dla frezów promieniowych:** określenie promienia naroża, np. `R0.5`, `R1.0`, `R2.5`.
* **Dla przeznaczenia materiałowego:** np. `ALU`, `INOX`, `STAL`, `GRAF`.
* **Dla narzędzi specjalnych:** np. `KORP1`, `MOD02`.

Wartość taga jest automatycznie łączona z typem narzędzia w tabeli koszyka oraz na wydruku oferty (np. *„Fazownik K90”*, *„Frez walcowo-czołowy ALU”*).

### 3.2. Reguła parzystości chwytu
* Program automatycznie zaokrągla średnicę chwytu ($D$) w górę do najbliższej **parzystej liczby całkowitej** względem średnicy roboczej ($d$):
  * $d = 5.0\text{ mm} \rightarrow D = 6\text{ mm}$
  * $d = 6.2\text{ mm} \rightarrow D = 8\text{ mm}$
  * $d = 10.0\text{ mm} \rightarrow D = 10\text{ mm}$
  * $d = 11.5\text{ mm} \rightarrow D = 12\text{ mm}$
* Jeśli narzędzie posiada nietypowy chwyt (np. redukowany), zaznacz pole nadpisania i wpisz pożądaną wartość.

### 3.3. Wiertła wielostopniowe
Po zaznaczeniu opcji *„Wiertło stopniowe”* w module wierteł użytkownik wskazuje liczbę stopni (od 2 do 4) oraz wpisuje poszczególne średnice ($d_1, d_2, d_3, d_4$). Program automatycznie odnajduje największą średnicę ($d_{max}$), która staje się bazą kalkulacji chwytu, ostrzenia i strefy powlekania.

### 3.4. Powłoki PVD i strefy powlekania
Użytkownik wybiera rodzaj powłoki (np. *TiN*, *TiAlN*, *AlTiN*, *DLC*) oraz długość strefy powlekania (*50 mm*, *100 mm*, *150 mm*, *200 mm*). Koszt nakładania powłoki kalkulowany jest precyzyjnie na podstawie średnicy i wybranej długości.

### 3.5. Niezależne ilości dla usług dodatkowych
Każda operacja dodatkowa posiada własne, niezależne pole ilości sztuk:
* **Cięcie / odcinanie zniszczonego czoła**
* **Opuszczenie średnicy / podszlifowanie szyjki** (wraz z mnożnikiem skomplikowania od $1\times$ do $5\times$)
* **Ciężkie zużycie / regeneracja wykruszeń**
* **Korekta geometrii czoła / promienia**

Dzięki temu w partii 10 sztuk narzędzi można przypisać np. cięcie tylko dla 2 najbardziej zużytych sztuk, a opuszczenie szyjki dla 5 sztuk.

---

## 4. Instrukcja edycji pliku cennika (`data/cennik.xlsx`)

### 4.1. Dostęp do pliku
Plik znajduje się w katalogu: `data/cennik.xlsx`.  
Można go otworzyć bezpośrednio z poziomu aplikacji klikając przycisk **[📊 Edytuj cennik]** w menu bocznym.

### 4.2. Automatyczne wykrywanie zmian (Auto-Reload)
Program Ostrzomat monitoruje plik Excel w czasie rzeczywistym. **Nie trzeba restartować programu po zmianie cen!**
1. Otwórz plik w programie Excel.
2. Zmień wartości, dodaj nowe pozycje lub zmień progi ilościowe.
3. Kliknij **Zapisz** (`Ctrl + S`) w Excelu.
4. Program w tle zweryfikuje poprawność pliku, zaktualizuje pamięć podręczną RAM i natychmiast przeliczy pozycje w otwartym koszyku!

### 4.3. Struktura arkuszy

#### Arkusz 1: `Narzedzia`
Definiuje stawki bazowe za ostrzenie narzędzi.

| Kolumna | Typ danych | Przykładowa wartość | Opis |
| :--- | :--- | :--- | :--- |
| `Kategoria` | Tekst | `Frezy`, `Wiertla`, `Inne` | Określa moduł, w którym pojawi się narzędzie. |
| `Typ` | Tekst | `Frez walcowo-czołowy`, `Fazownik` | Nazwa narzędzia widoczna na listach wyboru. |
| `Srednica_od` | Liczba | `1.0` | Początek przedziału średnicy roboczej (włącznie). |
| `Srednica_do` | Liczba | `6.0` | Koniec przedziału średnicy roboczej (włącznie). |
| `Ilosc_od` | Liczba całkowita | `1` | Minimalna liczba sztuk w przedziale ilościowym. |
| `Ilosc_do` | Liczba całkowita | `3` | Maksymalna liczba sztuk (dla ostatniego wpisz np. `9999`). |
| `Zeby` | Liczba / Tekst | `2`, `4`, `ALL` lub puste | Liczba ostrzy. Wpisz `ALL` lub zostaw puste, jeśli cena nie zależy od zębów. |
| `Cena` | Liczba (PLN) | `35.00` | Stawka netto za sztukę w danym przedziale. |

#### Arkusz 2: `Powloki`
Definiuje stawki za nakładanie powłok ochronnych PVD.

| Kolumna | Typ danych | Przykładowa wartość | Opis |
| :--- | :--- | :--- | :--- |
| `Nazwa_powloki` | Tekst | `TiAlN`, `DLC`, `AlTiN` | Nazwa handlowa powłoki widoczna na liście. |
| `Srednica_od` | Liczba | `1.0` | Początek przedziału średnicy chwytu. |
| `Srednica_do` | Liczba | `12.0` | Koniec przedziału średnicy chwytu. |
| `Dlugosc_od` | Liczba | `0` | Minimalna długość powlekania. |
| `Dlugosc_do` | Liczba | `100` | Maksymalna długość powlekania (np. 100 mm). |
| `Cena` | Liczba (PLN) | `22.50` | Stawka netto za powlekanie jednej sztuki. |

#### Arkusz 3: `Uslugi`
Definiuje stawki operacji dodatkowych.

| Kolumna | Typ danych | Przykładowa wartość | Opis |
| :--- | :--- | :--- | :--- |
| `Nazwa_uslugi` | Tekst | `Cięcie`, `Opuszczenie szyjki` | Identyfikator operacji technologicznej. |
| `Srednica_od` | Liczba | `1.0` | Dolna granica średnicy. |
| `Srednica_do` | Liczba | `32.0` | Górna granica średnicy. |
| `Cena_baza` | Liczba (PLN) | `15.00` | Stawka bazowa za wykonanie operacji. |

#### Arkusz 4: `Rabaty_Ilosciowe`
Tabela upustów procentowych naliczanych dla dużych zamówień.

| Kolumna | Opis |
| :--- | :--- |
| `Ilosc_od` / `Ilosc_do` | Przedział sumarycznej liczby narzędzi w zleceniu. |
| `Rabat_Procent` | Wartość zniżki (np. `5` dla 5%, `10` dla 10%). |

### 4.4. Odporność na błędy i zachowanie w przypadku luk (Fallback)
* **Co się stanie w przypadku dziury w przedziałach ilościowych lub średnic?**  
  Program Ostrzomat posiada inteligentny mechanizm fallbacków. Jeśli wprowadzono np. 8 sztuk narzędzia, a cennik zawiera jedynie przedziały 1–5 oraz 10–20, system automatycznie przypisze cenę z najbliższego niższego progu. Aplikacja nigdy nie zawiesza się z powodu braku dokładnego rekordu.
* **Co się stanie w przypadku błędnego formatu danych w Excelu?**  
  Jeśli w komórce z ceną wpisany zostanie tekst (np. *„brak”*), usunięty zostanie nagłówek kolumny lub komórka kluczowa pozostanie pusta, program wyświetli okno dialogowe z dokładnym numerem wiersza i nazwą błędnej kolumny. Baza programu nie zostanie nadpisana uszkodzonymi danymi — system kontynuuje pracę na ostatnich poprawnych stawkach.

---

## 5. Generowanie ofert i eksport dokumentów

Kliknięcie przycisku **[📄 Generuj ofertę]** w menu bocznym otwiera kreator eksportu:
1. **Format PDF:** Tworzy elegancki, gotowy do druku i wysłania dokument ofertowy z pełnym formatowaniem graficznym, tabelarycznym rozbiciem kosztów oraz stopką z miejscem na podpis.
2. **Format Word (.docx):** Tworzy edytowalny dokument, umożliwiający dopisanie dodatkowych klauzul handlowych, terminów realizacji czy indywidualnych warunków gwarancyjnych.

---

## 6. FAQ & Rozwiązywanie problemów (Troubleshooting)

**Q: Czy po edycji pliku Excel muszę restartować aplikację?**  
**A:** Nie. Ostrzomat automatycznie wykrywa moment zapisania pliku `cennik.xlsx` i przeładowuje cennik w pamięci programu w ułamku sekundy.

**Q: Jak dodać do programu zupełnie nowy typ narzędzia?**  
**A:** Wystarczy otworzyć `data/cennik.xlsx`, w arkuszu `Narzedzia` dopisać wiersz z kategorią (np. `Frezy`), nową nazwą w kolumnie `Typ` (np. *„Frez baryłkowy”*) oraz stawkami. Po zapisaniu pliku nowy typ od razu pojawi się w programie.

**Q: Jak przenieść program na inny komputer?**  
**A:** Wystarczy skopiować cały folder z plikiem `Ostrzomat.exe` oraz podfolderem `data/`. Program jest w pełni przenośny (portable) i nie wymaga praw administratora.

**Q: Gdzie zapisywane są dane klientów?**  
**A:** W pliku bazy danych SQLite `data/ostrzomat.db`. Można go bezpiecznie archiwizować lub przenosić między stanowiskami.

---
*Dokumentacja opracowana dla systemu Ostrzomat v0.2. Wszelkie prawa zastrzeżone.*
