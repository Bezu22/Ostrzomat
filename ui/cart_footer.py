import customtkinter as ctk
from ui.style import Style

class CartFooter(ctk.CTkFrame):
    def __init__(self, parent, on_save, on_load, on_clear, on_edit, on_delete):
        super().__init__(parent, height=140, fg_color=Style.COLOR_CARD_BG, corner_radius=Style.CORNER_RADIUS)
        
        self.total_label = ctk.CTkLabel(
            self, 
            text="ŁĄCZNIE DO ZAPŁATY: 0.00 zł", 
            font=Style.FONT_TOTAL, 
            text_color=Style.COLOR_SUCCESS
        )
        self.total_label.pack(side="right", padx=50, pady=30)

        self.actions_container = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_container.pack(side="left", padx=Style.PAD_LARGE, pady=Style.PAD_MEDIUM, fill="y")

        # --- KOLUMNA 1: Akcje Globalne ---
        self.col_global = ctk.CTkFrame(self.actions_container, fg_color="transparent")
        self.col_global.pack(side="left", padx=Style.PAD_MEDIUM, fill="y")

        self.btn_save = ctk.CTkButton(
            self.col_global, 
            text="💾 ZAPISZ KOSZYK", 
            command=on_save, 
            font=Style.FONT_BOLD,
            fg_color=Style.COLOR_PRIMARY, 
            hover_color=Style.COLOR_PRIMARY_HOVER,
            text_color=Style.COLOR_TEXT_LIGHT,
            width=160
        )
        self.btn_save.pack(side="top", pady=2, fill="x")

        self.btn_load = ctk.CTkButton(
            self.col_global, 
            text="📂 WCZYTAJ KOSZYK", 
            command=on_load, 
            font=Style.FONT_BOLD,
            fg_color=Style.COLOR_SECONDARY, 
            hover_color=Style.COLOR_SECONDARY_HOVER,
            text_color=Style.COLOR_TEXT_LIGHT,
            width=160
        )
        self.btn_load.pack(side="top", pady=2, fill="x")
        
        self.btn_clear = ctk.CTkButton(
            self.col_global, 
            text="🗑 WYCZYŚĆ KOSZYK", 
            command=on_clear, 
            font=Style.FONT_BOLD,
            fg_color=Style.COLOR_DANGER, 
            hover_color=Style.COLOR_DANGER_HOVER,
            text_color=Style.COLOR_TEXT_LIGHT,
            width=160
        )
        self.btn_clear.pack(side="top", pady=2, fill="x")

        # --- KOLUMNA 2: Akcje Pozycji ---
        self.col_item = ctk.CTkFrame(self.actions_container, fg_color="transparent")
        self.col_item.pack(side="left", padx=Style.PAD_MEDIUM, fill="y")

        self.btn_edit = ctk.CTkButton(
            self.col_item, 
            text="✏ EDYTUJ POZYCJĘ", 
            command=on_edit, 
            font=Style.FONT_BOLD,
            fg_color=Style.COLOR_WARNING, 
            hover_color=Style.COLOR_WARNING_HOVER,
            text_color=Style.COLOR_TEXT_LIGHT,
            width=160
        )
        self.btn_edit.pack(side="top", pady=2, fill="x")

        self.btn_delete = ctk.CTkButton(
            self.col_item, 
            text="❌ USUŃ POZYCJĘ", 
            command=on_delete, 
            font=Style.FONT_BOLD,
            fg_color=Style.COLOR_MUTED, 
            hover_color=Style.COLOR_MUTED_HOVER,
            text_color=Style.COLOR_TEXT_LIGHT,
            width=160
        )
        self.btn_delete.pack(side="top", pady=2, fill="x")

    def update_total(self, total_value):
        self.total_label.configure(text=f"ŁĄCZNIE DO ZAPŁATY: {total_value:.2f} zł")