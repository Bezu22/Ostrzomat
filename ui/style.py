import customtkinter as ctk

class Style:
    """
    Centralny Design System aplikacji Ostrzomat.
    Motyw: Krwista Czerwień & Grafitowy Bursztyn (Crimson & Amber Charcoal).
    Stonowane grafitowe tła + głęboka, krwista czerwień i bursztynowe akcenty.
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

    # --- 2. PALETA KOLORÓW (COLOR PALETTE) ---
    
    # Przycisk Główny / Akcje / Zapis (Wyrazista, krwista czerwień)
    COLOR_PRIMARY = "#B71C1C"         # Krwista czerwień
    COLOR_PRIMARY_HOVER = "#7F0000"   # Ciemniejsza, głęboka czerwień

    # Przycisk Drugorzędny / Cennik / Opcje (Mahoń i bursztyn)
    COLOR_SECONDARY = "#D84315"       # Ciemny rdzawy bursztyn
    COLOR_SECONDARY_HOVER = "#9F0000"

    # Akcenty / Uwagi / Wyróżnienia (Bursztyn / Miedź)
    COLOR_ACCENT_YELLOW = "#E65100"   # Ciepły miedziany bursztyn
    COLOR_ACCENT_YELLOW_HOVER = "#B23B00"

    # Sukces / Koszyk / Suma
    COLOR_SUCCESS = "#2E7D32"         # Głęboka zieleń
    COLOR_SUCCESS_HOVER = "#1B5E20"

    # Edycja
    COLOR_WARNING = "#C2185B"         # Karmazynowy
    COLOR_WARNING_HOVER = "#880E4F"

    # Usuwanie / Anulowanie
    COLOR_DANGER = "#8E0000"          # Ciemniejszy krwisty
    COLOR_DANGER_HOVER = "#580000"

    # Stonowane / Nieaktywne / Anuluj
    COLOR_MUTED = "#4E342E"           # Ciemny, grafitowo-brązowy stalowy
    COLOR_MUTED_HOVER = "#3E2723"

    # Tła i kontenery (Stonowana, nieoślepiająca szarość z nutą grafitu)
    COLOR_BG_DARK = "#9E9E9E"         # Ciemniejsza, matowa szarość tła głównego
    COLOR_CARD_BG = "#CFD8DC"         # Stonowana szaroblekitno-grafitowa karta/panel
    COLOR_SIDEBAR_BG = "#B0BEC5"      # Matowy szary panel boczny
    COLOR_HEADER_BG = "#BCAAA4"       # Warm-gray nagłówek tabeli

    # Wiersze tabeli
    COLOR_ROW_EVEN = "#ECEFF1"        # Bardzo stonowany jasnoszary
    COLOR_ROW_ODD = "#CFD8DC"         # Lekko przyciemniony grafitowy szary
    COLOR_ROW_SELECTED = "#FF8A65"    # Wyraziste bursztynowo-miedziane zaznaczenie

    # Teksty
    COLOR_TEXT_DARK = "#212121"       # Wyrazisty ciemny grafit na jasnych tłąch
    COLOR_TEXT_LIGHT = "#FFFFFF"      # Czysta biel na krwistoczerwonych przyciskach
    COLOR_TEXT_MUTED = "#424242"      # Ciemnoszary stonowany
    COLOR_TEXT_INACTIVE = "#757575"   # Szary nieaktywny
    COLOR_TEXT_ACCENT = "#B71C1C"     # Wyróżnienia tekstu w krwistej czerwieni

    # --- 3. GEOMETRIA I PROPORCJE ---
    CORNER_RADIUS = 8
    CORNER_RADIUS_POPUP = 12
    BORDER_WIDTH = 2

    PAD_SMALL = 5
    PAD_MEDIUM = 10
    PAD_LARGE = 20

    @classmethod
    def apply_theme(cls):
        """Ustawia profil jasny z bazą dark-blue."""
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("dark-blue")