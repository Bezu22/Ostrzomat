import customtkinter as ctk
import database as database

class FrezModule(ctk.CTkFrame):
    def __init__(self, parent, update_callback, settings, main_window):
        super().__init__(parent, fg_color="transparent")
        self.update_callback = update_callback
        self.main_window = main_window
        self.shank_override = ctk.BooleanVar(value=False)
        
        label_font = ("Arial", 12, "bold")
        
        # TYP - wczytujemy z settings
        self.add_label("Typ narzędzia:", label_font)
        self.type_combo = ctk.CTkComboBox(self, width=280, 
                                          values=database.get_unique_tool_types("Frezy"), 
                                          command=self.update_callback)
        # Ustawiamy wartość z cache
        self.type_combo.set(settings.get("last_tool_type", "Frez prosty"))
        self.type_combo.pack(pady=(0, 10), anchor="w")

        # OSTRZA - wczytujemy z settings
        self.add_label("Liczba ostrzy (Z):", label_font)
        self.blades_entry = ctk.CTkEntry(self, width=280)
        self.blades_entry.insert(0, settings.get("last_blades", "4"))
        self.blades_entry.pack(pady=(0, 10), anchor="w")
        self.blades_entry.bind("<KeyRelease>", self.update_callback)

        # CHWYT
        self.add_label("Średnica chwytu:", label_font)
        self.shank_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.shank_frame.pack(fill="x", pady=(0, 10), anchor="w")
        
        self.shank_entry = ctk.CTkEntry(self.shank_frame, width=120, state="disabled", fg_color="#1a1a1a")
        self.shank_entry.pack(side="left")
        
        # 2. TERAZ MOŻEMY WYWOŁAĆ SYNCHRONIZACJĘ
        self.sync_shank_with_diam()
        
        # Checkbox bez tekstu
        self.shank_cb = ctk.CTkCheckBox(self.shank_frame, text="", variable=self.shank_override, 
                                        command=self.toggle_shank, width=24)
        self.shank_cb.pack(side="left", padx=5)

    def add_label(self, text, font):
        ctk.CTkLabel(self, text=text, font=font).pack(pady=(4, 0), anchor="w")

    def sync_shank_with_diam(self):
        """Kopiuje wartość ze średnicy roboczej do chwytu, jeśli checkbox nie jest zaznaczony."""
        if not self.shank_override.get():
            current_diam = self.main_window.diam_entry.get()
            self.shank_entry.configure(state="normal")
            self.shank_entry.delete(0, "end")
            self.shank_entry.insert(0, current_diam)
            self.shank_entry.configure(state="disabled")

    def toggle_shank(self):
        """Blokuje/odblokowuje pole chwytu."""
        if self.shank_override.get():
            self.shank_entry.configure(state="normal", fg_color=["#F9F9FA", "#343638"])
        else:
            self.shank_entry.configure(state="disabled", fg_color="#1a1a1a")
            self.sync_shank_with_diam() # Przy odznaczeniu wróć do wartości roboczej
        self.update_callback()

    def get_data(self):
        return {
            "type": self.type_combo.get(),
            "z": self.blades_entry.get(),
            "shank": self.shank_entry.get()
        }