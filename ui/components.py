import customtkinter as ctk

class OstrzomatPopup(ctk.CTkToplevel):
    # DODAJEMY parametr on_confirm na samym końcu konstruktora
    def __init__(self, parent, title, message, type="info", on_confirm=None):
        super().__init__(parent)
        self.parent = parent
        self.type = type
        self.on_confirm = on_confirm # Zapisujemy funkcję do wykonania po zatwierdzeniu
        
        self.title(title)
        
        # Określanie koloru ramki w zależności od typu
        if type == "error":
            border_color = "#c0392b"  # Czerwony
        elif type == "success":
            border_color = "#28a745"  # Zielony
        elif type == "confirm":
            border_color = "#e67e22"  # Pomarańczowy dla ostrzeżeń/potwierdzeń
        else:
            border_color = "#1f538d"  # Niebieski (standard)
            
        self.configure(fg_color="#1a1a1a", highlightbackground=border_color, highlightthickness=2)
        
        # Centrowanie okna popupu
        width, height = 400, 180
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        self.attributes("-topmost", True)
        self.grab_set()
        self.resizable(False, False)
        
        # Układ wiadomości
        self.msg_label = ctk.CTkLabel(self, text=message, font=("Arial", 13), wraplength=360, justify="center")
        self.msg_label.pack(expand=True, padx=20, pady=(20, 10))
        
        # --- SEKCJA PRZYCISKÓW (DYNAMICZNA) ---
        if self.type == "confirm":
            # Tworzymy kontener na dwa przyciski obok siebie
            btn_frame = ctk.CTkFrame(self, fg_color="transparent")
            btn_frame.pack(side="bottom", fill="x", padx=20, pady=15)
            
            # Przycisk TAK (Uruchamia on_confirm i zamyka popup)
            self.btn_yes = ctk.CTkButton(btn_frame, text="TAK", fg_color="#28a745", hover_color="#218838", width=160, command=self._action_confirm)
            self.btn_yes.pack(side="left", padx=5, expand=True)
            
            # Przycisk NIE (Po prostu zamyka popup, anulując akcję)
            self.btn_no = ctk.CTkButton(btn_frame, text="NIE", fg_color="#c0392b", hover_color="#a93226", width=160, command=self.destroy)
            self.btn_no.pack(side="right", padx=5, expand=True)
        else:
            # Standardowy, pojedynczy przycisk OK dla info/error/success
            self.btn_ok = ctk.CTkButton(self, text="OK", fg_color=border_color, width=120, command=self.destroy)
            self.btn_ok.pack(side="bottom", pady=15)

    def _action_confirm(self):
        """Uruchamia przekazaną akcję i bezpiecznie niszczy okienko popup."""
        if self.on_confirm:
            self.on_confirm()
        self.destroy()