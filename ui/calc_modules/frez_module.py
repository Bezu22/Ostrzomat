import re
import customtkinter as ctk
import database
from logic import cart_logic
from ui.calc_modules.base_module import BaseToolModule
from ui.style import AppStyle


class FrezModule(BaseToolModule):
    """
    Moduł kalkulatora dla frezów (walcowe, czołowe, promieniowe, kuliste itp.).
    
    Dziedziczy z BaseToolModule obsługę chwytu, powłok oraz usług dodatkowych.
    Specyfika frezów:
    - Wybór profilu/typu frezu z bazy danych
    - Opcjonalne pole promienia R (wyświetlane dynamicznie dla frezów promieniowych)
    - Konfiguracja liczby ostrzy (Z)
    """

    def __init__(self, parent, update_callback, settings):
        super().__init__(parent, update_callback, settings)

        # ================= KOLUMNA LEWA: PARAMETRY FREZU =================
        # 1. Typ narzędzia
        self.add_label(self.left_col, "Typ narzędzia:", AppStyle.get_bold_font())
        frez_types = database.get_unique_tool_types("Frezy")
        self.type_combo = ctk.CTkComboBox(
            self.left_col,
            width=300,
            values=frez_types if frez_types else ["Frez walcowo-czołowy"],
            command=self._on_type_change,
            **AppStyle.get_combo_style(),
        )
        self.type_combo.set(settings.get("last_tool_type", frez_types[0] if frez_types else "Frez walcowo-czołowy"))
        self.type_combo.configure(state="readonly")
        self.type_combo.pack(pady=self.py_small, padx=self.px, anchor="w")

        # 2. Dynamiczne pole promienia (dla frezów promieniowych)
        self.radius_frame = ctk.CTkFrame(self.left_col, fg_color="transparent")
        lbl_r = ctk.CTkLabel(
            self.radius_frame,
            text="Promień (R):",
            font=AppStyle.get_bold_font(),
            text_color=AppStyle.COLOR_TEXT_DARK,
        )
        lbl_r.pack(anchor="w")

        self.radius_entry = ctk.CTkEntry(self.radius_frame, width=300, **AppStyle.get_entry_style())
        self.radius_entry.insert(0, "0.5")
        self.radius_entry.pack(pady=self.py_small, anchor="w")
        self.radius_entry.bind("<KeyRelease>", lambda e: self.update_callback())

        # 3. Liczba ostrzy
        self.add_label(self.left_col, "Liczba ostrzy:", AppStyle.get_bold_font())
        self.blades_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.blades_entry.insert(0, settings.get("last_blades", "4"))
        self.blades_entry.pack(pady=self.py_small, padx=self.px, anchor="w")
        self.blades_entry.bind("<KeyRelease>", lambda e: self.update_callback())

        # 4. Średnica robocza
        self.add_label(self.left_col, "Średnica robocza:", AppStyle.get_bold_font())
        self.diam_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.diam_entry.insert(0, settings.get("last_diam", "10.0"))
        self.diam_entry.pack(pady=self.py_small, padx=self.px, anchor="w")
        self.diam_entry.bind("<KeyRelease>", self.on_diam_change)

        # 5. Średnica chwytu (wspólna kontrolka z klasy bazowej)
        self.setup_shank_controls(self.left_col, default_shank=settings.get("last_shank", "10.0"))

        # 6. Powłoka i długość (wspólne kontrolki)
        self.setup_coating_controls(self.left_col)

        # 7. Ilość sztuk
        self.setup_qty_controls(self.left_col, default_qty="1")

        # ================= KOLUMNA PRAWA: USŁUGI DODATKOWE =================
        self.setup_services_controls(self.right_col)

        # Inicjalizacja widoku
        self._on_type_change()
        self.on_coating_change()
        self.toggle_shank()

    def _on_type_change(self, _=None):
        """Pokazuje pole promienia R, jeśli wybrany frez jest promieniowy."""
        selected_type = self.type_combo.get()
        if "promieniowy" in selected_type.lower():
            self.radius_frame.pack(after=self.type_combo, pady=self.py_small, padx=self.px, anchor="w", fill="x")
        else:
            self.radius_frame.pack_forget()

        self.update_callback()

    def set_item_data(self, item_data):
        """Ładuje dane edytowanej pozycji frezu z koszyka do formularza."""
        if not item_data:
            return

        raw_type = item_data.get("type", "Frez walcowo-czołowy")
        radius_val = "0.5"

        # Odczyt promienia R z nazwy typu (np. 'Frez promieniowy R0.5')
        match = re.search(r"^(.*?)\s+R([\d\.,]+)$", raw_type, re.IGNORECASE)
        if match:
            clean_type = match.group(1).strip()
            radius_val = match.group(2).replace(",", ".").strip()
        else:
            clean_type = raw_type

        if clean_type in self.type_combo.cget("values"):
            self.type_combo.set(clean_type)
        else:
            self.type_combo.set(raw_type)

        self._on_type_change()
        self.radius_entry.delete(0, "end")
        self.radius_entry.insert(0, radius_val)

        if "diam" in item_data:
            self.diam_entry.delete(0, "end")
            self.diam_entry.insert(0, str(item_data["diam"]))

        if "z" in item_data:
            self.blades_entry.delete(0, "end")
            self.blades_entry.insert(0, str(item_data["z"]))

        # Załadowanie wspólnych pól (ilość, chwyt, powłoka, usługi)
        self.load_base_item_data(item_data)

    def validate_all(self, diam, z, qty, shank):
        """Weryfikuje poprawność wprowadzonych wartości liczbowych."""
        try:
            float(diam)
            float(shank)
            if not z.isdigit() or not qty.isdigit():
                raise ValueError()

            if "promieniowy" in self.type_combo.get().lower():
                r_val = self.radius_entry.get().replace(",", ".").strip()
                float(r_val)

            return True
        except (ValueError, TypeError):
            from ui.components import OstrzomatPopup
            OstrzomatPopup(
                self.master,
                title="Błąd",
                message="Wprowadzono nieprawidłowe wartości. Popraw je przed kalkulacją!",
                type="error",
            )
            return False

    def get_full_item_data(self, run_validation=False):
        """Zbiera dane z formularza, oblicza koszty i zwraca słownik pozycji koszyka."""
        try:
            diam = self.diam_entry.get().replace(",", ".").strip()
            shank = self.shank_entry.get().replace(",", ".").strip()
            qty = self.qty_entry.get().strip() or "1"
            t_type = self.type_combo.get()
            blades = self.blades_entry.get()
            coat = self.coat_combo.get()
            coat_len = self.len_combo.get() if hasattr(self, "len_combo") else "100"

            if run_validation and not self.validate_all(diam, blades, qty, shank):
                return None

            calc_diam = diam
            services_qty_dict = self.get_services_qty_dict(fallback_qty=qty)
            heavy_wear_qty = services_qty_dict.get("zuzycie", 0)

            # Wycena narzędzia, powłoki i usług
            t_j, t_r = cart_logic.calculate_tool_price(t_type, blades, calc_diam, qty, heavy_wear_qty=heavy_wear_qty)
            c_j, c_r = cart_logic.calculate_coating_price(coat, calc_diam, coat_len, qty)
            e_j_total, e_r_total, active_labels = cart_logic.calculate_extra_services(
                self.service_vars, services_qty_dict, calc_diam, qty, opuszczenie_multiplier=self.opuszczenie_mult
            )

            # Aktualizacja podglądu cen przy checkboxach usług
            self.update_service_price_labels(calc_diam, services_qty_dict)

            # Zapisanie ostatnich ustawień do pamięci podręcznej
            database.save_user_settings({
                "last_tool_type": t_type,
                "last_blades": blades,
                "last_diam": diam,
                "last_shank": shank,
            })

            display_type = t_type
            if "promieniowy" in t_type.lower():
                r_text = self.radius_entry.get().replace(",", ".").strip() or "0.5"
                display_type = f"{t_type} R{r_text}"

            return {
                "type": display_type,
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
            print(f"Błąd w module FrezModule: {e}")
            return None