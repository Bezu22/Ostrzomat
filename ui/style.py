import customtkinter as ctk

class Style:
    """
    Centralny Design System aplikacji Ostrzomat.
    Wszystkie kolory, czcionki i wymiary są zarządzane w tym miejscu.
    """
    
    # --- 1. CZCIONKI (FONTS) ---
    FONT_FAMILY = "Arial"
    
    FONT_TITLE = (FONT_FAMILY, 16, "bold")
    FONT_SUBTITLE = (FONT_FAMILY, 14, "bold")
    FONT_HEADER = (FONT_FAMILY, 11, "bold")
    FONT_NORMAL = (FONT_FAMILY, 12)
    FONT_BOLD = (FONT_FAMILY, 12, "bold")
    FONT_SMALL = (FONT_FAMILY, 10)
    FONT_TOTAL = (FONT_FAMILY, 24, "bold")

    # --- 2. PALETA KOLORÓW (COLOR PALETTE) ---
    # Akcenty i akcje
    COLOR_PRIMARY = "#1f538d"       # Niebieski (Zapis, akcje główne)
    COLOR_PRIMARY_HOVER = "#163e69"
    
    COLOR_SUCCESS = "#28a745"       # Zielony (Suma, Dodawanie, Potwierdzenie)
    COLOR_SUCCESS_HOVER = "#218838"
    
    COLOR_WARNING = "#e67e22"       # Pomarańczowy (Edycja, Uwagi)
    COLOR_WARNING_HOVER = "#d35400"
    
    COLOR_DANGER = "#c0392b"        # Czerwony (Usuwanie, Anulowanie, Czyszczenie)
    COLOR_DANGER_HOVER = "#a93226"
    
    COLOR_SECONDARY = "#444444"     # Szary (Przyciski drugorzędne, cennik, zamknij)
    COLOR_SECONDARY_HOVER = "#333333"
    
    COLOR_MUTED = "#7f8c8d"         # Jasnoszary (Przycisk nieaktywny/usuwanie w tabeli)
    COLOR_MUTED_HOVER = "#95a5a6"

    # Tła i kontenery
    COLOR_BG_DARK = "#1a1a1a"       # Ciemne tło okien i pop-upów
    COLOR_ROW_EVEN = "#2b2b2b"      # Parzyste wiersze tabeli
    COLOR_ROW_ODD = "#333333"       # Nieparzyste wiersze tabeli
    COLOR_ROW_SELECTED = "#1f538d"  # Zaznaczony wiersz w tabeli
    
    COLOR_TEXT_LIGHT = "#ffffff"
    COLOR_TEXT_MUTED = "#888888"
    COLOR_TEXT_INACTIVE = "#555555"

    # --- 3. GEOMETRIA I WYMIARY ---
    CORNER_RADIUS = 8
    CORNER_RADIUS_POPUP = 12
    BORDER_WIDTH = 2
    
    PAD_SMALL = 5
    PAD_MEDIUM = 10
    PAD_LARGE = 20

    @classmethod
    def apply_theme(cls):
        """Wymusza na sztywno ciemny motyw i domyślny profil CustomTkinter."""
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")