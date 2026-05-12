import customtkinter as ctk
import database
from tkinter import messagebox

class ToolCalcWindow(ctk.CTkToplevel):
    def __init__(self, parent, tool_category="Frezy"):
        super().__init__(parent)
        self.parent = parent
        self.title(f"Konfiguracja: {tool_category}")
        self.geometry("500x780")
        self.attributes("-topmost", True)
        self.grab_set()

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Ustawienia wizualne
        label_font = ("Arial", 12, "bold")
        entry_width = 280
        padding_x = 30
        v_spacing = (0, 5) # Mniejszy odstęp pionowy

        self.settings = database.get_user_settings()

        # --- POLA WEJŚCIOWE ---
        self.add_label("Typ narzędzia:", label_font, padding_x)
        self.type_combo = ctk.CTkComboBox(self.main_frame, width=entry_width, values=database.get_unique_tool_types(tool_category), command=self.update_calculation)
        self.type_combo.set(self.settings.get("last_tool_type", "Frez prosty"))
        self.type_combo.pack(pady=v_spacing, padx=padding_x, anchor="w")

        self.add_label("Liczba ostrzy:", label_font, padding_x)
        self.blades_entry = ctk.CTkEntry(self.main_frame, width=entry_width)
        self.blades_entry.insert(0, self.settings.get("last_blades", "4"))
        self.blades_entry.pack(pady=v_spacing, padx=padding_x, anchor="w")
        self.blades_entry.bind("<KeyRelease>", self.update_calculation)

        self.add_label("Średnica robocza (Ø):", label_font, padding_x)
        self.diam_entry = ctk.CTkEntry(self.main_frame, width=entry_width)
        self.diam_entry.insert(0, self.settings.get("last_diam", "10.0"))
        self.diam_entry.pack(pady=v_spacing, padx=padding_x, anchor="w")
        self.diam_entry.bind("<KeyRelease>", self.on_diam_change)

        self.add_label("Średnica chwytu:", label_font, padding_x)
        self.shank_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.shank_container.pack(fill="x", padx=padding_x, pady=v_spacing, anchor="w")

        self.shank_entry = ctk.CTkEntry(self.shank_container, width=120, state="disabled", fg_color="#222") # Bardzo ciemne tło
        self.shank_entry.pack(side="left")
        
        self.shank_override_var = ctk.BooleanVar(value=False)
        self.shank_cb = ctk.CTkCheckBox(self.shank_container, text="", variable=self.shank_override_var, width=20, command=self.toggle_shank_entry)
        self.shank_cb.pack(side="left", padx=10)

        self.add_label("Ilość sztuk:", label_font, padding_x)
        self.qty_entry = ctk.CTkEntry(self.main_frame, width=entry_width)
        self.qty_entry.insert(0, "1")
        self.qty_entry.pack(pady=v_spacing, padx=padding_x, anchor="w")
        self.qty_entry.bind("<KeyRelease>", self.update_calculation)

        self.add_label("Powłoka:", label_font, padding_x)
        self.coating_combo = ctk.CTkComboBox(self.main_frame, width=entry_width,
                                             values=["Brak"] + database.get_unique_coating_names(), 
                                             command=self.on_coating_change)
        self.coating_combo.set("Brak")
        self.coating_combo.pack(pady=v_spacing, padx=padding_x, anchor="w")

        # Dynamiczne pole długości powłoki (ukryte domyślnie)
        self.length_label = ctk.CTkLabel(self.main_frame, text="Długość powłoki:", font=label_font)
        self.length_combo = ctk.CTkComboBox(self.main_frame, width=entry_width, values=["100"], command=self.update_calculation)

        # --- SEKCJA WYNIKOWA ---
        self.results_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.results_frame.pack(fill="x", padx=padding_x, pady=(15, 0), anchor="w")

        # Ceny ostrzenia
        self.unit_tool_label = ctk.CTkLabel(self.results_frame, text="Ostrzenie jedn.: 0.00 zł", font=("Arial", 11), text_color="gray")
        self.unit_tool_label.pack(anchor="w")
        self.total_tool_label = ctk.CTkLabel(self.results_frame, text="SUMA OSTRZENIE: 0.00 zł", font=("Arial", 18, "bold"), text_color="#28a745")
        self.total_tool_label.pack(anchor="w", pady=(0, 10))

        # Ceny powłoki
        self.unit_coat_label = ctk.CTkLabel(self.results_frame, text="", font=("Arial", 11), text_color="gray")
        self.unit_coat_label.pack(anchor="w")
        self.total_coat_label = ctk.CTkLabel(self.results_frame, text="", font=("Arial", 15, "bold"), text_color="#218838")
        self.total_coat_label.pack(anchor="w")

        self.add_btn = ctk.CTkButton(self.main_frame, text="DODAJ DO KOSZYKA", fg_color="#1f538d", height=45, width=entry_width, command=self.add_to_cart)
        self.add_btn.pack(side="bottom", pady=10, padx=padding_x, anchor="w")

        self.on_diam_change()

    def add_label(self, text, font, padx):
        lbl = ctk.CTkLabel(self.main_frame, text=text, font=font)
        lbl.pack(pady=(5, 0), padx=padx, anchor="w")

    def toggle_shank_entry(self):
        if self.shank_override_var.get():
            self.shank_entry.configure(state="normal", fg_color=["#F9F9FA", "#343638"])
        else:
            self.shank_entry.configure(state="disabled", fg_color="#222")
            self.on_diam_change()
        self.update_calculation()

    def on_diam_change(self, _=None):
        if not self.shank_override_var.get():
            val = self.diam_entry.get()
            self.shank_entry.configure(state="normal")
            self.shank_entry.delete(0, "end")
            self.shank_entry.insert(0, val)
            self.shank_entry.configure(state="disabled")
        self.update_calculation()

    def on_coating_change(self, _=None):
        coating = self.coating_combo.get()
        if coating != "Brak":
            lengths = database.get_coating_lengths(coating)
            self.length_combo.configure(values=lengths)
            # Ustawiamy pierwszą dostępną długość jako domyślną, jeśli nie ma "100"
            if "100" in lengths:
                self.length_combo.set("100")
            elif lengths:
                self.length_combo.set(lengths[0])
                
            self.length_label.pack(pady=(5, 0), padx=30, anchor="w", after=self.coating_combo)
            self.length_combo.pack(pady=(0, 5), padx=30, anchor="w", after=self.length_label)
        else:
            self.length_label.pack_forget()
            self.length_combo.pack_forget()
        self.update_calculation()

    def update_calculation(self, _=None):
        try:
            t_type = self.type_combo.get()
            # Mapowanie ostrzy (2-4 lub pozostałe)
            try:
                b_val = int(self.blades_entry.get())
                b_key = "2-4" if 2 <= b_val <= 4 else "pozostałe"
            except: b_key = "pozostałe"

            d = float(self.diam_entry.get().replace(',', '.')) if self.diam_entry.get() else 0.0
            q = int(self.qty_entry.get()) if self.qty_entry.get() else 0
            coating = self.coating_combo.get()
            length = float(self.length_combo.get()) if coating != "Brak" else 0

            if d > 0 and q > 0:
                # Ostrzenie
                p_tool = database.get_tool_price(t_type, b_key, d, q)
                sum_tool = p_tool * q
                self.unit_tool_label.configure(text=f"Ostrzenie jedn.: {p_tool:.2f} zł")
                self.total_tool_label.configure(text=f"SUMA OSTRZENIE: {sum_tool:.2f} zł")

                # Powłoka (niezależna)
                if coating != "Brak":
                    p_coat = database.get_coating_price_refined(coating, d, length)
                    sum_coat = p_coat * q
                    self.unit_coat_label.configure(text=f"Powlekanie jedn.: {p_coat:.2f} zł")
                    self.total_coat_label.configure(text=f"SUMA POWLEKANIE: {sum_coat:.2f} zł")
                else:
                    self.unit_coat_label.configure(text="")
                    self.total_coat_label.configure(text="")
            else:
                self.total_tool_label.configure(text="SUMA OSTRZENIE: 0.00 zł")
        except: pass

    def add_to_cart(self):
        database.save_user_settings(self.type_combo.get(), self.blades_entry.get(), self.diam_entry.get())
        
        # Przygotowujemy dane dla koszyka (rozdzielone ceny)
        item = {
            "name": f"{self.type_combo.get()} Ø{self.diam_entry.get()}",
            "qty": self.qty_entry.get(),
            "tool_unit": self.unit_tool_label.cget("text").split(": ")[1],
            "coat_unit": self.unit_coat_label.cget("text").split(": ")[1] if self.unit_coat_label.cget("text") else "0.00 zł",
            "coating": self.coating_combo.get(),
            "total_tool": self.total_tool_label.cget("text").split(": ")[1],
            "total_coat": self.total_coat_label.cget("text").split(": ")[1] if self.total_coat_label.cget("text") else "0.00 zł"
        }
        self.parent.add_item_to_basket(item)
        self.destroy()