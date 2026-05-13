import customtkinter as ctk
import database
from logic import cart_logic

class FrezModule(ctk.CTkFrame):
    def __init__(self, parent, update_callback, settings):
        super().__init__(parent, fg_color="transparent")
        self.update_callback = update_callback
        self.settings = settings
        self.shank_override = ctk.BooleanVar(value=False)
        
        f_bold = ("Arial", 12, "bold")
        f_price = ("Arial", 11, "italic")
        px = 20  # padding boczny
        py_small = (0, 5) # mniejszy odstęp pionowy
        
        # --- 1. TYP i ostrza ---
        self.add_label("Typ narzędzia:", f_bold)
        self.type_combo = ctk.CTkComboBox(self, width=300, values=database.get_unique_tool_types("Frezy"), command=self.update_callback)
        self.type_combo.set(settings.get("last_tool_type", "Frez prosty"))
        self.type_combo.configure(state="readonly") 
        self.type_combo.pack(pady=py_small, padx=px, anchor="w")

        self.add_label("Liczba ostrzy:", f_bold)
        self.blades_entry = ctk.CTkEntry(self, width=300)
        self.blades_entry.insert(0, settings.get("last_blades", "4"))
        self.blades_entry.pack(pady=py_small, padx=px, anchor="w")
        self.blades_entry.bind("<KeyRelease>", lambda e: self.update_callback())

        # --- 2. ŚREDNICA ROBOCZA ---
        self.add_label("Średnica robocza:", f_bold)
        self.diam_entry = ctk.CTkEntry(self, width=300)
        self.diam_entry.insert(0, settings.get("last_diam", "10.0"))
        self.diam_entry.pack(pady=py_small, padx=px, anchor="w")
        self.diam_entry.bind("<KeyRelease>", self.on_diam_change)

        # --- 3. CHWYT  ---
        self.add_label("Średnica chwytu:", f_bold)
        s_frame = ctk.CTkFrame(self, fg_color="transparent")
        s_frame.pack(fill="x", pady=py_small, padx=px)
        
        self.shank_entry = ctk.CTkEntry(s_frame, width=140)
        self.shank_entry.insert(0, settings.get("last_shank", "10.0"))
        self.shank_entry.pack(side="left")
        
        # Checkbox obok pola
        self.shank_cb = ctk.CTkCheckBox(s_frame, text="", width=24, variable=self.shank_override, command=self.toggle_shank)
        self.shank_cb.pack(side="left", padx=10)

        # --- 4. POWŁOKA ---
        self.add_label("Powłoka:", f_bold)
        self.coat_combo = ctk.CTkComboBox(self, width=300, values=["Brak"] + database.get_unique_coating_names(), command=self.on_coating_change)
        self.coat_combo.set("Brak")
        self.coat_combo.configure(state="readonly")
        self.coat_combo.pack(pady=py_small, padx=px, anchor="w")

        # Dynamiczne pola długości (ukryte domyślnie)
        self.len_label = ctk.CTkLabel(self, text="Długość (L):", font=f_bold)
        self.len_combo = ctk.CTkComboBox(self, width=300, values=[], command=self.update_callback)
        self.len_combo.configure(state="readonly")

        # --- 5. USŁUGI DODATKOWE (Pionowo z cenami obok) ---
        self.add_label("Usługi dodatkowe:", f_bold)
        self.service_vars = {
            "ciecie": ctk.BooleanVar(),
            "opuszczenie": ctk.BooleanVar(),
            "polerowanie": ctk.BooleanVar()
        }
        self.service_price_labels = {}
        
        service_names = {
            "ciecie": "Cięcie",
            "opuszczenie": "Zaniżenie",
            "polerowanie": "Polerowanie"
        }

        for key, label_text in service_names.items():
            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(fill="x", padx=px+10, pady=1)
            
            cb = ctk.CTkCheckBox(row, text=label_text, variable=self.service_vars[key], command=self.update_callback)
            cb.pack(side="left")
            
            # Etykieta na cenę po prawej
            p_lbl = ctk.CTkLabel(row, text="", font=f_price, text_color="#aaa")
            p_lbl.pack(side="right", padx=20)
            self.service_price_labels[key] = p_lbl

        # --- 6. ILOŚĆ SZTUK ---
        self.add_label("Ilość sztuk:", f_bold)
        self.qty_entry = ctk.CTkEntry(self, width=300)
        self.qty_entry.insert(0, "1")
        self.qty_entry.pack(pady=(0, 10), padx=px, anchor="w")
        self.qty_entry.bind("<KeyRelease>", lambda e: self.update_callback())
        
        # Startowa synchronizacja
        self.toggle_shank()

    def add_label(self, text, font):
        ctk.CTkLabel(self, text=text, font=font).pack(pady=(5, 0), padx=20, anchor="w")

    def on_diam_change(self, _=None):
        if not self.shank_override.get():
            val = self.diam_entry.get()
            self.shank_entry.configure(state="normal")
            self.shank_entry.delete(0, "end")
            self.shank_entry.insert(0, val)
            self.shank_entry.configure(state="disabled")
        self.update_callback()

    def toggle_shank(self):
        if self.shank_override.get():
            # Aktywny - jasne tło
            self.shank_entry.configure(state="normal", fg_color=["#F9F9FA", "#343638"], border_color="#1f538d")
        else:
            # Nieaktywny - wyraźnie ciemniejsze/inne tło
            self.shank_entry.configure(state="disabled", fg_color=["#D1D1D1", "#1A1A1A"], border_color="#444")
            self.on_diam_change()
        self.update_callback()

    def on_coating_change(self, _=None):
        selected = self.coat_combo.get()
        # Ukrywamy, aby zresetować pozycję
        self.len_label.pack_forget()
        self.len_combo.pack_forget()
        
        if selected != "Brak":
            lengths = database.get_unique_coating_lengths(selected)
            if lengths:
                self.len_combo.configure(values=lengths)
                self.len_combo.set(lengths[0])
                
                # Używamy parametru 'after', aby wstawić elementy dokładnie pod listę powłok
                self.len_label.pack(pady=(5,0), padx=20, anchor="w", after=self.coat_combo)
                self.len_combo.pack(pady=(0,10), padx=20, anchor="w", after=self.len_label)
        
        self.update_callback()

    def validate_all(self, diam, z, qty):
        """Sprawdza dane i wyrzuca popup tylko gdy jest to wymagane."""
        try:
            float(diam)
            if not z.isdigit() or not qty.isdigit():
                raise ValueError()
            return True
        except ValueError:
            # Importujemy lokalnie, żeby uniknąć problemów z cyklicznym importem
            from ui.calc_window import OstrzomatPopup
            OstrzomatPopup(self.master, title="Błąd", message="Sprawdź wartości liczbowe!", type="error")
            return False
    
    def get_full_item_data(self,run_validation=False):
        try:
            diam = self.diam_entry.get().replace(',', '.')
            qty = self.qty_entry.get() or "1" 
            t_type = self.type_combo.get()
            blades = self.blades_entry.get()
            coat = self.coat_combo.get()
            coat_len = self.len_combo.get() if (coat != "Brak" and hasattr(self, 'len_combo')) else "100"

            # WALIDACJA: Odpala się TYLKO gdy run_validation=True (czyli przy dodawaniu do koszyka)
            if run_validation:
                if not self.validate_all(diam, blades, qty):
                    return None  # Przerywa, jeśli walidacja nie przeszła
            
            # Obliczenia w cart_logic
            t_j, t_r = cart_logic.calculate_tool_price(t_type, blades, diam, qty)
            c_j, c_r = cart_logic.calculate_coating_price(coat, diam, coat_len, qty)
            e_j_total, e_r_total, _ = cart_logic.calculate_extra_services(self.service_vars, diam, qty)

            # --- AKTUALIZACJA CEN JEDNOSTKOWYCH PRZY CHECKBOXACH ---
            for key in self.service_vars:
                if self.service_vars[key].get():
                    db_name = "Cięcie" if key=="ciecie" else "Zaniżenie średnicy" if key=="opuszczenie" else "Polerowanie rowka"
                    price = database.get_service_price_refined(db_name, float(diam))
                    self.service_price_labels[key].configure(text=f"+{price:.2f} zł")
                else:
                    self.service_price_labels[key].configure(text="")

            database.save_user_settings({
                "last_tool_type": t_type, "last_blades": blades,
                "last_diam": diam, "last_shank": self.shank_entry.get()
            })

            return {
                "type": t_type, "diam": diam, "z": blades, "qty": qty,
                "tool_unit": t_j, "total_tool": t_r,
                "coat_name": coat, "coat_len": coat_len if coat != "Brak" else "-",
                "coat_unit": c_j, "total_coat": c_r,
                "services_status": {k: v.get() for k, v in self.service_vars.items()},
                "extra_unit": e_j_total, "total_extra": e_r_total
            }
        except Exception as e:
            print(f"Error in module: {e}")
            return None