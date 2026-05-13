import customtkinter as ctk

class OstrzomatPopup(ctk.CTkToplevel):
    def __init__(self, parent, title, message, type="info"):
        super().__init__(parent)
        self.title(title)
        
        # --- KONFIGURACJA GEOMETRII ---
        width, height = 400, 200
        # Środek ekranu względem okna nadrzędnego
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # --- STYL I WARSTWY ---
        self.attributes("-topmost", True)  # Zawsze na froncie
        self.grab_set()                   # Blokuje interakcję z oknem pod spodem
        self.resizable(False, False)
        
        # Kolorystyka zależna od typu
        color = "#28a745" if type == "info" else "#dc3545"
        
        # --- UI ---
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.main_frame = ctk.CTkFrame(self, corner_radius=15, border_width=2, border_color=color)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.msg_label = ctk.CTkLabel(
            self.main_frame, 
            text=message, 
            font=("Arial", 14), 
            wraplength=350,
            justify="center"
        )
        self.msg_label.pack(pady=(30, 20), padx=20)
        
        self.ok_btn = ctk.CTkButton(
            self.main_frame, 
            text="OK", 
            fg_color=color, 
            hover_color="#218838" if type == "info" else "#c82333",
            width=120,
            command=self.destroy
        )
        self.ok_btn.pack(pady=(0, 20))
        
        # Automatyczne zamknięcie po 3 sekundach (opcjonalnie)
        # self.after(3000, self.destroy)