import customtkinter as ctk

class CartFooter(ctk.CTkFrame):
    def __init__(self, parent, on_save, on_load, on_clear):
        super().__init__(parent, height=140)
        
        # Prawa strona: Suma całkowita
        self.total_label = ctk.CTkLabel(
            self, 
            text="ŁĄCZNIE DO ZAPŁATY: 0.00 zł", 
            font=("Arial", 24, "bold"), 
            text_color="#28a745"
        )
        self.total_label.pack(side="right", padx=50, pady=30)

        # Lewa strona: Kontener na przyciski akcji
        self.actions_container = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_container.pack(side="left", padx=20, pady=10)

        self.btn_save = ctk.CTkButton(
            self.actions_container, 
            text="ZAPISZ KOSZYK", 
            command=on_save, 
            fg_color="#1f538d", 
            width=150
        )
        self.btn_save.pack(side="left", padx=10)

        self.btn_load = ctk.CTkButton(
            self.actions_container, 
            text="WCZYTAJ KOSZYK", 
            command=on_load, 
            fg_color="#444", 
            width=150
        )
        self.btn_load.pack(side="left", padx=10)
        
        self.btn_clear = ctk.CTkButton(
            self.actions_container, 
            text="WYCZYŚĆ", 
            command=on_clear, 
            fg_color="#c0392b", 
            width=100
        )
        self.btn_clear.pack(side="left", padx=10)

    def update_total(self, total_value):
        """Aktualizuje tekst sumy końcowej."""
        self.total_label.configure(text=f"ŁĄCZNIE DO ZAPŁATY: {total_value:.2f} zł")