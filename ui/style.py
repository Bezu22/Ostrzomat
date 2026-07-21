import customtkinter as ctk

class Style:
    """
    Centralny Design System aplikacji Ostrzomat.
    Motyw: Energetyczny / Ciepły (Red - Orange - Yellow).
    Ograniczenie ciemnych i szarych tłeń na rzecz jasnych, ciepłych tonacji.
    """

    # --- 1. CZCIONKI (FONTS) ---
    FONT_FAMILY = "Segoe UI"  # Świetny wygląd na Windows

    FONT_TITLE = (FONT_FAMILY, 18, "bold")
    FONT_SUBTITLE = (FONT_FAMILY, 14, "bold")
    FONT_HEADER = (FONT_FAMILY, 11, "bold")
    FONT_NORMAL = (FONT_FAMILY, 12)
    FONT_BOLD = (FONT_FAMILY, 12, "bold")
    FONT_SMALL = (FONT_FAMILY, 10)
    FONT_TOTAL = (FONT_FAMILY, 22, "bold")

    # --- 2. PALETA KOLORÓW (COLOR PALETTE: RED-ORANGE-YELLOW) ---
    
    # Główne kolory marki / akcenty
    COLOR_PRIMARY = "#D32F2F"         # Głęboka czerwień (Zapis, akcje główne)
    COLOR_PRIMARY_HOVER = "#B71C1C"

    COLOR_SECONDARY = "#E65100"       # Ciepły pomarańcz (Podrzędne akcje, cennik)
    COLOR_SECONDARY_HOVER = "#EF6C00"

    COLOR_ACCENT_YELLOW = "#F57F17"   # Złocisty/Żółty akcent (Podświetlenia, uwagi)
    COLOR_ACCENT_YELLOW_HOVER = "#FBC02D"

    COLOR_SUCCESS = "#2E7D32"         # Soczysta zieleń (Dodawanie do koszyka, sukces, podsumowanie)
    COLOR_SUCCESS_HOVER = "#1B5E20"

    COLOR_WARNING = "#F57C00"         # Jasny pomarańcz (Edycja)
    COLOR_WARNING_HOVER = "#E65100"

    COLOR_DANGER = "#C62828"          # Czerwony powiadomień / usuwania
    COLOR_DANGER_HOVER = "#8E0000"

    COLOR_MUTED = "#8D6E63"           # Ciepły brunatny/szary
    COLOR_MUTED_HOVER = "#6D4C41"

    # Tła i kontenery (Ciepłe, jasne i umiarkowanie stonowane)
    COLOR_BG_DARK = "#FAF8F5"         # Bardzo jasne, ciepłe tło główne aplikacji (zamiast czerni)
    COLOR_CARD_BG = "#FFF8E1"         # Bardzo jasne ciepłe tło kart/paneli
    COLOR_SIDEBAR_BG = "#FFF3E0"      # Jasno-pomarańczowy odcień panelu bocznego
    COLOR_HEADER_BG = "#FFE0B2"       # Ciepłe tło nagłówków tabeli

    # Wiersze tabeli
    COLOR_ROW_EVEN = "#FFFDE7"        # Bardzo delikatny, kremowy żółty
    COLOR_ROW_ODD = "#FFF8E1"         # Jasno-bursztynowy odcień
    COLOR_ROW_SELECTED = "#FFCC80"    # Ciepły, pomarańczowy odcień zaznaczenia

    # Teksty
    COLOR_TEXT_DARK = "#212121"       # Ciemny tekst do jasnych tłeń
    COLOR_TEXT_LIGHT = "#FFFFFF"      # Jasny tekst do ciemnych przycisków
    COLOR_TEXT_MUTED = "#8D6E63"      # Stonowany tekst
    COLOR_TEXT_INACTIVE = "#BCAAA4"   # Nieaktywne kreski/statusy
    COLOR_TEXT_ACCENT = "#D84315"     # Tekst wyróżniony (pomarańczowy/czerwony)

    # --- 3. GEOMETRIA I PROPORCJE ---
    CORNER_RADIUS = 8
    CORNER_RADIUS_POPUP = 12
    BORDER_WIDTH = 2

    PAD_SMALL = 5
    PAD_MEDIUM = 10
    PAD_LARGE = 20

    @classmethod
    def apply_theme(cls):
        """Ustawia jasny motyw CustomTkinter."""
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue") 