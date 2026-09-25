import customtkinter as ctk
import database
from logic import cart_logic
from ui.calc_modules.base_module import BaseToolModule
from ui.style import AppStyle


class DrillModule(BaseToolModule):
    """
    Moduł kalkulatora dla wierteł (standardowe, węglikowe, stopniowe itp.).

    Dziedziczy z BaseToolModule obsługę chwytu, powłok oraz usług dodatkowych.
    Specyfika wierteł:
    - Obsługa wierteł standardowych (jedna średnica robocza)
    - Obsługa wierteł stopniowych (wybór liczby stopni 2, 3, 4 oraz dynamiczne pola d1..d4)
    - Automatyczne wyznaczanie średnicy chwytu z największego stopnia
    """

    def __init__(self, parent, update_callback, settings):
        super().__init__(parent, update_callback, settings)
        self._is_loading_data = False

        # ================= KOLUMNA LEWA: PARAMETRY WIERTŁA =================
        # 1. Typ narzędzia oraz wybór stopni (dla stopniowych)
        self.add_label(self.left_col, "Typ narzędzia:", AppStyle.get_bold_font())
        type_frame = ctk.CTkFrame(self.left_col, fg_color="transparent")
        type_frame.pack(fill="x", pady=self.py_small, padx=self.px)

        drill_types = database.get_unique_tool_types("Wiertla")
        self.type_combo = ctk.CTkComboBox(
            type_frame,
            width=200,
            values=drill_types if drill_types else ["Wiertło N"],
            command=self._on_type_change,
            **AppStyle.get_combo_style(),
        )
        self.type_combo.set(settings.get("last_drill_type", drill_types[0] if drill_types else "Wiertło N"))
        self.type_combo.configure(state="readonly")
        self.type_combo.pack(side="left")

        # Wybór liczby stopni (2, 3, 4) dla wiertła stopniowego
        self.steps_combo = ctk.CTkComboBox(
            type_frame,
            width=80,
            values=["2", "3", "4"],
            command=self._on_steps_change,
            **AppStyle.get_combo_style(),
        )
        self.steps_combo.set("2")
        self.steps_combo.configure(state="readonly")

        # 2. Liczba ostrzy (Z)
        self.add_label(self.left_col, "Liczba ostrzy (Z):", AppStyle.get_bold_font())
        self.blades_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.blades_entry.insert(0, settings.get("last_drill_blades", "2"))
        self.blades_entry.pack(pady=self.py_small, padx=self.px, anchor="w")
        self.blades_entry.bind("<KeyRelease>", lambda e: self.update_callback())

        # 3. Średnica robocza (pojedyncza lub zestaw pól d1..d4)
        self.diam_label = ctk.CTkLabel(
            self.left_col,
            text="Średnica robocza:",
            font=AppStyle.get_bold_font(),
            text_color=AppStyle.COLOR_TEXT_DARK,
        )
        self.diam_label.pack(pady=(AppStyle.PAD_SMALL, 0), padx=self.px, anchor="w")

        # Pole dla wiertła standardowego
        self.diam_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.diam_entry.insert(0, settings.get("last_drill_diam", "10.0"))
        self.diam_entry.pack(pady=self.py_small, padx=self.px, anchor="w")
        self.diam_entry.bind("<KeyRelease>", self.on_diam_change)

        # Kontener na dynamiczne pola d1, d2, d3, d4 dla wiertła stopniowego
        self.step_diams_frame = ctk.CTkFrame(self.left_col, fg_color="transparent")
        self.step_entries = []

        # 4. Średnica chwytu (wspólna kontrolka z klasy bazowej)
        self.setup_shank_controls(self.left_col, default_shank=settings.get("last_drill_shank", "10.0"))

        # 5. Powłoka i długość
        self.setup_coating_controls(self.left_col)

        # 6. Ilość sztuk
        self.setup_qty_controls(self.left_col, default_qty="1")

        # ================= KOLUMNA PRAWA: USŁUGI DODATKOWE =================
        self.setup_services_controls(self.right_col)

        # Inicjalizacja widoku
        self._on_type_change()
        self.on_coating_change()
        self.toggle_shank()

    # ================= LOGIKA WIERTEŁ STOPNIOWYCH =================

    def is_step_drill(self):
        """Zwraca True, jeśli wybrany typ to wiertło stopniowe."""
        return "stopniowe" in self.type_combo.get().lower()

    def get_working_diameter_str(self):
        """Nadpisuje metodę bazową – dla wiertła stopniowego zwraca największy stopień."""
        if self.is_step_drill():
            return str(self.get_max_diam())
        return self.diam_entry.get()

    def get_max_diam(self):
        """Wyciąga największą wpisaną średnicę roboczą (dla wyceny i chwytu)."""
        if self.is_step_drill():
            max_d = 0.0
            for ent in self.step_entries:
                try:
                    val = float(ent.get().replace(",", "."))
                    if val > max_d:
                        max_d = val
                except ValueError:
                    pass
            return max_d if max_d > 0.0 else 10.0

        try:
            return float(self.diam_entry.get().replace(",", "."))
        except ValueError:
            return 10.0

    def _render_step_entries(self):
        """Tworzy dynamiczne pola wprowadzania średnic stopni d1, d2, d3, d4."""
        for w in self.step_diams_frame.winfo_children():
            w.destroy()
        self.step_entries.clear()

        num_steps = int(self.steps_combo.get())
        default_vals = ["3.0", "6.0", "8.0", "10.0"]

        for i in range(num_steps):
            f = ctk.CTkFrame(self.step_diams_frame, fg_color="transparent")
            f.pack(side="left", padx=(0, 6))

            lbl = ctk.CTkLabel(
                f,
                text=f"d{i+1}:",
                font=AppStyle.get_normal_font(),
                text_color=AppStyle.COLOR_TEXT_DARK,
            )
            lbl.pack(anchor="w")

            entry = ctk.CTkEntry(f, width=55, **AppStyle.get_entry_style())
            if not self._is_loading_data:
                entry.insert(0, default_vals[i] if i < len(default_vals) else "10.0")
            entry.pack()
            entry.bind("<KeyRelease>", self.on_diam_change)
            self.step_entries.append(entry)

    def _on_steps_change(self, _=None):
        """Reaguje na zmianę liczby stopni w comboboxie."""
        self._render_step_entries()
        self.on_diam_change()

    def _on_type_change(self, _=None):
        """Przełącza widok między pojedynczą średnicą a polami stopni d1..d4."""
        if self.is_step_drill():
            self.steps_combo.pack(side="left", padx=(10, 0))
            self.diam_entry.pack_forget()
            self.step_diams_frame.pack(
                after=self.diam_label,
                pady=(0, AppStyle.PAD_SMALL),
                padx=AppStyle.PAD_LARGE,
                anchor="w",
                fill="x",
            )
            self._render_step_entries()
        else:
            self.steps_combo.pack_forget()
            self.step_diams_frame.pack_forget()
            self.diam_entry.pack(
                after=self.diam_label,
                pady=(0, AppStyle.PAD_SMALL),
                padx=AppStyle.PAD_LARGE,
                anchor="w",
            )
            self.on_diam_change()

        if not self._is_loading_data:
            self.update_callback()

    def set_item_data(self, item_data):
        """Ładuje dane edytowanego wiertła z koszyka do formularza."""
        if not item_data:
            return

        self._is_loading_data = True
        try:
            t_type = item_data.get("type", "Wiertło N")
            if t_type in self.type_combo.cget("values"):
                self.type_combo.set(t_type)
            else:
                self.type_combo.set("Wiertło N")

            self._on_type_change()

            raw_diam = str(item_data.get("diam", "10.0"))
            if self.is_step_drill():
                parts = raw_diam.split("/")
                steps_count = str(len(parts))
                if steps_count in self.steps_combo.cget("values"):
                    self.steps_combo.set(steps_count)
                self._render_step_entries()

                for i, p_val in enumerate(parts):
                    if i < len(self.step_entries):
                        self.step_entries[i].delete(0, "end")
                        self.step_entries[i].insert(0, p_val.strip())
            else:
                self.diam_entry.delete(0, "end")
                self.diam_entry.insert(0, raw_diam)

            if "z" in item_data:
                self.blades_entry.delete(0, "end")
                self.blades_entry.insert(0, str(item_data["z"]))

            # Załadowanie wspólnych pól (ilość, chwyt, powłoka, usługi)
            self.load_base_item_data(item_data)
        finally:
            self._is_loading_data = False

    def validate_all(self, diam, z, qty, shank):
        """Waliduje poprawność wprowadzonych wartości liczbowych dla wiertła."""
        try:
            if self.is_step_drill():
                if not self.step_entries:
                    raise ValueError()
                for ent in self.step_entries:
                    val = ent.get().replace(",", ".").strip()
                    float(val)
            else:
                float(diam)

            float(shank)
            if not z.isdigit() or not qty.isdigit():
                raise ValueError()
            return True
        except (ValueError, TypeError):
            from ui.components import OstrzomatPopup
            OstrzomatPopup(
                self.master,
                title="Błąd",
                message="Wprowadzono nieprawidłowe wartości w polach wiertła. Popraw je przed kalkulacją!",
                type="error",
            )
            return False

    def get_full_item_data(self, run_validation=False):
        """Zbiera dane, oblicza koszty i zwraca słownik pozycji koszyka."""
        try:
            if self.is_step_drill():
                diams_list = [ent.get().replace(",", ".").strip() for ent in self.step_entries]
                diam = "/".join(diams_list) if diams_list else "10.0"
                calc_diam = self.get_max_diam()
            else:
                diam = self.diam_entry.get().replace(",", ".").strip()
                calc_diam = diam

            shank = self.shank_entry.get().replace(",", ".").strip()
            qty = self.qty_entry.get().strip() or "1"
            t_type = self.type_combo.get()
            blades = self.blades_entry.get()
            coat = self.coat_combo.get()
            coat_len = self.len_combo.get() if hasattr(self, "len_combo") else "100"

            if run_validation and not self.validate_all(diam, blades, qty, shank):
                return None

            services_qty_dict = self.get_services_qty_dict(fallback_qty=qty)
            heavy_wear_qty = services_qty_dict.get("zuzycie", 0)

            # Wycena narzędzia, powłoki i usług dodatkowych
            t_j, t_r = cart_logic.calculate_tool_price(t_type, blades, calc_diam, qty, heavy_wear_qty=heavy_wear_qty)
            c_j, c_r = cart_logic.calculate_coating_price(coat, calc_diam, coat_len, qty)
            e_j_total, e_r_total, active_labels = cart_logic.calculate_extra_services(
                self.service_vars, services_qty_dict, calc_diam, qty, opuszczenie_multiplier=self.opuszczenie_mult
            )

            # Aktualizacja podglądu cen przy usługach
            self.update_service_price_labels(calc_diam, services_qty_dict)

            # Zapis preferencji użytkownika
            database.save_user_settings({
                "last_drill_type": t_type,
                "last_drill_blades": blades,
                "last_drill_diam": diam if not self.is_step_drill() else "10.0",
                "last_drill_shank": shank,
            })

            return {
                "type": t_type,
                "diam": diam,
                "shank_diam": shank,
                "shank_override": self.shank_override.get(),
                "z": blades,
                "qty": qty,
                "tool_unit": t_j,
                "total_tool": t_r,
                "coat_name": coat,
                "coat_len": coat_len,
                "coat_unit": c_j,
                "total_coat": c_r,
                "services_status": {k: v.get() for k, v in self.service_vars.items()},
                "services_qty": services_qty_dict,
                "opuszczenie_mult": self.opuszczenie_mult,
                "extra_unit": e_j_total,
                "total_extra": e_r_total,
            }
        except Exception as e:
            print(f"Błąd w module DrillModule: {e}")
            return None