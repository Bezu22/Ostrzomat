import customtkinter as ctk

class AppStyle:
    # --- 1. CZCIONKI (FONTS) ---
    FONT_FAMILY = "Arial"
    
    # Bazowy rozmiar czcionki – jeśli na mniejszym ekranie tekst będzie za duży,
    # zmieniasz tylko tę JEDNĄ liczbę (np. na 11 lub 10) i cała aplikacja się dopasuje.
    BASE_FONT_SIZE = 12
    
    @classmethod
    def get_header_font(cls):
        return (cls.FONT_FAMILY, cls.BASE_FONT_SIZE - 1, "bold")
        
    @classmethod
    def get_normal_font(cls):
        return (cls.FONT_FAMILY, cls.BASE_FONT_SIZE)
        
    @classmethod
    def get_bold_font(cls):
        return (cls.FONT_FAMILY, cls.BASE_FONT_SIZE, "bold")

    # --- 2. MARGINESY I DOPEŁNIENIA (PADDINGS) ---
    # Zamiast wpisywać padx=20, pady=10 w każdym module, używasz zmiennych.
    PAD_SMALL = 5
    PAD_MEDIUM = 10
    PAD_LARGE = 20

    # --- 3. KOLORYSTYKA (THEME COLORS) ---
    # Definiujemy stałe kolory dla całej aplikacji (w formacie [LIGHT_MODE, DARK_MODE])
    COLOR_PRIMARY = "#1f538d"       # Główny niebieski (przyciski, akcenty)
    COLOR_SUCCESS = "#28a745"       # Zielony (sukces, finanse)
    COLOR_WARNING = "#e67e22"       # Pomarańczowy (edycja, ostrzeżenia, uwagi)
    COLOR_DANGER = "#c0392b"        # Czerwony (usuwanie, anulowanie)
    
    COLOR_BG_DARK = "#2b2b2b"       # Ciemne wiersze tabeli
    COLOR_BG_LIGHT = "#333333"      # Jaśniejsze wiersze tabeli / nagłówki
    COLOR_TEXT_MUTED = "#888888"    # Szary tekst dla nieaktywnych elementów

    @classmethod
    def configure_app_theme(cls):
        """Wymusza na sztywno ciemny motyw i spójną kolorystykę CustomTkinter."""
        ctk.set_appearance_mode("Dark")  # <--- BLOKADA AUTOMATU WINDOWSA ("System"/"Light"/"Dark")
        ctk.set_default_color_theme("blue")  # Bazowy profil akcentów domyślnych