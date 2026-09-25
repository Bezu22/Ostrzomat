import customtkinter as ctk
import database
from logic import cart_logic
from ui.calc_modules.base_module import BaseToolModule
from ui.style import AppStyle


class SpecialModule(BaseToolModule):
    """
    Moduł kalkulatora dla narzędzi specjalnych.
    
    Dziedziczy z BaseToolModule obsługę chwytu, powłok oraz usług dodatkowych.
    Specyfika narzędzi specjalnych:
    - Dowolna wpisywana ręcznie nazwa narzędzia (pole tekstowe zamiast comboboxa)
    - Ręcznie wprowadzana cena jednostkowa ostrzenia (niepobierana ze standardowego cennika)
    """

    def __init__(self, parent, update_callback, settings):
        super().__init__(parent, update_callback, settings)

        # ================= KOLUMNA LEWA: PARAMETRY NARZĘDZIA =================
        # 1. Typ / nazwa narzędzia specjalnego
        self.add_label(self.left_col, "Typ narzędzia:", AppStyle.get_bold_font())
        self.type_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.type_entry.insert(0, settings.get("last_special_type", "Specjalne"))
        self.type_entry.pack(pady=self.py_small, padx=self.px, anchor="w")
        self.type_entry.bind("<KeyRelease>", lambda e: self.update_callback())

        # 2. Liczba ostrzy
        self.add_label(self.left_col, "Liczba ostrzy:", AppStyle.get_bold_font())
        self.blades_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.blades_entry.insert(0, settings.get("last_special_blades", "4"))
        self.blades_entry.pack(pady=self.py_small, padx=self.px, anchor="w")
        self.blades_entry.bind("<KeyRelease>", lambda e: self.update_callback())

        # 3. Średnica robocza
        self.add_label(self.left_col, "Średnica robocza:", AppStyle.get_bold_font())
        self.diam_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.diam_entry.insert(0, settings.get("last_special_diam", "10.0"))
        self.diam_entry.pack(pady=self.py_small, padx=self.px, anchor="w")
        self.diam_entry.bind("<KeyRelease>", self.on_diam_change)

        # 4. Średnica chwytu (wspólna kontrolka z klasy bazowej)
        self.setup_shank_controls(self.left_col, default_shank=settings.get("last_special_shank", "10.0"))

        # 5. Powłoka i długość
        self.setup_coating_controls(self.left_col)

        # 6. Ilość sztuk
        self.setup_qty_controls(self.left_col, default_qty=settings.get("last_special_qty", "1"))

        # 7. Ręczna cena za sztukę
        self.add_label(self.left_col, "Cena za sztukę [zł]:", AppStyle.get_bold_font())
        self.unit_price_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.unit_price_entry.insert(0, settings.get("last_special_unit_price", "0.00"))
        self.unit_price_entry.pack(pady=self.py_small, padx=self.px, anchor="w")
        self.unit_price_entry.bind("<KeyRelease>", lambda e: self.update_callback())

        # ================= KOLUMNA PRAWA: USŁUGI DODATKOWE =================
        self.setup_services_controls(self.right_col)

        # Inicjalizacja widoku
        self.on_coating_change()
        self.toggle_shank()
        self._on_service_toggle()

    def set_item_data(self, item_data):
        """Wypełnia formularz danymi edytowanej pozycji narzędzia specjalnego."""
        if not item_data:
            return

        self.type_entry.delete(0, "end")
        self.type_entry.insert(0, item_data.get("type", "Specjalne"))

        if "z" in item_data:
            self.blades_entry.delete(0, "end")
            self.blades_entry.insert(0, str(item_data["z"]))

        if "diam" in item_data:
            self.diam_entry.delete(0, "end")
            self.diam_entry.insert(0, str(item_data["diam"]))

        if "tool_unit" in item_data:
            self.unit_price_entry.delete(0, "end")
            self.unit_price_entry.insert(0, str(item_data["tool_unit"]))

        # Załadowanie wspólnych pól (ilość, chwyt, powłoka, usługi)
        self.load_base_item_data(item_data)

    def validate_all(self, diam, z, qty, shank, unit_price):
        """Waliduje poprawność wprowadzonych wartości liczbowych."""
        try:
            float(diam)
            float(shank)
            float(unit_price)
            if not z.isdigit() or not qty.isdigit():
                raise ValueError()
            return True
        except (ValueError, TypeError):
            from ui.components import OstrzomatPopup
            OstrzomatPopup(
                self.master,
                title="Błąd",
                message="Wprowadzono nieprawidłowe wartości liczbowe. Popraw je przed dodaniem do koszyka.",
                type="error",
            )
            return False

    def get_full_item_data(self, run_validation=False):
        """Zbiera dane, kalkuluje koszty powłok/usług i zwraca słownik pozycji koszyka."""
        try:
            t_type = self.type_entry.get().strip() or "Specjalne"
            blades = self.blades_entry.get().strip() or "4"
            diam = self.diam_entry.get().replace(",", ".").strip() or "10.0"
            shank = self.shank_entry.get().replace(",", ".").strip() or "10.0"
            qty = self.qty_entry.get().strip() or "1"
            unit_price_raw = self.unit_price_entry.get().replace(",", ".").strip() or "0.00"

            if run_validation and not self.validate_all(diam, blades, qty, shank, unit_price_raw):
                return None

            try:
                t_j = float(unit_price_raw)
                q_val = int(qty)
            except ValueError:
                t_j = 0.0
                q_val = 1

            services_qty_dict = self.get_services_qty_dict(fallback_qty=q_val)
            heavy_wear_qty = services_qty_dict.get("zuzycie", 0)

            # Ciężkie zużycie nalicza +5% do ceny ręcznej narzędzia specjalnego
            hw_qty = min(max(heavy_wear_qty, 0), q_val)
            normal_qty = q_val - hw_qty
            t_r = round((normal_qty * t_j) + (hw_qty * t_j * 1.05), 2)
            unit_avg = round(t_r / q_val, 2) if q_val > 0 else t_j

            coat = self.coat_combo.get()
            coat_len = self.len_combo.get() if hasattr(self, "len_combo") else "100"

            c_j, c_r = cart_logic.calculate_coating_price(coat, diam, coat_len, q_val)
            e_j_total, e_r_total, active_labels = cart_logic.calculate_extra_services(
                self.service_vars, services_qty_dict, diam, q_val, opuszczenie_multiplier=self.opuszczenie_mult
            )

            self.update_service_price_labels(diam, services_qty_dict)

            # Zapis ostatnich ustawień
            database.save_user_settings({
                "last_special_type": t_type,
                "last_special_blades": blades,
                "last_special_diam": diam,
                "last_special_shank": shank,
                "last_special_qty": qty,
                "last_special_unit_price": unit_price_raw,
            })

            return {
                "type": t_type,
                "tool_category": "Specjalne",
                "diam": diam,
                "shank_diam": shank,
                "shank_override": self.shank_override.get(),
                "z": blades,
                "qty": q_val,
                "tool_unit": unit_avg,
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
            print(f"Błąd w module SpecialModule: {e}")
            return None
