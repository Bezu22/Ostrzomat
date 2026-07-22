import customtkinter as ctk
import database

# Importy modułów kalkulacyjnych
from ui.calc_modules.frez_module import FrezModule
from ui.calc_modules.drill_module import DrillModule

from ui.components import OstrzomatPopup
from ui.style import AppStyle


class ToolCalcWindow(ctk.CTkToplevel):
    """
    Uniwersalne okno pop-up kalkulatora narzędzi.
    Pełni rolę kontenera (UI) dla modułów narzędziowych (Frezy, Wiertła).
    """

    def __init__(
        self,
        parent,
        tool_category="Frezy",
        edit_mode=False,
        item_data=None,
        item_index=None,
    ):
        super().__init__(parent)
        self.parent = parent
        self.tool_category = tool_category

        self.edit_mode = edit_mode
        self.item_data = item_data
        self.item_index = item_index

        if self.edit_mode and self.item_index is not None:
            self.title(f"Edycja pozycji L.p. {self.item_index + 1}: {tool_category}")
        else:
            self.title(f"Konfiguracja: {tool_category}")

        # Zmiana rozmiaru zgodnie z prośbą, dla lepszego rozłożenia kolumn
        width, height = 1200, 800
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        # Zabezpieczenie, by okno nie wyjechało poza górną krawędź ekranu
        self.geometry(f"{width}x{height}+{x}+10") 

        self.attributes("-topmost", True)
        self.grab_set()

        self.settings = database.get_user_settings()

        self.main_scroll = ctk.CTkScrollableFrame(self)
        self.main_scroll.pack(fill="both", expand=True, padx=15, pady=15)

        # Wybór modułu
        self.tool_module = None
        if tool_category == "Frezy":
            self.tool_module = FrezModule(
                self.main_scroll, self.update_calculation, self.settings
            )
        elif tool_category == "Wiertla":
            self.tool_module = DrillModule(
                self.main_scroll, self.update_calculation, self.settings
            )
            
        if self.tool_module:
            # fill="both", expand=True pozwala na ładne rozszerzenie 2 kolumn modułu na całe okno
            self.tool_module.pack(fill="both", expand=True, padx=10, pady=10)

            # --- KLUCZOWA ZMIANA UKŁADU ---
            # Zamiast pakować podgląd i przyciski na sam dół pod modułem,
            # sprawdzamy, czy moduł ma prawą kolumnę i pakujemy je bezpośrednio do niej!
            target_parent = getattr(self.tool_module, "right_col", self.main_scroll)

            self.setup_price_preview(target_parent)
            self.setup_action_buttons(target_parent)

            if self.edit_mode and self.item_data:
                self.load_item_data_into_form()

                saved_mult = self.item_data.get("opuszczenie_mult", 1)
                if hasattr(self.tool_module, "opuszczenie_mult"):
                    setattr(self.tool_module, "opuszczenie_mult", saved_mult)

                lbl_mult = getattr(self.tool_module, "lbl_mult_val", None)
                if saved_mult > 1 and lbl_mult and hasattr(lbl_mult, "configure"):
                    lbl_mult.configure(text=f"{saved_mult * 10} mm (x{saved_mult})")

                on_service_toggle = getattr(self.tool_module, "_on_service_toggle", None)
                if callable(on_service_toggle):
                    on_service_toggle()

            self.update_calculation()
        else:
            ctk.CTkLabel(
                self.main_scroll,
                text=f"Błąd: Nie znaleziono modułu dla kategorii '{tool_category}'",
                font=AppStyle.get_bold_font(),
            ).pack(pady=20)

    def setup_price_preview(self, parent_frame):
        """Tworzy dolny panel z podglądem przeliczonych cen i pakuje do wskazanej ramki."""
        self.preview_frame = ctk.CTkFrame(
            parent_frame, fg_color=AppStyle.COLOR_HEADER_BG
        )
        # Margines górny (pady=(20, 10)) odsuwa podgląd cen od usług dodatkowych
        self.preview_frame.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            self.preview_frame,
            text="CENA - PODGLĄD",
            font=AppStyle.get_bold_font(),
            text_color=AppStyle.COLOR_TEXT_LIGHT,
        ).pack(pady=5)

        self.price_labels = {}
        fields = [
            ("Ostrzenie:", "tool_price"),
            ("Powlekanie:", "coat_price"),
            ("Usługi dodatkowe:", "extra_price"),
            ("SUMA:", "total_price"),
        ]

        for label_text, key in fields:
            f = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
            f.pack(fill="x", padx=20, pady=2)

            ctk.CTkLabel(
                f,
                text=label_text,
                font=AppStyle.get_normal_font(),
                text_color=AppStyle.COLOR_TEXT_LIGHT,
            ).pack(side="left")

            self.price_labels[key] = ctk.CTkLabel(
                f,
                text="0.00 zł",
                font=AppStyle.get_bold_font(),
                text_color=AppStyle.COLOR_TEXT_LIGHT,
            )
            self.price_labels[key].pack(side="right")

    def setup_action_buttons(self, parent_frame):
        """Tworzy przyciski akcji i pakuje do wskazanej ramki."""
        btn_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        # Pojawią się na samym dole prawej kolumny
        btn_frame.pack(fill="x", side="bottom", padx=20, pady=(15, 30))

        btn_text = "ZAPISZ ZMIANY" if self.edit_mode else "DODAJ DO KOSZYKA"
        btn_color = (
            AppStyle.COLOR_SECONDARY
            if self.edit_mode
            else AppStyle.COLOR_SUCCESS
        )
        btn_cmd = self.save_changes if self.edit_mode else self.add_to_cart

        self.add_btn = ctk.CTkButton(
            btn_frame,
            text=btn_text,
            height=45,
            font=AppStyle.get_bold_font(),
            fg_color=btn_color,
            command=btn_cmd,
        )
        self.add_btn.pack(fill="x", pady=5)

        self.close_btn = ctk.CTkButton(
            btn_frame,
            text="ZAMKNIJ",
            height=35,
            font=AppStyle.get_normal_font(),
            fg_color=AppStyle.COLOR_MUTED,
            hover_color=AppStyle.COLOR_MUTED_HOVER,
            command=self.destroy,
        )
        self.close_btn.pack(fill="x", pady=5)

    def load_item_data_into_form(self):
        """Uzupełnia formularz danymi podczas edycji."""
        try:
            m = self.tool_module
            d = self.item_data
            if not m or not d:
                return

            type_combo = getattr(m, "type_combo", None)
            if type_combo and hasattr(type_combo, "set"):
                type_combo.set(d.get("type", ""))

            blades_entry = getattr(m, "blades_entry", None)
            if blades_entry and hasattr(blades_entry, "delete"):
                blades_entry.delete(0, "end")
                blades_entry.insert(0, str(d.get("z", "")))

            diam_entry = getattr(m, "diam_entry", None)
            if diam_entry and hasattr(diam_entry, "delete"):
                diam_entry.delete(0, "end")
                diam_entry.insert(0, str(d.get("diam", "")))

            qty_entry = getattr(m, "qty_entry", None)
            if qty_entry and hasattr(qty_entry, "delete"):
                qty_entry.delete(0, "end")
                qty_entry.insert(0, str(d.get("qty", "")))

            coat_combo = getattr(m, "coat_combo", None)
            if coat_combo and hasattr(coat_combo, "set"):
                coat_combo.set(d.get("coat_name", "Brak"))

                on_coat = getattr(m, "_on_coating_change", getattr(m, "on_coating_change", None))
                if callable(on_coat):
                    on_coat()

                if d.get("coat_name") != "Brak":
                    len_combo = getattr(m, "len_combo", None)
                    if len_combo and hasattr(len_combo, "set"):
                        len_combo.set(d.get("coat_len", "100"))

            shank_entry = getattr(m, "shank_entry", None)
            if shank_entry and hasattr(shank_entry, "delete"):
                shank_entry.configure(state="normal")
                shank_entry.delete(0, "end")
                shank_entry.insert(0, str(d.get("shank_diam", d.get("diam", ""))))

                shank_override = getattr(m, "shank_override", None)
                if (
                    shank_override
                    and hasattr(shank_override, "set")
                    and d.get("shank_diam")
                    and d.get("shank_diam") != d.get("diam")
                ):
                    shank_override.set(True)

                toggle_shank = getattr(m, "_toggle_shank", getattr(m, "toggle_shank", None))
                if callable(toggle_shank):
                    toggle_shank()

            service_vars = getattr(m, "service_vars", {})
            status = d.get("services_status", {})
            if isinstance(service_vars, dict):
                for key, var in service_vars.items():
                    if key in status and hasattr(var, "set"):
                        var.set(status[key])

        except Exception as e:
            print(f"Błąd ładowania danych do formularza edycji: {e}")

    def update_calculation(self, _=None):
        """Aktualizuje podgląd cen."""
        if not self.tool_module:
            return

        get_data_func = getattr(self.tool_module, "get_full_item_data", None)
        data = None
        if callable(get_data_func):
            data = get_data_func(run_validation=False)

        # Usunięcie ostrzeżeń z VS Code: upewniamy się, że data to w 100% słownik
        if isinstance(data, dict):
            try:
                t_j = float(data.get("tool_unit", 0.0))
                t_r = float(data.get("total_tool", 0.0))

                c_j = float(data.get("coat_unit", 0.0))
                c_r = float(data.get("total_coat", 0.0))

                e_j = float(data.get("extra_unit", 0.0))
                e_r = float(data.get("total_extra", 0.0))

                self.price_labels["tool_price"].configure(
                    text=f"{t_j:.2f} / {t_r:.2f} zł"
                )

                if c_r > 0:
                    self.price_labels["coat_price"].configure(
                        text=f"{c_j:.2f} / {c_r:.2f} zł",
                        text_color=AppStyle.COLOR_TEXT_LIGHT,
                    )
                else:
                    self.price_labels["coat_price"].configure(
                        text="---", text_color=AppStyle.COLOR_TEXT_MUTED
                    )

                if e_r > 0:
                    self.price_labels["extra_price"].configure(
                        text=f"{e_j:.2f} / {e_r:.2f} zł",
                        text_color=AppStyle.COLOR_TEXT_LIGHT,
                    )
                else:
                    self.price_labels["extra_price"].configure(
                        text="---", text_color=AppStyle.COLOR_TEXT_MUTED
                    )

                total_final = t_r + c_r + e_r
                self.price_labels["total_price"].configure(
                    text=f"{total_final:.2f} zł",
                    text_color=AppStyle.COLOR_SUCCESS,
                )

            except Exception as ex:
                print(f"Błąd odświeżania podglądu cen: {ex}")
                self.price_labels["total_price"].configure(
                    text="Błąd danych", text_color=AppStyle.COLOR_DANGER
                )
        else:
            for lbl in self.price_labels.values():
                lbl.configure(text="---", text_color=AppStyle.COLOR_TEXT_MUTED)

    def add_to_cart(self):
        """Dodaje pozycję do koszyka BEZ zamykania okna."""
        get_data_func = getattr(self.tool_module, "get_full_item_data", None)
        if not callable(get_data_func):
            return

        item_data = get_data_func(run_validation=True)
        
        # Usunięcie ostrzeżeń z VS Code w tym miejscu
        if not isinstance(item_data, dict):
            return
            
        item_data["tool_category"] = self.tool_category

        shank_entry = getattr(self.tool_module, "shank_entry", None)
        if shank_entry and hasattr(shank_entry, "get"):
            item_data["shank_diam"] = shank_entry.get()

        item_data["notes"] = ""

        for key in [
            "tool_unit",
            "total_tool",
            "coat_unit",
            "total_coat",
            "extra_unit",
            "total_extra",
        ]:
            if key in item_data:
                item_data[key] = round(float(item_data[key]), 2)

        self.parent.add_item_to_cart(item_data)

        tool_type = item_data.get("type", self.tool_category)
        tool_diam = item_data.get("diam", "")

        OstrzomatPopup(
            self,
            title="Sukces",
            message=f"Narzędzie {tool_type} Ø{tool_diam} zostało dodane do koszyka!",
            type="info",
        )

    def save_changes(self):
        """Zapisuje zmiany w trybie edycji i zamyka okno."""
        get_data_func = getattr(self.tool_module, "get_full_item_data", None)
        if not callable(get_data_func):
            return

        item_data = get_data_func(run_validation=True)
        
        # Usunięcie ostrzeżeń z VS Code w tym miejscu
        if not isinstance(item_data, dict) or self.item_index is None:
            return
            
        item_data["tool_category"] = self.tool_category

        shank_entry = getattr(self.tool_module, "shank_entry", None)
        if shank_entry and hasattr(shank_entry, "get"):
            item_data["shank_diam"] = shank_entry.get()

        if (
            hasattr(self.parent, "cart_items")
            and len(self.parent.cart_items) > self.item_index
        ):
            old_item = self.parent.cart_items[self.item_index]
            item_data["notes"] = old_item.get("notes", "")

        for key in [
            "tool_unit",
            "total_tool",
            "coat_unit",
            "total_coat",
            "extra_unit",
            "total_extra",
        ]:
            if key in item_data:
                item_data[key] = round(float(item_data[key]), 2)

        self.parent.update_item_in_cart(self.item_index, item_data)
        self.destroy()