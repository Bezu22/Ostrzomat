import math
import customtkinter as ctk
import database
from logic import cart_logic
from ui.style import AppStyle


class DrillModule(ctk.CTkFrame):
    def __init__(self, parent, update_callback, settings):
        super().__init__(parent, fg_color="transparent")
        self.update_callback = update_callback
        self.settings = settings
        self.shank_override = ctk.BooleanVar(value=False)

        # --- GŁÓWNY KONTENER DWUKOLUMNOWY ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        self.left_col = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.right_col = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.right_col.pack(side="left", fill="both", expand=True, padx=(10, 0))

        px = AppStyle.PAD_LARGE
        py_small = (0, AppStyle.PAD_SMALL)

        # ================= KOLUMNA LEWA =================
        # --- 1. TYP i ostrza ---
        self.add_label(self.left_col, "Typ narzędzia:", AppStyle.get_bold_font())
        drill_types = database.get_unique_tool_types("Wiertla")
        self.type_combo = ctk.CTkComboBox(
            self.left_col, 
            width=300, 
            values=drill_types if drill_types else ["Wiertło N"], 
            command=self.update_callback,
            **AppStyle.get_combo_style()
        )
        self.type_combo.set(settings.get("last_drill_type", drill_types[0] if drill_types else "Wiertło N"))
        self.type_combo.configure(state="readonly") 
        self.type_combo.pack(pady=py_small, padx=px, anchor="w")

        self.add_label(self.left_col, "Liczba ostrzy (Z):", AppStyle.get_bold_font())
        self.blades_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.blades_entry.insert(0, settings.get("last_drill_blades", "2"))
        self.blades_entry.pack(pady=py_small, padx=px, anchor="w")
        self.blades_entry.bind("<KeyRelease>", lambda e: self.update_callback())

        # --- 2. ŚREDNICA ROBOCZA ---
        self.add_label(self.left_col, "Średnica robocza:", AppStyle.get_bold_font())
        self.diam_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.diam_entry.insert(0, settings.get("last_drill_diam", "10.0"))
        self.diam_entry.pack(pady=py_small, padx=px, anchor="w")
        self.diam_entry.bind("<KeyRelease>", self.on_diam_change)

        # --- 3. CHWYT ---
        self.add_label(self.left_col, "Średnica chwytu:", AppStyle.get_bold_font())
        s_frame = ctk.CTkFrame(self.left_col, fg_color="transparent")
        s_frame.pack(fill="x", pady=py_small, padx=px)
        
        self.shank_entry = ctk.CTkEntry(s_frame, width=140, **AppStyle.get_entry_style())
        self.shank_entry.insert(0, settings.get("last_drill_shank", "10.0"))
        self.shank_entry.pack(side="left")
        
        self.shank_cb = ctk.CTkCheckBox(
            s_frame, 
            text="", 
            width=24, 
            variable=self.shank_override, 
            command=self.toggle_shank,
            fg_color=AppStyle.COLOR_PRIMARY,
            hover_color=AppStyle.COLOR_PRIMARY_HOVER
        )
        self.shank_cb.pack(side="left", padx=AppStyle.PAD_MEDIUM)

        # --- 4. POWŁOKA i długość ---
        self.add_label(self.left_col, "Powłoka:", AppStyle.get_bold_font())
        self.coat_combo = ctk.CTkComboBox(
            self.left_col, 
            width=300, 
            values=["Brak"] + database.get_unique_coating_names(), 
            command=self.on_coating_change,
            **AppStyle.get_combo_style()
        )
        self.coat_combo.set("Brak")
        self.coat_combo.configure(state="readonly")
        self.coat_combo.pack(pady=py_small, padx=px, anchor="w")

        self.len_label = ctk.CTkLabel(self.left_col, text="Długość (L):", font=AppStyle.get_bold_font(), text_color=AppStyle.COLOR_TEXT_DARK)
        self.len_label.pack(pady=(AppStyle.PAD_SMALL, 0), padx=px, anchor="w")

        self.len_combo = ctk.CTkComboBox(
            self.left_col, 
            width=300, 
            values=[], 
            command=self.update_callback,
            **AppStyle.get_combo_style()
        )
        self.len_combo.configure(state="readonly")
        self.len_combo.pack(pady=(0, AppStyle.PAD_MEDIUM), padx=px, anchor="w")

        # --- 5. ILOŚĆ SZTUK ---
        self.add_label(self.left_col, "Ilość sztuk:", AppStyle.get_bold_font())
        self.qty_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.qty_entry.insert(0, "1")
        self.qty_entry.pack(pady=(0, AppStyle.PAD_MEDIUM), padx=px, anchor="w")
        self.qty_entry.bind("<KeyRelease>", lambda e: self.update_callback())

        # ================= KOLUMNA PRAWA =================
        # --- 6. USŁUGI DODATKOWE ---
        self.add_label(self.right_col, "Usługi dodatkowe:", AppStyle.get_bold_font())
        self.service_vars = {
            "ciecie": ctk.BooleanVar(),
            "opuszczenie": ctk.BooleanVar(),
            "polerowanie": ctk.BooleanVar(),
            "zuzycie": ctk.BooleanVar()
        }
        self.service_price_labels = {}
        self.opuszczenie_mult = 1

        services_info = [
            ("ciecie", "Cięcie narzędzia (skracanie)"),
            ("opuszczenie", "Zaniżenie średnicy (szyjka)"),
            ("polerowanie", "Polerowanie rowka wiórowego"),
            ("zuzycie", "Ciężkie zużycie / wyszczerbienia (+5%)")
        ]

        for key, text in services_info:
            row_frame = ctk.CTkFrame(self.right_col, fg_color="transparent")
            row_frame.pack(fill="x", padx=px, pady=2, anchor="w")

            cb = ctk.CTkCheckBox(
                row_frame, text=text, variable=self.service_vars[key], 
                command=self._on_service_toggle, font=AppStyle.get_normal_font(),
                fg_color=AppStyle.COLOR_PRIMARY, hover_color=AppStyle.COLOR_PRIMARY_HOVER,
                text_color=AppStyle.COLOR_TEXT_DARK
            )
            cb.pack(side="left")

            if key == "opuszczenie":
                self.mult_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
                
                btn_minus = ctk.CTkButton(
                    self.mult_frame, text="-", width=20, height=20, 
                    fg_color=AppStyle.COLOR_MUTED, hover_color=AppStyle.COLOR_MUTED_HOVER, 
                    command=lambda: self._change_multiplier(-1)
                )
                btn_minus.pack(side="left", padx=2)
                
                self.lbl_mult_val = ctk.CTkLabel(self.mult_frame, text="10 mm (x1)", font=AppStyle.get_bold_font(), text_color=AppStyle.COLOR_TEXT_ACCENT, width=70)
                self.lbl_mult_val.pack(side="left", padx=AppStyle.PAD_SMALL)
                
                btn_plus = ctk.CTkButton(
                    self.mult_frame, text="+", width=20, height=20, 
                    fg_color=AppStyle.COLOR_MUTED, hover_color=AppStyle.COLOR_MUTED_HOVER, 
                    command=lambda: self._change_multiplier(1)
                )
                btn_plus.pack(side="left", padx=2)

            lbl_p = ctk.CTkLabel(row_frame, text="", font=AppStyle.get_normal_font(), text_color=AppStyle.COLOR_SUCCESS)
            lbl_p.pack(side="right", padx=AppStyle.PAD_SMALL)
            self.service_price_labels[key] = lbl_p

        # Uruchomienie domyślnych funkcji na starcie
        self.on_coating_change()
        self.toggle_shank()

    # ================= LOGIKA WIDOKU =================
    def add_label(self, parent_frame, text, font):
        """Pomocnicza metoda wymaga teraz podania ramki, do której etykieta ma trafić."""
        ctk.CTkLabel(parent_frame, text=text, font=font, text_color=AppStyle.COLOR_TEXT_DARK).pack(pady=(AppStyle.PAD_SMALL, 0), padx=AppStyle.PAD_LARGE, anchor="w")

    def calculate_shank_value(self, diam_str):
        """Zwraca bezpiecznie wyliczoną średnicę chwytu parzystą w górę."""
        try:
            val = diam_str.replace(',', '.')
            if not val:
                return ""
            d = float(val)
            if d <= 0:
                return ""
            
            # Jeśli wartość to idealnie parzysta liczba całkowita np. 8.0, 10.0
            if d.is_integer() and int(d) % 2 == 0:
                return str(int(d))
            
            # Zaokrąglenie w górę np. 8.5 -> 9,  4.7 -> 5
            c = math.ceil(d)
            
            # Jeśli po zaokrągleniu wynik jest nieparzysty, podbijamy do parzystej
            if c % 2 != 0:
                c += 1
                
            return str(c)
        except ValueError:
            # W przypadku wpisania liter po prostu zwracamy puste, 
            # prawdziwa walidacja następuje dopiero przy zapisie!
            return ""

    def on_diam_change(self, _=None):
        if not self.shank_override.get():
            raw_val = self.diam_entry.get()
            new_shank = self.calculate_shank_value(raw_val)

            self.shank_entry.configure(state="normal")
            self.shank_entry.delete(0, "end")
            self.shank_entry.insert(0, new_shank)
            self.shank_entry.configure(state="disabled")
        self.update_callback()

    def toggle_shank(self):
        if self.shank_override.get():
            self.shank_entry.configure(
                state="normal", fg_color=AppStyle.COLOR_BG_LIGHT,
                border_color=AppStyle.COLOR_SECONDARY, border_width=2
            )
        else:
            self.shank_entry.configure(
                state="disabled", fg_color=AppStyle.COLOR_MAIN_BG,
                border_color=AppStyle.COLOR_MUTED, border_width=1
            )
            self.on_diam_change()
        self.update_callback()

    def on_coating_change(self, _=None):
        selected = self.coat_combo.get()
        lengths = database.get_unique_coating_lengths(selected)
        if lengths:
            self.len_combo.configure(values=lengths)
            self.len_combo.set(lengths[0])
        self.update_callback()

    # ================= LOGIKA DANYCH I WALIDACJA =================
    def validate_all(self, diam, z, qty, shank):
        try:
            # Sprawdzamy czy dają się przekształcić na liczby z kropką
            float(diam)
            float(shank)
            if not z.isdigit() or not qty.isdigit():
                raise ValueError()
            return True
        except ValueError:
            from ui.components import OstrzomatPopup
            OstrzomatPopup(self.master, title="Błąd", message="Wprowadzono nieprawidłowe wartości (litery/znaki specjalne). Popraw je przed kalkulacją!", type="error")
            return False
    
    def get_full_item_data(self, run_validation=False):
        try:
            diam = self.diam_entry.get().replace(',', '.')
            shank = self.shank_entry.get().replace(',', '.')
            qty = self.qty_entry.get() or "1" 
            t_type = self.type_combo.get()
            blades = self.blades_entry.get()
            coat = self.coat_combo.get()
            coat_len = self.len_combo.get() if hasattr(self, 'len_combo') else "100"

            if run_validation:
                # Blokujemy dalszą pracę jeśli są litery
                if not self.validate_all(diam, blades, qty, shank):
                    return None
            
            heavy_wear_active = self.service_vars["zuzycie"].get()
            # Pamiętaj, dla wierteł przekazujemy "Wiertla" wewnątrz bazy 
            t_j, t_r = cart_logic.calculate_tool_price(t_type, blades, diam, qty, heavy_wear=heavy_wear_active)
            c_j, c_r = cart_logic.calculate_coating_price(coat, diam, coat_len, qty)
            
            e_j_total, e_r_total, active_labels = cart_logic.calculate_extra_services(
                self.service_vars, diam, qty, opuszczenie_multiplier=self.opuszczenie_mult
            )

            for key in self.service_vars:
                if key == "zuzycie":
                    self.service_price_labels[key].configure(text="+5% do ostrz." if self.service_vars[key].get() else "")
                    continue

                if self.service_vars[key].get():
                    db_name = "Cięcie" if key == "ciecie" else "Zaniżenie średnicy" if key == "opuszczenie" else "Polerowanie rowka"
                    price = database.get_service_price_refined(db_name, float(diam))
                    if key == "opuszczenie":
                        price = price * self.opuszczenie_mult
                    self.service_price_labels[key].configure(text=f"+{price:.2f} zł")
                else:
                    self.service_price_labels[key].configure(text="")

            database.save_user_settings({
                "last_drill_type": t_type, "last_drill_blades": blades,
                "last_drill_diam": diam, "last_drill_shank": shank
            })

            return {
                "type": t_type, "diam": diam, "z": blades, "qty": qty,
                "tool_unit": t_j, "total_tool": t_r,
                "coat_name": coat, "coat_len": coat_len,
                "coat_unit": c_j, "total_coat": c_r,
                "services_status": {k: v.get() for k, v in self.service_vars.items()},
                "opuszczenie_mult": self.opuszczenie_mult,
                "extra_unit": e_j_total, "total_extra": e_r_total
            }
        except Exception as e:
            print(f"Błąd w module DrillModule: {e}")
            return None

    def _on_service_toggle(self):
        if self.service_vars["opuszczenie"].get():
            self.mult_frame.pack(side="left", padx=AppStyle.PAD_MEDIUM)
        else:
            self.mult_frame.pack_forget()
            self.opuszczenie_mult = 1
            self.lbl_mult_val.configure(text="10 mm (x1)")
            
        self.update_callback()
    
    def _change_multiplier(self, delta):
        new_val = self.opuszczenie_mult + delta
        if new_val >= 1:
            self.opuszczenie_mult = new_val
            mm_text = f"{new_val * 10} mm"
            self.lbl_mult_val.configure(text=f"{mm_text} (x{new_val})")
            self.update_callback()