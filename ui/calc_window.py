import customtkinter as ctk
import database
from tkinter import messagebox

class ToolCalcWindow(ctk.CTkToplevel):
    def __init__(self, parent, tool_category="Frezy"):
        super().__init__(parent)
        self.parent = parent
        self.title(f"Konfiguracja: {tool_category}")
        self.geometry("500x850") # Rozciągnięte okno w pionie
        self.attributes("-topmost", True)
        self.grab_set()

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Ustawienia wizualne
        label_font = ("Arial", 12, "bold")
        entry_width = 280
        padding_x = 35
        v_spacing = (0, 8) # Większy odstęp dla lepszej czytelności

        self.settings = database.get_user_settings()

        # --- 1. TYP I OSTRZA ---
        self.add_label("Typ narzędzia:", label_font, padding_x)
        self.type_combo = ctk.CTkComboBox(self.main_frame, width=entry_width, 
                                          values=database.get_unique_tool_types(tool_category), 
                                          command=self.update_calculation)
        self.type_combo.set(self.settings.get("last_tool_type", "Frez prosty"))
        self.type_combo.pack(pady=v_spacing, padx=padding_x, anchor="w")

        self.add_label("Liczba ostrzy:", label_font, padding_x)
        self.blades_entry = ctk.CTkEntry(self.main_frame, width=entry_width)
        self.blades_entry.insert(0, self.settings.get("last_blades", "4"))
        self.blades_entry.pack(pady=v_spacing, padx=padding_x, anchor="w")
        self.blades_entry.bind("<KeyRelease>", self.update_calculation)

        # --- 2. ŚREDNICE ---
        self.add_label("Średnica robocza (Ø):", label_font, padding_x)
        self.diam_entry = ctk.CTkEntry(self.main_frame, width=entry_width)
        self.diam_entry.insert(0, self.settings.get("last_diam", "10.0"))
        self.diam_entry.pack(pady=v_spacing, padx=padding_x, anchor="w")
        self.diam_entry.bind("<KeyRelease>", self.on_diam_change)

        self.add_label("Średnica chwytu:", label_font, padding_x)
        self.shank_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.shank_container.pack(fill="x", padx=padding_x, pady=v_spacing, anchor="w")

        self.shank_entry = ctk.CTkEntry(self.shank_container, width=120, state="disabled", fg_color="#1a1a1a")
        self.shank_entry.pack(side="left")
        
        self.shank_override_var = ctk.BooleanVar(value=False)
        self.shank_cb = ctk.CTkCheckBox(self.shank_container, text="", variable=self.shank_override_var, 
                                        width=20, command=self.toggle_shank_entry)
        self.shank_cb.pack(side="left", padx=10)

        # --- 3. ILOŚĆ SZTUK ---
        self.add_label("Ilość sztuk:", label_font, padding_x)
        self.qty_entry = ctk.CTkEntry(self.main_frame, width=entry_width)
        self.qty_entry.insert(0, "1")
        self.qty_entry.pack(pady=v_spacing, padx=padding_x, anchor="w")
        self.qty_entry.bind("<KeyRelease>", self.update_calculation)

        # --- 4. USŁUGI DODATKOWE ---
        self.add_label("Usługi dodatkowe:", label_font, padding_x)
        self.services_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.services_frame.pack(fill="x", padx=padding_x, pady=(5, 15), anchor="w")

        self.extra_services = {
            "ciecie": {"label": "Cięcie", "db_name": "Cięcie"},
            "opuszczenie": {"label": "Opuszczenie", "db_name": "Zaniżenie średnicy"},
            "polerowanie": {"label": "Polerowanie", "db_name": "Polerowanie rowka"}
        }
        self.service_vars = {}

        for key, info in self.extra_services.items():
            var = ctk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(self.services_frame, text=info["label"], variable=var, 
                                 command=self.update_calculation, font=("Arial", 11), width=100)
            cb.pack(side="left", padx=(0, 15))
            self.service_vars[key] = var

        # --- 5. POWŁOKA ---
        self.add_label("Powłoka i długość:", label_font, padding_x)
        self.coating_combo = ctk.CTkComboBox(self.main_frame, width=entry_width,
                                             values=["Brak"] + database.get_unique_coating_names(), 
                                             command=self.on_coating_change)
        self.coating_combo.set("Brak")
        self.coating_combo.pack(pady=v_spacing, padx=padding_x, anchor="w")

        self.length_combo = ctk.CTkComboBox(self.main_frame, width=entry_width, values=["100"], command=self.update_calculation)

        # --- 6. SEKCJA WYNIKOWA ---
        self.results_frame = ctk.CTkFrame(self.main_frame, fg_color="#222", corner_radius=10)
        self.results_frame.pack(fill="x", padx=padding_x, pady=(20, 20), anchor="w")

        self.unit_tool_label = ctk.CTkLabel(self.results_frame, text="Ostrzenie jedn.: 0.00 zł", font=("Arial", 11), text_color="gray")
        self.unit_tool_label.pack(anchor="w", padx=15, pady=(10, 0))
        self.total_tool_label = ctk.CTkLabel(self.results_frame, text="SUMA OSTRZENIE: 0.00 zł", font=("Arial", 18, "bold"), text_color="#28a745")
        self.total_tool_label.pack(anchor="w", padx=15)

        self.unit_extra_label = ctk.CTkLabel(self.results_frame, text="", font=("Arial", 11), text_color="gray")
        self.unit_extra_label.pack(anchor="w", padx=15)
        self.total_extra_label = ctk.CTkLabel(self.results_frame, text="", font=("Arial", 15, "bold"), text_color="#3498db")
        self.total_extra_label.pack(anchor="w", padx=15)

        self.unit_coat_label = ctk.CTkLabel(self.results_frame, text="", font=("Arial", 11), text_color="gray")
        self.unit_coat_label.pack(anchor="w", padx=15)
        self.total_coat_label = ctk.CTkLabel(self.results_frame, text="", font=("Arial", 15, "bold"), text_color="#f1c40f")
        self.total_coat_label.pack(anchor="w", padx=15, pady=(0, 10))

        self.add_btn = ctk.CTkButton(self.main_frame, text="DODAJ DO KOSZYKA", fg_color="#1f538d", height=50, width=entry_width, command=self.add_to_cart)
        self.add_btn.pack(side="bottom", pady=10, padx=padding_x, anchor="w")

        self.on_diam_change()

    def add_label(self, text, font, padx):
        lbl = ctk.CTkLabel(self.main_frame, text=text, font=font)
        lbl.pack(pady=(4, 0), padx=padx, anchor="w")

    def toggle_shank_entry(self):
        if self.shank_override_var.get():
            self.shank_entry.configure(state="normal", fg_color=["#F9F9FA", "#343638"])
        else:
            self.shank_entry.configure(state="disabled", fg_color="#1a1a1a")
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
            self.length_combo.set("100" if "100" in lengths else lengths[0])
            self.length_combo.pack(pady=(2, 5), padx=35, anchor="w", after=self.coating_combo)
        else:
            self.length_combo.pack_forget()
        self.update_calculation()

    def validate_inputs(self):
        try:
            d_str = self.diam_entry.get().replace(',', '.')
            if not d_str: return False
            float(d_str)
            
            b_str = self.blades_entry.get()
            if not b_str: return False
            int(b_str)
            
            q_str = self.qty_entry.get()
            if not q_str: return False
            int(q_str)
            return True
        except ValueError:
            return False

    def update_calculation(self, _=None):
        # PRZYWRÓCONA WALIDACJA
        if not self.validate_inputs():
            self.total_tool_label.configure(text="BŁĘDNE DANE", text_color="#e74c3c")
            self.unit_tool_label.configure(text="")
            self.unit_extra_label.configure(text="")
            self.total_extra_label.configure(text="")
            self.unit_coat_label.configure(text="")
            self.total_coat_label.configure(text="")
            return

        try:
            t_type = self.type_combo.get()
            b_val = int(self.blades_entry.get())
            b_key = "2-4" if 2 <= b_val <= 4 else "pozostałe"

            d = float(self.diam_entry.get().replace(',', '.'))
            q = int(self.qty_entry.get())
            
            coating = self.coating_combo.get()
            length = float(self.length_combo.get()) if (coating != "Brak" and self.length_combo.get()) else 0

            # OSTRZENIE
            p_tool = database.get_tool_price(t_type, b_key, d, q)
            sum_tool = p_tool * q
            self.unit_tool_label.configure(text=f"Ostrzenie jedn.: {p_tool:.2f} zł")
            self.total_tool_label.configure(text=f"SUMA OSTRZENIE: {sum_tool:.2f} zł", text_color="#28a745")

            # USŁUGI
            total_extra_unit = 0.0
            active_extras = []
            for key, info in self.extra_services.items():
                if self.service_vars[key].get():
                    price = database.get_service_price_refined(info["db_name"], d)
                    total_extra_unit += price
                    active_extras.append(info["label"])

            if total_extra_unit > 0:
                sum_extra = total_extra_unit * q
                self.unit_extra_label.configure(text=f"Usługi ({', '.join(active_extras)}) jedn.: {total_extra_unit:.2f} zł")
                self.total_extra_label.configure(text=f"SUMA USŁUGI: {sum_extra:.2f} zł")
            else:
                self.unit_extra_label.configure(text="")
                self.total_extra_label.configure(text="")

            # POWŁOKA
            if coating != "Brak":
                # Pobieramy długość, sprawdzając czy combo nie jest puste
                current_len_str = self.length_combo.get()
                length = float(current_len_str) if current_len_str else 100.0
                
                p_coat = database.get_coating_price_refined(coating, d, length)
                
                if p_coat > 0:
                    sum_coat = p_coat * q
                    self.unit_coat_label.configure(text=f"Powlekanie ({coating}) jedn.: {p_coat:.2f} zł")
                    self.total_coat_label.configure(text=f"SUMA POWLEKANIE: {sum_coat:.2f} zł", text_color="#f1c40f")
                else:
                    # Jeśli baza zwróci 0 (np. brak zakresu), poinformuj o tym
                    self.unit_coat_label.configure(text="Brak ceny dla tych wymiarów")
                    self.total_coat_label.configure(text="")
            else:
                self.unit_coat_label.configure(text="")
                self.total_coat_label.configure(text="")
                
        except Exception as e:
            print(f"Błąd: {e}")

    def add_to_cart(self):
        if not self.validate_inputs():
            messagebox.showerror("Błąd", "Wprowadź poprawne liczby!")
            return
            
        # Pobieramy surowe dane
        coating_type = self.coating_combo.get()
        # Przygotowujemy obiekt z rozbiciem na parametry
        item = {
            "type": self.type_combo.get(),
            "diam": self.diam_entry.get().replace(',', '.'),
            "z": self.blades_entry.get(),
            "qty": self.qty_entry.get(),
            "tool_unit": self.unit_tool_label.cget("text").split(": ")[1] if ":" in self.unit_tool_label.cget("text") else "0.00 zł",
            "coat_name": coating_type,
            "coat_len": self.length_combo.get() if coating_type != "Brak" else "-",
            "coat_unit": self.unit_coat_label.cget("text").split(": ")[1] if self.unit_coat_label.cget("text") else "0.00 zł",
            "total_coat": self.total_coat_label.cget("text").split(": ")[1] if self.total_coat_label.cget("text") else "0.00 zł",
            "extra_unit": self.unit_extra_label.cget("text").split(": ")[1] if self.unit_extra_label.cget("text") else "0.00 zł",
            "total_tool": self.total_tool_label.cget("text").split(": ")[1],
            "total_extra": self.total_extra_label.cget("text").split(": ")[1] if self.total_extra_label.cget("text") else "0.00 zł"
        }
        self.parent.add_item_to_basket(item)
        self.destroy()