import customtkinter as ctk

class AppStyle:
    """
    Centralny Design System aplikacji Ostrzomat.
    Gromadzi stałe kolorów, czcionek, geometrii oraz metody pomocnicze.
    """

    # --- 1. CZCIONKI (FONTS) ---
    FONT_FAMILY = "Segoe UI"
    BASE_FONT_SIZE = 12

    FONT_TITLE = (FONT_FAMILY, 18, "bold")
    FONT_SUBTITLE = (FONT_FAMILY, 14, "bold")
    FONT_HEADER = (FONT_FAMILY, 11, "bold")
    FONT_NORMAL = (FONT_FAMILY, BASE_FONT_SIZE)
    FONT_BOLD = (FONT_FAMILY, BASE_FONT_SIZE, "bold")
    FONT_ITALIC = (FONT_FAMILY, BASE_FONT_SIZE, "italic")
    FONT_SMALL = (FONT_FAMILY, 10)
    FONT_TOTAL = (FONT_FAMILY, 22, "bold")

    # --- METODY CZCIONEK ---
    @classmethod
    def get_normal_font(cls):
        return cls.FONT_NORMAL

    @classmethod
    def get_bold_font(cls):
        return cls.FONT_BOLD

    @classmethod
    def get_italic_font(cls):
        return cls.FONT_ITALIC

    @classmethod
    def get_title_font(cls):
        return cls.FONT_TITLE

    @classmethod
    def get_header_font(cls):
        return cls.FONT_HEADER

    @classmethod
    def get_small_font(cls):
        return cls.FONT_SMALL

    @classmethod
    def get_total_font(cls):
        return cls.FONT_TOTAL

    # --- 2. PALETA KOLORÓW (COLOR PALETTE) ---
    
    # Tła główne i kontenery
    COLOR_MAIN_BG = "#1A1617"       # Głębokie, ciemne tło aplikacji
    COLOR_BG_DARK = COLOR_MAIN_BG   # Alias
    COLOR_BG_LIGHT = "#2D2628"      # Jasniejsze tło dla kart/kontenerów zamiennych
    COLOR_CARD_BG = "#241E20"       # Tło paneli i kart
    COLOR_SIDEBAR_BG = "#201A1C"    # Tło panelu bocznego
    COLOR_HEADER_BG = "#2E2428"     # Tło nagłówków i pasków tytułowych

    # Przyciski i akcje główne
    COLOR_PRIMARY = "#8B0000"        # Głęboki Crimson / Krwista Czerwień
    COLOR_PRIMARY_HOVER = "#A00000"  # Jasniejszy Crimson po najechaniu
    
    COLOR_SECONDARY = "#D97706"      # Bursztyn / Ciepły Amber
    COLOR_SECONDARY_HOVER = "#F59E0B"# Jasny Bursztyn po najechaniu

    COLOR_ACCENT_YELLOW = COLOR_SECONDARY
    COLOR_ACCENT_YELLOW_HOVER = COLOR_SECONDARY_HOVER

    # Stany, komunikaty, przyciski akcji
    COLOR_SUCCESS = "#15803D"        # Zieleń sukcesu
    COLOR_SUCCESS_HOVER = "#16A34A"
    
    COLOR_WARNING = "#B45309"        # Ostrzeżenie / Uwaga
    COLOR_WARNING_HOVER = "#D97706"

    COLOR_DANGER = "#991B1B"         # Błąd / Usuwanie
    COLOR_DANGER_HOVER = "#DC2626"
    COLOR_ERROR = COLOR_DANGER       # Alias dla OstrzomatPopup
    COLOR_ERROR_HOVER = COLOR_DANGER_HOVER

    COLOR_INFO = "#1D4ED8"          # Informacja / Niebieski akcent
    COLOR_INFO_HOVER = "#2563EB"

    # Usługi i kategorie
    COLOR_COAT = "#0284C7"          # Powłoki PVD
    COLOR_COAT_HOVER = "#0369A1"
    COLOR_EXTRA = "#7C3AED"         # Usługi dodatkowe
    COLOR_EXTRA_HOVER = "#6D28D9"

    # Neutralne / Przygaszone
    COLOR_MUTED = "#3D3237"          # Przygaszony grafitowy śliwkowy
    COLOR_MUTED_HOVER = "#4A3E44"

    # Tabela koszyka i listy
    COLOR_ROW_EVEN = "#221C1E"       # Parzyste wiersze
    COLOR_ROW_ODD = "#292124"        # Nieparzyste wiersze
    COLOR_ROW_HOVER = "#382C31"      # Wiersz po najechaniu
    COLOR_ROW_SELECTED = "#4A1D24"   # Zaznaczony wiersz w tabeli

    # Teksty
    COLOR_TEXT_LIGHT = "#F3F4F6"     # Jasny tekst
    COLOR_TEXT_DARK = "#E5E7EB"      # Standardowy ciemny/jasny tekst
    COLOR_TEXT_MUTED = "#9CA3AF"     # Szary tekst
    COLOR_TEXT_INACTIVE = "#6B7280"  # Nieaktywny
    COLOR_TEXT_ACCENT = "#F59E0B"    # Akcent bursztynowy

    # --- 3. GEOMETRIA I PROPORCJE ---
    CORNER_RADIUS = 8
    CORNER_RADIUS_POPUP = 12
    BORDER_WIDTH = 2

    PAD_SMALL = 5
    PAD_MEDIUM = 10
    PAD_LARGE = 15

    # -- przyciski dolne menu
    COLOR_SAVE = "#2B5B84"           # Elegancki niebieski dla ZAPISZ
    COLOR_SAVE_HOVER = "#1E405D"

    COLOR_LOAD = "#D97706"           # Bursztynowy/Pomarańczowy dla WCZYTAJ
    COLOR_LOAD_HOVER = "#B45309"

    COLOR_CLEAR = "#4B5563"          # Ciemnoszary dla WYCZYŚĆ
    COLOR_CLEAR_HOVER = "#374151"

    # --- 4. STYLE WIDŻETÓW (POMOCNICZE SŁOWNIKI) ---
    @classmethod
    def get_entry_style(cls):
        """Standardowe parametry dla widżetów CTkEntry."""
        return {
            "font": cls.FONT_NORMAL,
            "corner_radius": cls.CORNER_RADIUS,
            "border_width": 1,
            "border_color": cls.COLOR_MUTED,
            "fg_color": cls.COLOR_BG_LIGHT,
            "text_color": cls.COLOR_TEXT_LIGHT
        }

    @classmethod
    def get_combo_style(cls):
        """Standardowe parametry dla widżetów CTkComboBox."""
        return {
            "font": cls.FONT_NORMAL,
            "dropdown_font": cls.FONT_NORMAL,
            "corner_radius": cls.CORNER_RADIUS,
            "border_width": 1,
            "border_color": cls.COLOR_MUTED,
            "fg_color": cls.COLOR_BG_LIGHT,
            "button_color": cls.COLOR_MUTED,
            "button_hover_color": cls.COLOR_MUTED_HOVER,
            "text_color": cls.COLOR_TEXT_LIGHT
        }

    @classmethod
    def apply_theme(cls):
        """Ustawia ciemny motyw CustomTkinter."""
        ctk.set_appearance_mode("Dark")

    @classmethod
    def configure_app_theme(cls):
        """Alias metody konfiguracyjnej."""
        cls.apply_theme()