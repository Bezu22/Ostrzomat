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
        self._is_loading_data = False

        # --- GŁÓWNY KONTENER DWUKOLUMNOWY ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        self.main_container.grid_columnconfigure(0, weight=1, uniform="kolumna")
        self.main_container.grid_columnconfigure(1, weight=1, uniform="kolumna")
        self.main_container.grid_rowconfigure(0, weight=1)

        self.left_col = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.right_col = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        px = AppStyle.PAD_LARGE
        py_small = (0, AppStyle.PAD_SMALL)

        # ================= KOLUMNA LEWA =================
        # --- 1. TYP i ostrza ---
        self.add_label(self.left_col, "Typ narzędzia:", AppStyle.get_bold_font())
        
        type_frame = ctk.CTkFrame(self.left_col, fg_color="transparent")
        type_frame.pack(fill="x", pady=py_small, padx=px)

        drill_types = database.get_unique_tool_types("Wiertla")
        self.type_combo = ctk.CTkComboBox(
            type_frame, 
            width=200, 
            values=drill_types if drill_types else ["Wiertło N"], 
            command=self._on_type_change,
            **AppStyle.get_combo_style()
        )
        self.type_combo.set(settings.get("last_drill_type", drill_types[0] if drill_types else "Wiertło N"))
        self.type_combo.configure(state="readonly") 
        self.type_combo.pack(side="left")

        # Wybór liczby stopni (2, 3, 4)
        self.steps_combo = ctk.CTkComboBox(
            type_frame,
            width=80,
            values=["2", "3", "4"],
            command=self._on_steps_change,
            **AppStyle.get_combo_style()
        )
        self.steps_combo.set("2")
        self.steps_combo.configure(state="readonly")

        self.add_label(self.left_col, "Liczba ostrzy (Z):", AppStyle.get_bold_font())
        self.blades_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.blades_entry.insert(0, settings.get("last_drill_blades", "2"))
        self.blades_entry.pack(pady=py_small, padx=px, anchor="w")
        self.blades_entry.bind("<KeyRelease>", lambda e: self.update_callback())

        # --- 2. ŚREDNICA ROBOCZA / STOPNIOWA ---
        self.diam_label = ctk.CTkLabel(self.left_col, text="Średnica robocza:", font=AppStyle.get_bold_font(), text_color=AppStyle.COLOR_TEXT_DARK)
        self.diam_label.pack(pady=(AppStyle.PAD_SMALL, 0), padx=px, anchor="w")

        # Pole dla standardowego wiertła
        self.diam_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.diam_entry.insert(0, settings.get("last_drill_diam", "10.0"))
        self.diam_entry.pack(pady=py_small, padx=px, anchor="w")
        self.diam_entry.bind("<KeyRelease>", self.on_diam_change)

        # Kontener na dynamiczne pola d1, d2, d3, d4 dla wiertła stopniowego
        self.step_diams_frame = ctk.CTkFrame(self.left_col, fg_color="transparent")
        self.step_entries = []

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

            lbl_p = ctk.CTkLabel(
                row_frame, 
                text="", 
                font=AppStyle.get_normal_font(), 
                text_color=AppStyle.COLOR_SUCCESS,
                width=90,
                anchor="e"
            )
            lbl_p.pack(side="right", padx=AppStyle.PAD_SMALL)
            self.service_price_labels[key] = lbl_p

        self._on_type_change()
        self.on_coating_change()
        self.toggle_shank()

    # ================= LOGIKA WIDOKU =================
    def is_step_drill(self):
        return "stopniowe" in self.type_combo.get().lower()

    def _on_type_change(self, _=None):
        if self.is_step_drill():
            self.steps_combo.pack(side="left", padx=(10, 0))
            self.diam_entry.pack_forget()
            self.step_diams_frame.pack(after=self.diam_label, pady=(0, AppStyle.PAD_SMALL), padx=AppStyle.PAD_LARGE, anchor="w", fill="x")
            self._render_step_entries()
        else:
            self.steps_combo.pack_forget()
            self.step_diams_frame.pack_forget()
            self.diam_entry.pack(after=self.diam_label, pady=(0, AppStyle.PAD_SMALL), padx=AppStyle.PAD_LARGE, anchor="w")
            self.on_diam_change()

        if not self._is_loading_data:
            self.update_callback()

    def _on_steps_change(self, _=None):
        self._render_step_entries()
        self.on_diam_change()

    def _render_step_entries(self):
        for w in self.step_diams_frame.winfo_children():
            w.destroy()
        self.step_entries.clear()

        num_steps = int(self.steps_combo.get())
        default_vals = ["3.0", "6.0", "8.0", "10.0"]

        for i in range(num_steps):
            f = ctk.CTkFrame(self.step_diams_frame, fg_color="transparent")
            f.pack(side="left", padx=(0, 6))

            lbl = ctk.CTkLabel(f, text=f"d{i+1}:", font=AppStyle.get_normal_font(), text_color=AppStyle.COLOR_TEXT_DARK)
            lbl.pack(anchor="w")

            entry = ctk.CTkEntry(f, width=55, **AppStyle.get_entry_style())
            # Wstawiamy domyślne wartości tylko, gdy NIE TRWA wczytywanie edycji
            if not self._is_loading_data:
                entry.insert(0, default_vals[i] if i < len(default_vals) else "10.0")
            entry.pack()
            entry.bind("<KeyRelease>", self.on_diam_change)
            self.step_entries.append(entry)

    def add_label(self, parent_frame, text, font):
        ctk.CTkLabel(parent_frame, text=text, font=font, text_color=AppStyle.COLOR_TEXT_DARK).pack(pady=(AppStyle.PAD_SMALL, 0), padx=AppStyle.PAD_LARGE, anchor="w")

    def get_max_diam(self):
        """Wyciąga największą wpisaną średnicę roboczą."""
        if self.is_step_drill():
            max_d = 0.0
            for e in self.step_entries:
                try:
                    val = float(e.get().replace(',', '.').strip())
                    if val > max_d:
                        max_d = val
                except ValueError:
                    pass
            return str(max_d) if max_d > 0 else ""
        else:
            return self.diam_entry.get()

    def calculate_shank_value(self, diam_str):
        try:
            val = diam_str.replace(',', '.')
            if not val:
                return ""
            d = float(val)
            if d <= 0:
                return ""
            
            if d.is_integer() and int(d) % 2 == 0:
                return str(int(d))
            
            c = math.ceil(d)
            if c % 2 != 0:
                c += 1
                
            return str(c)
        except ValueError:
            return ""

    def on_diam_change(self, _=None):
        """Automatyczne wyliczanie chwytu podczas pisania (tylko gdy użytkownik nie odblokował chwytu)."""
        if self._is_loading_data:
            return

        if not self.shank_override.get():
            max_diam = self.get_max_diam()
            new_shank = self.calculate_shank_value(max_diam)

            self.shank_entry.configure(state="normal")
            self.shank_entry.delete(0, "end")
            self.shank_entry.insert(0, new_shank)
            self.shank_entry.configure(state="disabled")
            
        self.update_callback()

    def toggle_shank(self):
        if self._is_loading_data:
            return

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
        if not self._is_loading_data:
            self.update_callback()

    # ================= LOGIKA DANYCH I WALIDACJA =================
    def set_item_data(self, item_data):
        """Precyzyjne i bezpieczne wczytywanie pozycji do edycji z koszyka."""
        if not item_data:
            return

        self._is_loading_data = True

        try:
            # 1. Ustawienie typu narzędzia
            raw_type = item_data.get("type", "Wiertło N")
            if raw_type in self.type_combo.cget("values"):
                self.type_combo.set(raw_type)

            # 2. Parsowanie średnic roboczych ZANIM wyrenderujemy widok
            diam_str = str(item_data.get("diam", "10.0")).strip()

            if self.is_step_drill() and "x" in diam_str:
                parts = [p.strip() for p in diam_str.split("x") if p.strip()]
                num_parts = len(parts)

                # Najpierw ustawiamy odpowiednią krotność w comboboxie stopni!
                if str(num_parts) in self.steps_combo.cget("values"):
                    self.steps_combo.set(str(num_parts))

                # Pokażemy kontener i utworzymy PUSTE pola w odpowiedniej liczbie (num_parts)
                self.steps_combo.pack(side="left", padx=(10, 0))
                self.diam_entry.pack_forget()
                self.step_diams_frame.pack(after=self.diam_label, pady=(0, AppStyle.PAD_SMALL), padx=AppStyle.PAD_LARGE, anchor="w", fill="x")
                self._render_step_entries()

                # Wpisujemy czyste wartości d1, d2, d3 z koszyka
                for idx, p in enumerate(parts):
                    if idx < len(self.step_entries):
                        self.step_entries[idx].delete(0, "end")
                        self.step_entries[idx].insert(0, p)
            else:
                self.steps_combo.pack_forget()
                self.step_diams_frame.pack_forget()
                self.diam_entry.pack(after=self.diam_label, pady=(0, AppStyle.PAD_SMALL), padx=AppStyle.PAD_LARGE, anchor="w")
                self.diam_entry.delete(0, "end")
                self.diam_entry.insert(0, diam_str)

            # 3. Wypełnienie pozostałych pól
            if "z" in item_data:
                self.blades_entry.delete(0, "end")
                self.blades_entry.insert(0, str(item_data["z"]))

            if "qty" in item_data:
                self.qty_entry.delete(0, "end")
                self.qty_entry.insert(0, str(item_data["qty"]))

            if "coat_name" in item_data and item_data["coat_name"] in self.coat_combo.cget("values"):
                self.coat_combo.set(item_data["coat_name"])
                self.on_coating_change()
                if "coat_len" in item_data and item_data["coat_len"] in self.len_combo.cget("values"):
                    self.len_combo.set(item_data["coat_len"])

            if "services_status" in item_data:
                for k, val in item_data["services_status"].items():
                    if k in self.service_vars:
                        self.service_vars[k].set(val)

            if "opuszczenie_mult" in item_data:
                self.opuszczenie_mult = item_data["opuszczenie_mult"]
                mm_text = f"{self.opuszczenie_mult * 10} mm"
                self.lbl_mult_val.configure(text=f"{mm_text} (x{self.opuszczenie_mult})")

            self._on_service_toggle()

            # 4. PRECYZYJNA LOGIKA CHWYTU
            is_overridden = item_data.get("shank_override", False)
            self.shank_override.set(is_overridden)

            saved_shank = item_data.get("shank_diam")
            if saved_shank is not None and str(saved_shank).strip() != "":
                final_shank = str(saved_shank).strip()
            else:
                max_d = self.get_max_diam()
                final_shank = self.calculate_shank_value(max_d)

            self.shank_entry.configure(state="normal")
            self.shank_entry.delete(0, "end")
            self.shank_entry.insert(0, final_shank)

            if is_overridden:
                self.shank_entry.configure(
                    state="normal", fg_color=AppStyle.COLOR_BG_LIGHT,
                    border_color=AppStyle.COLOR_SECONDARY, border_width=2
                )
            else:
                self.shank_entry.configure(
                    state="disabled", fg_color=AppStyle.COLOR_MAIN_BG,
                    border_color=AppStyle.COLOR_MUTED, border_width=1
                )

        finally:
            self._is_loading_data = False
            self.update_callback()

    def validate_all(self, z, qty, shank):
        try:
            float(shank)
            if not z.isdigit() or not qty.isdigit():
                raise ValueError()

            if self.is_step_drill():
                for e in self.step_entries:
                    float(e.get().replace(',', '.').strip())
            else:
                float(self.diam_entry.get().replace(',', '.').strip())

            return True
        except ValueError:
            from ui.components import OstrzomatPopup
            OstrzomatPopup(self.master, title="Błąd", message="Wprowadzono nieprawidłowe wartości (litery/znaki specjalne). Popraw je przed kalkulacją!", type="error")
            return False
    
    def get_full_item_data(self, run_validation=False):
        """Zapisuje bieżący stan formularza do słownika pozycji koszyka."""
        try:
            shank = self.shank_entry.get().replace(',', '.').strip()
            qty = self.qty_entry.get() or "1" 
            t_type = self.type_combo.get()
            blades = self.blades_entry.get()
            coat = self.coat_combo.get()
            coat_len = self.len_combo.get() if hasattr(self, 'len_combo') else "100"

            if run_validation:
                if not self.validate_all(blades, qty, shank):
                    return None

            if self.is_step_drill():
                parsed_vals = []
                for e in self.step_entries:
                    raw = e.get().replace(',', '.').strip() or "0.0"
                    parsed_vals.append(raw)
                diam_display = "x".join(parsed_vals)
                calc_diam = self.get_max_diam()
            else:
                diam_display = self.diam_entry.get().replace(',', '.').strip()
                calc_diam = diam_display

            heavy_wear_active = self.service_vars["zuzycie"].get()
            t_j, t_r = cart_logic.calculate_tool_price(t_type, blades, calc_diam, qty, heavy_wear=heavy_wear_active)
            c_j, c_r = cart_logic.calculate_coating_price(coat, calc_diam, coat_len, qty)
            
            e_j_total, e_r_total, active_labels = cart_logic.calculate_extra_services(
                self.service_vars, calc_diam, qty, opuszczenie_multiplier=self.opuszczenie_mult
            )

            for key in self.service_vars:
                if key == "zuzycie":
                    self.service_price_labels[key].configure(text="+5% do ostrz." if self.service_vars[key].get() else "")
                    continue

                if self.service_vars[key].get():
                    db_name = "Cięcie" if key == "ciecie" else "Zaniżenie średnicy" if key == "opuszczenie" else "Polerowanie rowka"
                    price = database.get_service_price_refined(db_name, float(calc_diam))
                    if key == "opuszczenie":
                        price = price * self.opuszczenie_mult
                    self.service_price_labels[key].configure(text=f"+{price:.2f} zł")
                else:
                    self.service_price_labels[key].configure(text="")

            database.save_user_settings({
                "last_drill_type": t_type, "last_drill_blades": blades,
                "last_drill_diam": calc_diam, "last_drill_shank": shank
            })

            return {
                "type": t_type, 
                "diam": diam_display, 
                "shank_diam": shank,
                "shank_override": self.shank_override.get(),
                "z": blades, 
                "qty": qty,
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
            
        if not self._is_loading_data:
            self.update_callback()
    
    def _change_multiplier(self, delta):
        new_val = self.opuszczenie_mult + delta
        if new_val >= 1:
            self.opuszczenie_mult = new_val
            mm_text = f"{new_val * 10} mm"
            self.lbl_mult_val.configure(text=f"{mm_text} (x{new_val})")
            self.update_callback()