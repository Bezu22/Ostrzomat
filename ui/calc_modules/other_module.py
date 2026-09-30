import customtkinter as ctk
import database
from logic import cart_logic
from ui.calc_modules.base_module import BaseToolModule
from ui.style import AppStyle


class OtherModule(BaseToolModule):
    """
    Moduł kalkulatora dla kategorii 'Inne' (Fazowniki, Frezy z promieniem wewnętrznym itp.).

    Dziedziczy z BaseToolModule obsługę chwytu, powłok oraz usług dodatkowych.
    Specyfika kategorii Inne:
    - Wybór typu narzędzia z bazy danych (kategoria 'Inne')
    - Stałe pole identyfikacji / oznaczenia (maks. 6 znaków, np. K90, R1.0, ALU)
    - Konfiguracja liczby ostrzy (Z) i średnicy roboczej
    """

    def __init__(self, parent, update_callback, settings):
        super().__init__(parent, update_callback, settings)

        # ================= KOLUMNA LEWA: PARAMETRY NARZĘDZIA =================
        # 1. Typ narzędzia oraz oznaczenie (tag)
        self.add_label(self.left_col, "Typ narzędzia / Oznaczenie (max 6 znaków):", AppStyle.get_bold_font())
        type_row = ctk.CTkFrame(self.left_col, fg_color="transparent")
        type_row.pack(fill="x", pady=self.py_small, padx=self.px)

        other_types = database.get_unique_tool_types("Inne")
        default_type = other_types[0] if other_types else "Fazownik"
        self.type_combo = ctk.CTkComboBox(
            type_row,
            width=215,
            values=other_types if other_types else ["Fazownik"],
            command=self._on_type_change,
            **AppStyle.get_combo_style(),
        )
        self.type_combo.set(settings.get("last_other_type", default_type))
        self.type_combo.configure(state="readonly")
        self.type_combo.pack(side="left")

        self.setup_tag_control(type_row, width=75)

        # 2. Liczba ostrzy (Z)
        self.add_label(self.left_col, "Liczba ostrzy (Z):", AppStyle.get_bold_font())
        self.blades_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.blades_entry.insert(0, settings.get("last_other_blades", "4"))
        self.blades_entry.pack(pady=self.py_small, padx=self.px, anchor="w")
        self.blades_entry.bind("<KeyRelease>", lambda e: self.update_callback())

        # 3. Średnica robocza
        self.add_label(self.left_col, "Średnica robocza:", AppStyle.get_bold_font())
        self.diam_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.diam_entry.insert(0, settings.get("last_other_diam", "10.0"))
        self.diam_entry.pack(pady=self.py_small, padx=self.px, anchor="w")
        self.diam_entry.bind("<KeyRelease>", self.on_diam_change)

        # 4. Średnica chwytu (wspólna kontrolka z klasy bazowej)
        self.setup_shank_controls(self.left_col, default_shank=settings.get("last_other_shank", "10.0"))

        # 5. Powłoka i długość (wspólne kontrolki)
        self.setup_coating_controls(self.left_col)

        # 6. Ilość sztuk
        self.setup_qty_controls(self.left_col, default_qty="1")

        # ================= KOLUMNA PRAWA: USŁUGI DODATKOWE =================
        self.setup_services_controls(self.right_col)

        # Inicjalizacja widoku
        self._on_type_change()
        self.on_coating_change()
        self.toggle_shank()

    def _on_type_change(self, _=None):
        """Obsługa zmiany wybranego typu narzędzia."""
        self.update_callback()

    def set_item_data(self, item_data):
        """Ładuje dane edytowanej pozycji z koszyka do formularza."""
        if not item_data:
            return

        other_types = self.type_combo.cget("values")
        clean_type, tag = self.parse_type_and_tag(
            item_data.get("type", other_types[0] if other_types else "Fazownik"),
            known_types=other_types,
            explicit_tag=item_data.get("tag"),
        )

        if clean_type in other_types:
            self.type_combo.set(clean_type)
        else:
            self.type_combo.set(item_data.get("type", clean_type))

        if hasattr(self, "tag_var"):
            self.tag_var.set(tag)

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
                "last_other_type": t_type,
                "last_other_blades": blades,
                "last_other_diam": diam,
                "last_other_shank": shank,
            })

            tag = self.tag_var.get().strip() if hasattr(self, "tag_var") else ""
            display_type = self.format_tool_type_with_tag(t_type)

            return {
                "type": display_type,
                "tag": tag,
                "tool_category": "Inne",
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
            print(f"Błąd w module OtherModule: {e}")
            return None
