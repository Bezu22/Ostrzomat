import customtkinter as ctk

class CartFooter(ctk.CTkFrame):
    def __init__(self, parent, on_save, on_load, on_clear, on_edit, on_delete):
        super().__init__(parent, height=140)
        
        # Prawa strona: Suma całkowita (ma teraz dużo miejsca dla siebie)
        self.total_label = ctk.CTkLabel(
            self, 
            text="ŁĄCZNIE DO ZAPŁATY: 0.00 zł", 
            font=("Arial", 24, "bold"), 
            text_color="#28a745"
        )
        self.total_label.pack(side="right", padx=50, pady=30)

        # Lewa strona: Główny kontener na przyciski akcji
        self.actions_container = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_container.pack(side="left", padx=20, pady=10, fill="y")

        # --- KOLUMNA 1: Akcje Globalne (Zapis, Odczyt, Czyszczenie całości) ---
        self.col_global = ctk.CTkFrame(self.actions_container, fg_color="transparent")
        self.col_global.pack(side="left", padx=10, fill="y")

        self.btn_save = ctk.CTkButton(
            self.col_global, 
            text="💾 ZAPISZ KOSZYK", 
            command=on_save, 
            fg_color="#1f538d", 
            width=160
        )
        self.btn_save.pack(side="top", pady=2, fill="x")

        self.btn_load = ctk.CTkButton(
            self.col_global, 
            text="📂 WCZYTAJ KOSZYK", 
            command=on_load, 
            fg_color="#444", 
            width=160
        )
        self.btn_load.pack(side="top", pady=2, fill="x")
        
        self.btn_clear = ctk.CTkButton(
            self.col_global, 
            text="🗑 WYCZYŚĆ KOSZYK", 
            command=on_clear, 
            fg_color="#c0392b", 
            width=160
        )
        self.btn_clear.pack(side="top", pady=2, fill="x")

        # --- KOLUMNA 2: Akcje Pozycji (Edycja, Usuwanie pojedynczego wiersza) ---
        self.col_item = ctk.CTkFrame(self.actions_container, fg_color="transparent")
        self.col_item.pack(side="left", padx=10, fill="y")

        self.btn_edit = ctk.CTkButton(
            self.col_item, 
            text="✏ EDYTUJ POZYCJĘ", 
            command=on_edit, 
            fg_color="#e67e22", 
            hover_color="#d35400",
            width=160
        )
        self.btn_edit.pack(side="top", pady=2, fill="x")

        self.btn_delete = ctk.CTkButton(
            self.col_item, 
            text="❌ USUŃ POZYCJĘ", 
            command=on_delete, 
            fg_color="#7f8c8d", 
            hover_color="#95a5a6",
            width=160
        )
        self.btn_delete.pack(side="top", pady=2, fill="x")

    def update_total(self, total_value):
        """Aktualizuje tekst sumy końcowej."""
        self.total_label.configure(text=f"ŁĄCZNIE DO ZAPŁATY: {total_value:.2f} zł")