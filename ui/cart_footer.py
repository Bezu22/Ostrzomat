import customtkinter as ctk
from ui.style import AppStyle  # Integracja ze stylami

class CartFooter(ctk.CTkFrame):
    def __init__(self, parent, on_save, on_load, on_clear, on_edit, on_delete):
        super().__init__(parent, height=140)
        
        # Prawa strona: Suma całkowita (skaluje font w oparciu o BASE_FONT_SIZE)
        self.total_label = ctk.CTkLabel(
            self, 
            text="ŁĄCZNIE DO ZAPŁATY: 0.00 zł", 
            font=(AppStyle.FONT_FAMILY, int(AppStyle.BASE_FONT_SIZE * 2), "bold"), 
            text_color=AppStyle.COLOR_SUCCESS
        )
        self.total_label.pack(side="right", padx=50, pady=30)

        # Lewa strona: Główny kontener na przyciski akcji
        self.actions_container = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_container.pack(side="left", padx=AppStyle.PAD_LARGE, pady=AppStyle.PAD_MEDIUM, fill="y")

        # --- KOLUMNA 1: Akcje Globalne (Zapis, Odczyt, Czyszczenie całości) ---
        self.col_global = ctk.CTkFrame(self.actions_container, fg_color="transparent")
        self.col_global.pack(side="left", padx=AppStyle.PAD_MEDIUM, fill="y")

        self.btn_save = ctk.CTkButton(
            self.col_global, 
            text="💾 ZAPISZ KOSZYK", 
            command=on_save, 
            font=AppStyle.get_bold_font(),
            fg_color=AppStyle.COLOR_PRIMARY, 
            width=160
        )
        self.btn_save.pack(side="top", pady=2, fill="x")

        self.btn_load = ctk.CTkButton(
            self.col_global, 
            text="📂 WCZYTAJ KOSZYK", 
            command=on_load, 
            font=AppStyle.get_bold_font(),
            fg_color="#444", 
            width=160
        )
        self.btn_load.pack(side="top", pady=2, fill="x")
        
        self.btn_clear = ctk.CTkButton(
            self.col_global, 
            text="🗑 WYCZYŚĆ KOSZYK", 
            command=on_clear, 
            font=AppStyle.get_bold_font(),
            fg_color=AppStyle.COLOR_DANGER, 
            width=160
        )
        self.btn_clear.pack(side="top", pady=2, fill="x")

        # --- KOLUMNA 2: Akcje Pozycji (Edycja, Usuwanie pojedynczego wiersza) ---
        self.col_item = ctk.CTkFrame(self.actions_container, fg_color="transparent")
        self.col_item.pack(side="left", padx=AppStyle.PAD_MEDIUM, fill="y")

        self.btn_edit = ctk.CTkButton(
            self.col_item, 
            text="✏ EDYTUJ POZYCJĘ", 
            command=on_edit, 
            font=AppStyle.get_bold_font(),
            fg_color=AppStyle.COLOR_WARNING, 
            hover_color="#d35400",
            width=160
        )
        self.btn_edit.pack(side="top", pady=2, fill="x")

        self.btn_delete = ctk.CTkButton(
            self.col_item, 
            text="❌ USUŃ POZYCJĘ", 
            command=on_delete, 
            font=AppStyle.get_bold_font(),
            fg_color="#7f8c8d", 
            hover_color="#95a5a6",
            width=160
        )
        self.btn_delete.pack(side="top", pady=2, fill="x")

    def update_total(self, total_value):
        """Aktualizuje tekst sumy końcowej."""
        self.total_label.configure(text=f"ŁĄCZNIE DO ZAPŁATY: {total_value:.2f} zł")