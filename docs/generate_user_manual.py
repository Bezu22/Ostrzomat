import os
import sys
from pathlib import Path

# Łątka dla użycia md5 w bibliotekach
import hashlib
_original_md5 = hashlib.md5
def _safe_md5(*args, **kwargs):
    kwargs.pop('usedforsecurity', None)
    return _original_md5(*args, **kwargs)
hashlib.md5 = _safe_md5

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """
    Dwubiegowy canvas zbierający łączną liczbę stron i rysujący elegancki nagłówek oraz stopkę.
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

    def draw_page_decorations(self, total_pages):
        page_num = self._pageNumber
        width, height = A4

        # Pomijamy nagłówek i stopkę na stronie tytułowej (strona 1)
        if page_num == 1:
            return

        self.saveState()
        self.setFont("Arial", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Górny nagłówek (running header)
        header_text = "Ostrzomat v0.2 — Podręcznik Użytkownika i Instrukcja Obsługi Cennika"
        self.drawString(40, height - 32, header_text)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, height - 36, width - 40, height - 36)

        # Dolna stopka (running footer)
        footer_left = "System kalkulacji i regeneracji narzędzi skrawających"
        footer_right = f"Strona {page_num} z {total_pages}"
        self.line(40, 42, width - 40, 42)
        self.drawString(40, 30, footer_left)
        self.drawRightString(width - 40, 30, footer_right)

        self.restoreState()


def register_fonts():
    fonts_dir = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')
    pdfmetrics.registerFont(TTFont('Arial', os.path.join(fonts_dir, 'arial.ttf')))
    pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(fonts_dir, 'arialbd.ttf')))
    pdfmetrics.registerFont(TTFont('Arial-Italic', os.path.join(fonts_dir, 'ariali.ttf')))
    pdfmetrics.registerFont(TTFont('Arial-BoldItalic', os.path.join(fonts_dir, 'arialbi.ttf')))
    pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold', italic='Arial-Italic', boldItalic='Arial-BoldItalic')


def create_callout(text, style, kind="info", width=515):
    """Tworzy estetyczną ramkę z objaśnieniem lub ostrzeżeniem."""
    cfg = {
        "info": {
            "bg": colors.HexColor("#EFF6FF"),
            "border": colors.HexColor("#2563EB"),
            "prefix": "<b>INFORMACJA:</b> "
        },
        "tip": {
            "bg": colors.HexColor("#ECFDF5"),
            "border": colors.HexColor("#059669"),
            "prefix": "<b>WSKAZÓWKA:</b> "
        },
        "warning": {
            "bg": colors.HexColor("#FFFBEB"),
            "border": colors.HexColor("#D97706"),
            "prefix": "<b>UWAGA / OSTRZEŻENIE:</b> "
        },
        "danger": {
            "bg": colors.HexColor("#FEF2F2"),
            "border": colors.HexColor("#DC2626"),
            "prefix": "<b>WAŻNE:</b> "
        }
    }.get(kind, {"bg": colors.HexColor("#F8FAFC"), "border": colors.HexColor("#64748B"), "prefix": ""})

    p = Paragraph(f"{cfg['prefix']}{text}", style)
    t = Table([[p]], colWidths=[width])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), cfg["bg"]),
        ('BOX', (0, 0), (-1, -1), 0.5, cfg["border"]),
        ('LINELEFT', (0, 0), (0, -1), 3.5, cfg["border"]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    return t


def build_manual_pdf(output_path: str):
    register_fonts()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=46,
        bottomMargin=50
    )

    # Definicja stylów
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=24,
        leading=30,
        textColor=colors.HexColor("#0F172A"),
        alignment=0,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#475569"),
        alignment=0,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=5
    )

    body_bold = ParagraphStyle(
        'Body_Bold',
        parent=body_style,
        fontName='Arial-Bold'
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=9.2,
        leading=13,
        textColor=colors.HexColor("#334155"),
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0F172A"),
        backColor=colors.HexColor("#F1F5F9"),
        spaceAfter=4,
        leftIndent=10
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1E293B")
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    story = []

    # ==========================================
    # STRONA TYTUŁOWA / WPROWADZENIE
    # ==========================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("Ostrzomat v0.2", title_style))
    story.append(Paragraph("Kompleksowy Podręcznik Użytkownika &amp; Przewodnik Administracji Cennikiem", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2563EB"), spaceAfter=14))

    meta_data = [
        [
            Paragraph("<b>Przeznaczenie:</b> System automatyzacji kalkulacji kosztów ostrzenia, powlekania i regeneracji narzędzi skrawających", table_cell),
            Paragraph("<b>Wersja:</b> 0.2 (Edycja produkcyjna)", table_cell)
        ],
        [
            Paragraph("<b>Format danych:</b> MS Excel (.xlsx), SQLite (.db), PDF, DOCX", table_cell),
            Paragraph(f"<b>Data wydania dokumentu:</b> Wrzesień 2026 r.", table_cell)
        ]
    ]
    t_meta = Table(meta_data, colWidths=[330, 185])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 12))

    story.append(create_callout(
        "Niniejszy dokument stanowi oficjalną instrukcję obsługi oprogramowania <b>Ostrzomat</b>. "
        "Zawiera szczegółowy opis wszystkich modułów obliczeniowych, zasad wprowadzania danych, "
        "sposobów generowania ofert handlowych oraz pełny przewodnik po strukturze i bezpiecznej edycji arkusza Excel z cennikiem.",
        body_style,
        kind="info"
    ))
    story.append(Spacer(1, 10))

    # ==========================================
    # SPIS TREŚCI
    # ==========================================
    story.append(Paragraph("Spis zawartości podręcznika", h2_style))
    toc_data = [
        [Paragraph("<b>Rozdział 1. Wprowadzenie i architektura systemu</b> — cel programu, struktura plików i instalacja", table_cell)],
        [Paragraph("<b>Rozdział 2. Interfejs użytkownika i zarządzanie wyceną</b> — menu boczne, klienci, koszyk, uwagi", table_cell)],
        [Paragraph("<b>Rozdział 3. Moduły kalkulacyjne narzędzi</b> — frezy, wiertła, inne, specjalne, identyfikator tag (6 znaków)", table_cell)],
        [Paragraph("<b>Rozdział 4. Edycja cennika Excel (cennik.xlsx)</b> — struktura arkuszy, przedziały, auto-reload, zabezpieczenia", table_cell)],
        [Paragraph("<b>Rozdział 5. Generowanie ofert i eksport dokumentów</b> — kalkulacje PDF i Word (DOCX)", table_cell)],
        [Paragraph("<b>Rozdział 6. FAQ &amp; Rozwiązywanie problemów</b> — odpowiedzi na najczęstsze pytania techniczne", table_cell)],
    ]
    t_toc = Table(toc_data, colWidths=[515])
    t_toc.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_toc)
    story.append(Spacer(1, 12))

    # ==========================================
    # ROZDZIAŁ 1: WPROWADZENIE
    # ==========================================
    story.append(Paragraph("1. Wprowadzenie i architektura systemu", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#93C5FD"), spaceAfter=8))
    story.append(Paragraph(
        "System <b>Ostrzomat</b> to dedykowana aplikacja inżyniersko-handlowa stworzona w celu błyskawicznej, "
        "precyzyjnej i bezbłędnej kalkulacji kosztów ostrzenia, regeneracji, modyfikacji oraz powlekania monolitycznych "
        "narzędzi skrawających z węglika spiekanego (VHM) i stali szybkotnącej (HSS).",
        body_style
    ))
    story.append(Paragraph(
        "Aplikacja eliminuje konieczność ręcznego wertowania tabel cennikowych, automatyzuje obliczenia matematyczne "
        "(zaokrąglanie średnic chwytów, mnożniki podszlifów, strefy powlekania, rabatowanie ilościowe) i pozwala w kilka sekund "
        "stworzyć profesjonalny dokument ofertowy dla klienta.",
        body_style
    ))

    story.append(Paragraph("Struktura plików programu:", h2_style))
    story.append(Paragraph("Aplikacja w wersji skompilowanej lub instalacyjnej opiera się na przejrzystym katalogu głównym:", body_style))

    file_struct_data = [
        [Paragraph("<b>Plik / Katalog</b>", table_header), Paragraph("<b>Rola w systemie i zalecenia</b>", table_header)],
        [Paragraph("<code>Ostrzomat.exe</code>", table_cell), Paragraph("Główny plik wykonywalny programu. Może być uruchamiany bezpośrednio lub poprzez skrót na Pulpicie.", table_cell)],
        [Paragraph("<code>icon.ico</code>", table_cell), Paragraph("Plik ikony wykorzystywany przez interfejs graficzny i pasek zadań Windows.", table_cell)],
        [Paragraph("<code>data/</code>", table_cell), Paragraph("<b>Kluczowy katalog danych.</b> Zawiera bazę cennika i ustawienia programu. Musi znajdować się obok pliku .exe!", table_cell)],
        [Paragraph("<code>data/cennik.xlsx</code>", table_cell), Paragraph("Główny arkusz kalkulacyjny z cenami ostrzenia, powłok i usług. Edytowalny w programie Excel.", table_cell)],
        [Paragraph("<code>data/ostrzomat.db</code>", table_cell), Paragraph("Wewnętrzna baza SQLite z zindeksowanymi danymi, bazą klientów oraz historią konfiguracji.", table_cell)],
        [Paragraph("<code>data/cart_state.json</code>", table_cell), Paragraph("Automatyczna kopia bieżącej sesji koszyka (zapobiega utracie pracy w razie przypadkowego zamknięcia).", table_cell)]
    ]
    t_struct = Table(file_struct_data, colWidths=[130, 385])
    t_struct.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_struct)
    story.append(Spacer(1, 10))

    # ==========================================
    # ROZDZIAŁ 2: INTERFEJS UŻYTKOWNIKA
    # ==========================================
    story.append(PageBreak())
    story.append(Paragraph("2. Interfejs użytkownika i obsługa wyceny", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#93C5FD"), spaceAfter=8))
    story.append(Paragraph(
        "Układ graficzny programu został zaprojektowany z zachowaniem zasad ergonomii pracy biurowej i warsztatowej. "
        "Ekran podzielony jest na logiczne obszary robocze: <b>Panel boczny (Sidebar)</b> po lewej stronie, "
        "<b>Górny pasek kontrahenta</b>, <b>Obszar tabeli wyceny (Koszyk)</b> oraz <b>Stopkę koszyka z przyciskami akcji</b>.",
        body_style
    ))

    story.append(Paragraph("Panel boczny (Sidebar):", h2_style))
    story.append(Paragraph("• <b>[➕ DODAJ FREZ]:</b> Otwiera kalkulator dedykowany frezom walcowo-czołowym, z czołem kulistym, promieniowym oraz frezom zgrubnym.", bullet_style))
    story.append(Paragraph("• <b>[➕ DODAJ WIERTŁO]:</b> Otwiera kalkulator wierteł krętych monolitycznych oraz wierteł wielostopniowych (od 2 do 4 stopni średnic).", bullet_style))
    story.append(Paragraph("• <b>[➕ DODAJ INNE]:</b> Moduł dedykowany fazownikom, pogłębiaczom stożkowym i frezom z promieniem wewnętrznym (wklęsłym).", bullet_style))
    story.append(Paragraph("• <b>[➕ DODAJ SPECJALNE]:</b> Umożliwia wycenę narzędzi niestandardowych, zmodyfikowanych i prototypów z ręcznym określeniem stawki jednostkowej.", bullet_style))
    story.append(Paragraph("• <b>[⚙ CENNIK]:</b> Bezpośrednio otwiera plik <code>data/cennik.xlsx</code> w domyślnym programie (np. Microsoft Excel) w celu aktualizacji stawek.", bullet_style))
    story.append(Paragraph("• <b>[↻ SPRAWDŹ I PRZEŁADUJ CENNIK]:</b> Ręczne wymuszenie ponownej walidacji i załadowania cennika do pamięci podręcznej programu.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Pasek górny (Wybór kontrahenta):", h2_style))
    story.append(Paragraph(
        "Przycisk <b>[👤 Klient: ...]</b> znajduje się w górnym pasku bezpośrednio nad tabelą koszyka. "
        "Kliknięcie otwiera wyszukiwarkę kontrahentów z bazy danych z możliwością filtrowania oraz natychmiastowego "
        "dodania nowej firmy (Nazwa, NIP, Adres, Telefon, E-mail).",
        body_style
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Obsługa tabeli wyceny i operacje w stopce (Koszyk pozycji):", h2_style))
    story.append(Paragraph(
        "Tabela w centralnej części okna prezentuje listę wszystkich skalkulowanych narzędzi z dokładnym rozbiciem kosztów: "
        "ceną jednostkową i łączną za ostrzenie, powłokę oraz usługi dodatkowe.",
        body_style
    ))
    story.append(Paragraph("<b>Obsługa pozycji w koszyku:</b>", body_style))
    story.append(Paragraph("1. <b>Edycja pozycji:</b> Zaznacz pozycję w tabeli (klikając lewym przyciskiem myszy na wierszu), a następnie kliknij przycisk <b>[Edytuj pozycję]</b> znajdujący się w stopce pod tabelą. Parametry narzędzia zostaną załadowane do formularza modułu.", bullet_style))
    story.append(Paragraph("2. <b>Usuwanie pozycji:</b> Zaznacz pozycję i kliknij przycisk <b>[Usuń zaznaczone]</b> lub czerwoną ikonę usuwania na końcu wiersza.", bullet_style))
    story.append(Paragraph("3. <b>Uwagi techniczne [📝 Uwagi]:</b> Zaznacz pozycję i kliknij przycisk uwag, aby wprowadzić uwagi technologiczne. Wprowadzone uwagi znajdą się bezpośrednio na raporcie końcowym obok nazwy pozycji.", bullet_style))
    story.append(Paragraph("4. <b>Zarządzanie koszykiem:</b> W stopce dostępne są przyciski <b>[Nowy koszyk]</b> (czyszczenie aktualnej kalkulacji) oraz <b>[Zapisz koszyk]</b> (zapis bieżącego stanu).", bullet_style))
    story.append(Paragraph("5. <b>Pasek podsumowania:</b> Na dole ekranu wyświetla w czasie rzeczywistym łączną wartość netto, naliczony podatek VAT (23%), kwotę brutto oraz sumaryczną liczbę sztuk w zleceniu.", bullet_style))

    story.append(Spacer(1, 10))

    # ==========================================
    # ROZDZIAŁ 3: MODUŁY KALKULACYJNE
    # ==========================================
    story.append(Paragraph("3. Moduły kalkulacyjne narzędzi — Parametry i funkcje", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#93C5FD"), spaceAfter=8))
    story.append(Paragraph(
        "Każdy moduł kalkulatora wyposażony jest w spójny zestaw kontrolek podzielonych na parametry geometryczne, "
        "konfigurację powlekania oraz usługi regeneracyjne.",
        body_style
    ))

    story.append(create_callout(
        "<b>Pole identyfikatora / taga (max 6 znaków):</b><br/>"
        "W każdym module obok wyboru typu narzędzia znajduje się kompaktowe pole tekstowe o stałym limicie 6 znaków. "
        "Umożliwia ono natychmiastowe spersonalizowanie i rozróżnienie pozycji:<br/>"
        "• Dla fazowników: określenie kąta ostrza: <code>K90</code>, <code>K60</code>, <code>K120</code>.<br/>"
        "• Dla frezów promieniowych: oznaczenie promienia naroża: <code>R0.5</code>, <code>R1.0</code>, <code>R2.5</code>.<br/>"
        "• Dla rozróżnienia przeznaczenia materiałowego: <code>ALU</code>, <code>INOX</code>, <code>STAL</code>, <code>GRAFIT</code>.<br/>"
        "Wartość wpisana w tagu automatycznie łączy się z nazwą narzędzia w koszyku i na wydruku raportu (np. <i>'Fazownik K90'</i>, <i>'Frez walcowo-czołowy ALU'</i>).",
        body_style,
        kind="tip"
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Zasady doboru parametrów:", h2_style))
    story.append(Paragraph("• <b>Średnica robocza (d) a średnica chwytu (D):</b> Program automatycznie oblicza i zaokrągla średnicę chwytu w górę do najbliższej <b>parzystej wartości</b> (np. frez d=5.0 mm otrzymuje chwyt D=6 mm; frez d=6.2 mm otrzymuje chwyt D=8 mm). Jeżeli narzędzie posiada chwyt nietypowy (np. redukowany), użytkownik może zaznaczyć pole nadpisania i wpisać dowolną średnicę chwytu.", bullet_style))
    story.append(Paragraph("• <b>Wiertła wielostopniowe (d1, d2, d3, d4):</b> Po wybraniu w module wierteł opcji <i>'Wiertło stopniowe'</i> pojawia się wybór liczby stopni (2, 3 lub 4) oraz dynamiczne pola średnic. Program automatycznie wyznacza największą średnicę (d_max), która stanowi bazę do kalkulacji powłoki, chwytu i ostrzenia.", bullet_style))
    story.append(Paragraph("• <b>Strefa powlekania PVD:</b> Po wyborze rodzaju powłoki (np. TiN, TiAlN, AlTiN, DLC) użytkownik określa długość strefy powlekania (50, 100, 150 lub 200 mm). Koszt powłoki wyliczany jest precyzyjnie na podstawie średnicy chwytu i długości strefy.", bullet_style))
    story.append(Paragraph("• <b>Usługi dodatkowe z osobnymi ilościami:</b> Każda usługa (Cięcie, Opuszczenie średnicy / szyjki, Szlifowanie czoła, Ciężkie zużycie) posiada własne pole ilości sztuk. Pozwala to przypisać daną operację tylko do wybranej liczby sztuk z partii.", bullet_style))
    story.append(Paragraph("• <b>Mnożnik opuszczenia szyjki (x1 .. x5):</b> Dotyczy <b>liczby wcięć / wejść szlifierskich</b>. Klient płaci stawkę bazową za jedno wejście szlifierskie (głębokość opuszczenia do 10 mm), natomiast każde kolejne wejście (np. 20 mm, 30 mm) jest dodatkowo płatne zgodnie z wybranym mnożnikiem.", bullet_style))

    story.append(Spacer(1, 10))

    # ==========================================
    # ROZDZIAŁ 4: EDYCJA CENNIKA EXCEL
    # ==========================================
    story.append(PageBreak())
    story.append(Paragraph("4. Edycja pliku cennika (data/cennik.xlsx)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#93C5FD"), spaceAfter=8))
    story.append(Paragraph(
        "Cennik programu Ostrzomat oparty jest na standardowym skoroszycie programu Microsoft Excel. "
        "Dzięki temu przedsiębiorstwo ma pełną swobodę w modyfikowaniu stawek, dodawaniu nowych typów narzędzi "
        "i dopasowywaniu rabatów bez ingerencji w kod źródłowy aplikacji.",
        body_style
    ))

    story.append(create_callout(
        "<b>AUTOMATYCZNY NASŁUCH I PRZEŁADOWANIE (Auto-Reload):</b><br/>"
        "Program monitoruje czas modyfikacji pliku <code>data/cennik.xlsx</code> w czasie rzeczywistym. "
        "Wystarczy otworzyć plik, dokonać zmian i nacisnąć <b>Zapisz (Ctrl+S)</b> w Excelu. "
        "Ostrzomat natychmiast zweryfikuje plik, przeładuje stawki i przeliczy koszyk bez konieczności restartowania aplikacji!",
        body_style,
        kind="info"
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Struktura arkuszy w pliku cennik.xlsx:", h2_style))

    excel_sheets_data = [
        [Paragraph("<b>Arkusz</b>", table_header), Paragraph("<b>Wymagane kolumny</b>", table_header), Paragraph("<b>Opis zawartości i przeznaczenie</b>", table_header)],
        [
            Paragraph("<b>Narzędzia</b>", table_cell),
            Paragraph("<code>Kategoria, Typ narzędzia, Ostrza min, Ostrza max, Średnica min, Średnica max, Cena bazowa</code>", table_cell),
            Paragraph("Główny arkusz stawek bazowych za ostrzenie. Definiuje widełki średnic (np. 1–6 mm), zakresy liczby ostrzy oraz stawkę bazową netto w PLN. Przedziały ilościowe wydzielono do osobnego arkusza rabatów!", table_cell)
        ],
        [
            Paragraph("<b>Rabaty ilościowe</b>", table_cell),
            Paragraph("<code>Ilość min, Ilość max, Rabat %</code>", table_cell),
            Paragraph("Centralna tabela progów rabatowych pozwalająca definiować zniżki procentowe dla partii zamawianych narzędzi.", table_cell)
        ],
        [
            Paragraph("<b>Powłoki</b>", table_cell),
            Paragraph("<code>Nazwa powłoki, Średnica max, Długość, Cena</code>", table_cell),
            Paragraph("Tabela stawek za nakładanie powłok ochronnych (TiN, TiAlN, DLC itp.) w zależności od średnicy narzędzia i długości roboczej powlekania.", table_cell)
        ],
        [
            Paragraph("<b>Usługi</b>", table_cell),
            Paragraph("<code>Nazwa usługi, Parametr min, Parametr max, Cena</code>", table_cell),
            Paragraph("Stawki za operacje regeneracyjne i dodatkowe: Cięcie, Opuszczenie średnicy/szyjki, Ciężkie zużycie, Korekta czoła.", table_cell)
        ]
    ]
    t_excel = Table(excel_sheets_data, colWidths=[95, 175, 245])
    t_excel.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_excel)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Zasady definiowania przedziałów i odporność na luki:", h2_style))
    story.append(Paragraph(
        "1. <b>Kolumny Kategoria i Typ narzędzia:</b> Wartość w kolumnie <i>Kategoria</i> musi odpowiadać jednemu z modułów programu: "
        "<code>Frezy</code>, <code>Wiertla</code> lub <code>Inne</code>. W kolumnie <i>Typ narzędzia</i> wpisujemy dokładną nazwę narzędzia.",
        bullet_style
    ))
    story.append(Paragraph(
        "2. <b>Kolumny Ostrza min / Ostrza max:</b> Definiują zakres zębów narzędzia. Jeśli narzędzie ma stałą cenę niezależnie od liczby zębów "
        "(np. wiertła lub fazowniki), wpisujemy Ostrza min=1, Ostrza max=99.",
        bullet_style
    ))
    story.append(Paragraph(
        "3. <b>Przedziały średnic i rabatowanie:</b> Przedziały średnic powinny być ciągłe (np. Średnica min=1, Średnica max=6; kolejny wiersz Średnica min=6.01, Średnica max=10). "
        "Wszelkie zniżki ilościowe konfiguruje się w arkuszu <i>Rabaty ilościowe</i>.",
        bullet_style
    ))
    story.append(Paragraph(
        "4. <b>Co się stanie w przypadku 'dziury' w cenniku?</b> System Ostrzomat wyposażony jest w <i>inteligentny mechanizm fallbacku</i>. "
        "Gdy wprowadzona zostanie średnica lub liczba ostrzy niewystępująca w tabeli, program <b>nie ulegnie awarii</b>, "
        "lecz automatycznie dobierze stawkę z najbliższego pasującego przedziału.",
        bullet_style
    ))

    story.append(Spacer(1, 6))
    story.append(create_callout(
        "<b>ZABEZPIECZENIA I WALIDACJA BŁĘDÓW W EXCELU:</b><br/>"
        "Jeżeli podczas edycji cennika popełniony zostanie błąd formalny (np. wpisanie tekstu 'pięć' zamiast liczby 5 w kolumnie ceny, "
        "usunięcie nagłówka kolumny lub pozostawienie pustego typu), program natychmiast wyświetli czytelne okno ostrzegawcze z numerem wiersza "
        "i nazwą błędnej kolumny. <b>Baza programu nie zostanie uszkodzona</b> — aplikacja kontynuuje pracę na dotychczasowych, stabilnych stawkach, "
        "dając czas na poprawienie pliku Excel.",
        body_style,
        kind="warning"
    ))

    story.append(Spacer(1, 10))

    # ==========================================
    # ROZDZIAŁ 5: GENEROWANIE DOKUMENTÓW
    # ==========================================
    story.append(PageBreak())
    story.append(Paragraph("5. Generowanie ofert i eksport dokumentów", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#93C5FD"), spaceAfter=8))
    story.append(Paragraph(
        "Po skompletowaniu listy narzędzi w koszyku, program umożliwia wygenerowanie formalnej oferty handlowej "
        "w jednym z dwóch formatów: <b>Adobe PDF</b> lub <b>Microsoft Word (.docx)</b>.",
        body_style
    ))

    story.append(Paragraph("Elementy generowanego dokumentu:", h2_style))
    story.append(Paragraph("• <b>Nagłówek oferty:</b> Numer kalkulacji, bieżąca data wystawienia oraz pełne dane teleadresowe kontrahenta pobrane z bazy klientów.", bullet_style))
    story.append(Paragraph("• <b>Szczegółowa tabela pozycji:</b> Każde narzędzie wymienione jest z zachowaniem pełnej specyfikacji (Typ + Tag, średnica robocza, chwyt, liczba zębów, nakładana powłoka ochronna, wyszczególnione usługi dodatkowe oraz uwagi technologiczne).", bullet_style))
    story.append(Paragraph("• <b>Rozbicie finansowe:</b> Przejrzysty podział kwot na operację ostrzenia, powlekania PVD oraz dodatkowych zabiegów regeneracyjnych.", bullet_style))
    story.append(Paragraph("• <b>Zestawienie końcowe:</b> Łączna wartość netto zlecenia, kwota podatku VAT (23%), wartość brutto oraz pole na podpis technologa przygotowującego wycenę.", bullet_style))

    story.append(Spacer(1, 12))

    # ==========================================
    # ROZDZIAŁ 6: FAQ & ROZWIĄZYWANIE PROBLEMÓW
    # ==========================================
    story.append(Paragraph("6. FAQ &amp; Rozwiązywanie problemów (Troubleshooting)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#93C5FD"), spaceAfter=8))

    faq_items = [
        ("Program nie uruchamia się lub zgłasza brak pliku cennika.",
         "Upewnij się, że katalog <code>data/</code> znajduje się w tym samym folderze co plik <code>Ostrzomat.exe</code>. Plik <code>data/cennik.xlsx</code> jest niezbędny do załadowania bazy stawek."),
        ("Po edycji cennika w Excelu pojawił się komunikat o błędzie.",
         "Otwórz plik <code>cennik.xlsx</code> ponownie i sprawdź wiersz wskazany w komunikacie błędu. Upewnij się, że w kolumnach liczbowych (ceny, średnice, ilości) nie ma liter ani znaków specjalnych, a separatorem dziesiętnym jest kropka lub przecinek."),
        ("Jak dodać do programu zupełnie nowy typ narzędzia?",
         "Otwórz <code>cennik.xlsx</code>, w arkuszu <i>Narzedzia</i> dopisz nowy wiersz z kategorią (np. <code>Frezy</code> lub <code>Inne</code>), nową nazwą w kolumnie <i>Typ</i> (np. <i>'Frez baryłkowy'</i>) i zdefiniuj stawki. Po zapisaniu pliku nowy typ natychmiast pojawi się na liście wyboru w programie!"),
        ("Czy mogę przenieść program na pendrive na inny komputer?",
         "Tak! Wystarczy skopiować cały folder zawierający <code>Ostrzomat.exe</code> oraz podfolder <code>data/</code>. Aplikacja nie wymaga instalacji żadnych zewnętrznych bibliotek ani uprawnień administratora.")
    ]

    for q, a in faq_items:
        story.append(Paragraph(f"<b>Pytanie: {q}</b>", h2_style))
        story.append(Paragraph(f"<b>Odpowiedź:</b> {a}", body_style))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=8))
    story.append(Paragraph(
        "<i>Dokument wygenerowany automatycznie przez system Ostrzomat. Wszelkie prawa zastrzeżone.</i>",
        ParagraphStyle('FooterNotice', parent=styles['Normal'], fontName='Arial-Italic', fontSize=8, textColor=colors.HexColor("#64748B"), alignment=1)
    ))

    # Budowa dokumentu PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print("Sukces: Wygenerowano instrukcje PDF: " + output_path)


if __name__ == "__main__":
    out_dir = Path("docs")
    out_dir.mkdir(exist_ok=True)
    pdf_target = str(out_dir / "Instrukcja_Uzytkownika_Ostrzomat.pdf")
    build_manual_pdf(pdf_target)
