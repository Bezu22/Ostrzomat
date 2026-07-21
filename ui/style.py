import customtkinter as ctk

class Style:
    """
    Centralny Design System aplikacji Ostrzomat.
    Motyw: Przyjemny Niebiesko-Morski / Ocean (Blue - Teal - Aqua).
    Chłodna, profesjonalna i wyważona kolorystyka.
    """

    # --- 1. CZCIONKI (FONTS) ---
    FONT_FAMILY = "Segoe UI"

    FONT_TITLE = (FONT_FAMILY, 18, "bold")
    FONT_SUBTITLE = (FONT_FAMILY, 14, "bold")
    FONT_HEADER = (FONT_FAMILY, 11, "bold")
    FONT_NORMAL = (FONT_FAMILY, 12)
    FONT_BOLD = (FONT_FAMILY, 12, "bold")
    FONT_SMALL = (FONT_FAMILY, 10)
    FONT_TOTAL = (FONT_FAMILY, 22, "bold")

    # --- 2. PALETA KOLORÓW (COLOR PALETTE: BLUE-TEAL) ---
    
    # Główne kolory marki / akcenty
    COLOR_PRIMARY = "#00695C"         # Głęboka morska zieleń/teak (Zapis, akcje główne)
    COLOR_PRIMARY_HOVER = "#004D40"

    COLOR_SECONDARY = "#0277BD"       # Głęboki błękit (Cennik, akcje drugorzędne)
    COLOR_SECONDARY_HOVER = "#01579B"

    COLOR_ACCENT_YELLOW = "#00838F"   # Turkus / Złocisty błękit (Podświetlenia, uwagi)
    COLOR_ACCENT_YELLOW_HOVER = "#006064"

    COLOR_SUCCESS = "#2E7D32"         # Soczysta zieleń (Dodawanie do koszyka, sukces, podsumowanie)
    COLOR_SUCCESS_HOVER = "#1B5E20"

    COLOR_WARNING = "#0288D1"         # Jasny błękit morski (Edycja)
    COLOR_WARNING_HOVER = "#0277BD"

    COLOR_DANGER = "#C62828"          # Czerwony powiadomień / usuwania
    COLOR_DANGER_HOVER = "#8E0000"

    COLOR_MUTED = "#546E7A"           # Chłodny stalowy / szaroniebieski
    COLOR_MUTED_HOVER = "#37474F"

    # Tła i kontenery (Chłodne, jasne i morskie tonacje)
    COLOR_BG_DARK = "#F0F4F8"         # Bardzo jasne, chłodne niebieskoszare tło główne
    COLOR_CARD_BG = "#E0F2F1"         # Bardzo jasne morskie tło kart/paneli
    COLOR_SIDEBAR_BG = "#E1F5FE"      # Jasnobłękitny odcień panelu bocznego
    COLOR_HEADER_BG = "#B2EBF2"       # Morski błękit nagłówków tabeli

    # Wiersze tabeli
    COLOR_ROW_EVEN = "#F4FBFB"        # BARDZO delikatna morska biel
    COLOR_ROW_ODD = "#E0F2F1"         # Jasno-morski odcień
    COLOR_ROW_SELECTED = "#80DEEA"    # Wyrazisty, turkusowo-morski odcień zaznaczenia

    # Teksty
    COLOR_TEXT_DARK = "#1A237E"       # Ciemnogranatowy tekst do jasnych tłeń
    COLOR_TEXT_LIGHT = "#FFFFFF"      # Jasny tekst do ciemnych przycisków
    COLOR_TEXT_MUTED = "#546E7A"      # Stonowany tekst stalowy
    COLOR_TEXT_INACTIVE = "#90A4AE"   # Nieaktywne kreski/statusy
    COLOR_TEXT_ACCENT = "#00695C"     # Tekst wyróżniony (morski/granatowy)

    # --- 3. GEOMETRIA I PROPORCJE ---
    CORNER_RADIUS = 8
    CORNER_RADIUS_POPUP = 12
    BORDER_WIDTH = 2

    PAD_SMALL = 5
    PAD_MEDIUM = 10
    PAD_LARGE = 20

    @classmethod
    def apply_theme(cls):
        """Ustawia jasny motyw CustomTkinter z bazowym kolorem dark-blue."""
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("dark-blue")