import math
import customtkinter as ctk
import database
from ui.style import AppStyle


class BaseToolModule(ctk.CTkFrame):
    """
    Klasa bazowa dla modułów kalkulatora narzędzi (Frezy, Wiertła, Narzędzia specjalne).

    Koncentruje w jednym miejscu powtarzający się kod:
    - Układ dwukolumnowy (lewa kolumna: parametry narzędzia, prawa: usługi dodatkowe)
    - Obsługę średnicy chwytu (automatyczne wyliczanie z roboczej + opcja ręcznego nadpisania)
    - Sekcję wyboru powłoki oraz dopasowania dostępnych długości z bazy
    - Sekcję usług dodatkowych (cięcie, zaniżenie średnicy z mnożnikiem, polerowanie, zużycie)
    - Dwukierunkową synchronizację ilości w usługach z główną ilością sztuk
    """

    def __init__(self, parent, update_callback, settings):
        super().__init__(parent, fg_color="transparent")
        self.update_callback = update_callback
        self.settings = settings

        # Flaga ręcznego wpisywania średnicy chwytu
        self.shank_override = ctk.BooleanVar(value=False)

        # Usługi dodatkowe
        self.opuszczenie_mult = 1
        self.service_vars = {
            "ciecie": ctk.BooleanVar(),
            "opuszczenie": ctk.BooleanVar(),
            "polerowanie": ctk.BooleanVar(),
            "zuzycie": ctk.BooleanVar(),
        }
        self.service_qty_entries = {}
        self.service_price_labels = {}

        self.px = AppStyle.PAD_LARGE
        self.py_small = (0, AppStyle.PAD_SMALL)

        # Kontener główny podzielony na dwie równe kolumny
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        self.main_container.grid_columnconfigure(0, weight=1, uniform="kolumna")
        self.main_container.grid_columnconfigure(1, weight=1, uniform="kolumna")
        self.main_container.grid_rowconfigure(0, weight=1)

        self.left_col = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.right_col = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

    # ================= POMOCNIKI KONTROLEK UI =================

    def add_label(self, parent_frame, text, font=None):
        """Dodaje sformatowaną etykietę nagłówkową do wskazanego panelu."""
        font = font or AppStyle.get_bold_font()
        lbl = ctk.CTkLabel(
            parent_frame,
            text=text,
            font=font,
            text_color=AppStyle.COLOR_TEXT_DARK,
        )
        lbl.pack(pady=(AppStyle.PAD_SMALL, 0), padx=self.px, anchor="w")
        return lbl

    def setup_tag_control(self, parent_row_frame, width=80):
        """
        Tworzy małe, stałe pole identyfikacji narzędzia (maks. 6 znaków, np. R0.5, ALU, K90).
        Wartość ta trafia do opisu narzędzia w koszyku i na wycenie.
        """
        self.tag_var = ctk.StringVar(value="")

        def _on_tag_change(*args):
            val = self.tag_var.get()
            if len(val) > 6:
                self.tag_var.set(val[:6])
                return
            self.update_callback()

        self.tag_var.trace_add("write", _on_tag_change)

        self.tag_entry = ctk.CTkEntry(
            parent_row_frame,
            width=width,
            textvariable=self.tag_var,
            placeholder_text="Oznacz.",
            **AppStyle.get_entry_style(),
        )
        self.tag_entry.pack(side="left", padx=(8, 0))
        return self.tag_entry

    def format_tool_type_with_tag(self, base_type):
        """Dołącza wpisaną krótką identyfikację (np. 'ALU', 'K90', 'R0.5') do nazwy typu."""
        tag = ""
        if hasattr(self, "tag_var"):
            tag = self.tag_var.get().strip()
        elif hasattr(self, "tag_entry"):
            tag = self.tag_entry.get().strip()
        if tag:
            return f"{base_type} {tag}"
        return base_type

    def parse_type_and_tag(self, raw_type, known_types=None, explicit_tag=None):
        """
        Rozdziela pełną nazwę narzędzia na czysty typ bazowy oraz krótki identyfikator (tag).
        Obsługuje zarówno nowe pozycje z polem 'tag', jak i starsze zapisy (np. 'Frez promieniowy R0.5').
        """
        if explicit_tag is not None and str(explicit_tag).strip():
            tag = str(explicit_tag).strip()
            clean_type = str(raw_type).strip()
            if clean_type.endswith(" " + tag):
                clean_type = clean_type[:-len(tag)-1].strip()
            return clean_type, tag[:6]

        raw_type = str(raw_type or "").strip()
        if known_types:
            for kt in sorted(known_types, key=len, reverse=True):
                if raw_type == kt:
                    return kt, ""
                if raw_type.startswith(kt + " "):
                    return kt, raw_type[len(kt)+1:].strip()[:6]

        # Fallback dla starszych zapisów promienia R
        import re
        match = re.search(r"^(.*?)\s+R([\d\.,]+)$", raw_type, re.IGNORECASE)
        if match:
            return match.group(1).strip(), f"R{match.group(2).replace(',', '.')}"[:6]

        return raw_type, ""

    def setup_shank_controls(self, parent_frame, default_shank="10.0"):
        """
        Buduje kontrolki średnicy chwytu: pole tekstowe oraz checkbox
        pozwalający odpiąć automatyczne wyliczanie i wpisać średnicę ręcznie.
        """
        self.add_label(parent_frame, "Średnica chwytu:", AppStyle.get_bold_font())
        s_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        s_frame.pack(fill="x", pady=self.py_small, padx=self.px)

        self.shank_entry = ctk.CTkEntry(s_frame, width=140, **AppStyle.get_entry_style())
        self.shank_entry.insert(0, str(default_shank))
        self.shank_entry.pack(side="left")

        self.shank_cb = ctk.CTkCheckBox(
            s_frame,
            text="",
            width=24,
            variable=self.shank_override,
            command=self.toggle_shank,
            fg_color=AppStyle.COLOR_PRIMARY,
            hover_color=AppStyle.COLOR_PRIMARY_HOVER,
        )
        self.shank_cb.pack(side="left", padx=AppStyle.PAD_MEDIUM)

    def setup_coating_controls(self, parent_frame):
        """Buduje listę wyboru powłoki oraz zależną listę dostępnych długości."""
        self.add_label(parent_frame, "Powłoka:", AppStyle.get_bold_font())
        self.coat_combo = ctk.CTkComboBox(
            parent_frame,
            width=300,
            values=["Brak"] + database.get_unique_coating_names(),
            command=self.on_coating_change,
            **AppStyle.get_combo_style(),
        )
        self.coat_combo.set("Brak")
        self.coat_combo.configure(state="readonly")
        self.coat_combo.pack(pady=self.py_small, padx=self.px, anchor="w")

        self.len_label = ctk.CTkLabel(
            parent_frame,
            text="Długość (L):",
            font=AppStyle.get_bold_font(),
            text_color=AppStyle.COLOR_TEXT_DARK,
        )
        self.len_label.pack(pady=(AppStyle.PAD_SMALL, 0), padx=self.px, anchor="w")

        self.len_combo = ctk.CTkComboBox(
            parent_frame,
            width=300,
            values=[],
            command=self.update_callback,
            **AppStyle.get_combo_style(),
        )
        self.len_combo.configure(state="readonly")
        self.len_combo.pack(pady=(0, AppStyle.PAD_MEDIUM), padx=self.px, anchor="w")

    def setup_qty_controls(self, parent_frame, default_qty="1"):
        """Buduje główne pole wprowadzania ilości sztuk."""
        self.add_label(parent_frame, "Ilość sztuk:", AppStyle.get_bold_font())
        self.qty_entry = ctk.CTkEntry(parent_frame, width=300, **AppStyle.get_entry_style())
        self.qty_entry.insert(0, str(default_qty))
        self.qty_entry.pack(pady=(0, AppStyle.PAD_MEDIUM), padx=self.px, anchor="w")
        self.qty_entry.bind("<KeyRelease>", self._on_main_qty_change)

    def setup_services_controls(self, parent_frame):
        """Buduje pełną sekcję usług dodatkowych z polami ilości oraz kontrolkami mnożnika."""
        self.add_label(parent_frame, "Usługi dodatkowe:", AppStyle.get_bold_font())

        services_info = [
            ("ciecie", "Cięcie narzędzia (skracanie)"),
            ("opuszczenie", "Zaniżenie średnicy (szyjka)"),
            ("polerowanie", "Polerowanie rowka wiórowego"),
            ("zuzycie", "Ciężkie zużycie / wyszczerbienia (+5%)"),
        ]

        for key, text in services_info:
            row_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=self.px, pady=2, anchor="w")

            cb = ctk.CTkCheckBox(
                row_frame,
                text=text,
                variable=self.service_vars[key],
                command=self._on_service_toggle,
                font=AppStyle.get_normal_font(),
                fg_color=AppStyle.COLOR_PRIMARY,
                hover_color=AppStyle.COLOR_PRIMARY_HOVER,
                text_color=AppStyle.COLOR_TEXT_DARK,
            )
            cb.pack(side="left")

            # Pole do wpisania ilości sztuk dla danej usługi
            qty_ent = ctk.CTkEntry(row_frame, width=45, **AppStyle.get_entry_style())
            qty_ent.insert(0, "1")
            qty_ent.bind("<KeyRelease>", lambda e: self.update_callback())
            self.service_qty_entries[key] = qty_ent

            # Mnożnik dla zaniżenia średnicy (szyjki)
            if key == "opuszczenie":
                self.mult_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
                btn_minus = ctk.CTkButton(
                    self.mult_frame,
                    text="-",
                    width=20,
                    height=20,
                    fg_color=AppStyle.COLOR_MUTED,
                    hover_color=AppStyle.COLOR_MUTED_HOVER,
                    command=lambda: self._change_multiplier(-1),
                )
                btn_minus.pack(side="left", padx=2)

                self.lbl_mult_val = ctk.CTkLabel(
                    self.mult_frame,
                    text="10 mm (x1)",
                    font=AppStyle.get_bold_font(),
                    text_color=AppStyle.COLOR_TEXT_ACCENT,
                    width=70,
                )
                self.lbl_mult_val.pack(side="left", padx=AppStyle.PAD_SMALL)

                btn_plus = ctk.CTkButton(
                    self.mult_frame,
                    text="+",
                    width=20,
                    height=20,
                    fg_color=AppStyle.COLOR_MUTED,
                    hover_color=AppStyle.COLOR_MUTED_HOVER,
                    command=lambda: self._change_multiplier(1),
                )
                btn_plus.pack(side="left", padx=2)

            lbl_p = ctk.CTkLabel(
                row_frame,
                text="",
                font=AppStyle.get_normal_font(),
                text_color=AppStyle.COLOR_SUCCESS,
                width=90,
                anchor="e",
            )
            lbl_p.pack(side="right", padx=AppStyle.PAD_SMALL)
            self.service_price_labels[key] = lbl_p

    # ================= LOGIKA WIDOKU I SYNCHRONIZACJI =================

    @staticmethod
    def calculate_shank_value(diam_str):
        """
        Zwraca sugerowaną, znormalizowaną średnicę chwytu dla podanej średnicy roboczej.
        Zaokrągla w górę do najbliższej parzystej liczby całkowitej.
        """
        try:
            val = str(diam_str).replace(",", ".").strip()
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
        except (ValueError, TypeError):
            return ""

    def on_diam_change(self, _=None):
        """
        Aktualizuje średnicę chwytu na podstawie roboczej (gdy override jest wyłączony)
        oraz wywołuje odświeżenie kalkulacji.
        """
        if not self.shank_override.get() and hasattr(self, "shank_entry"):
            raw_val = self.get_working_diameter_str()
            new_shank = self.calculate_shank_value(raw_val)

            self.shank_entry.configure(state="normal")
            self.shank_entry.delete(0, "end")
            self.shank_entry.insert(0, new_shank)
            self.shank_entry.configure(state="disabled")
        self.update_callback()

    def get_working_diameter_str(self):
        """Zwraca bieżącą wartość średnicy roboczej jako ciąg znaków."""
        if hasattr(self, "diam_entry"):
            return self.diam_entry.get()
        return ""

    def toggle_shank(self):
        """Przełącza stan edytowalności chwytu (automatyczny vs ręczny)."""
        if not hasattr(self, "shank_entry"):
            return

        if self.shank_override.get():
            self.shank_entry.configure(
                state="normal",
                fg_color=AppStyle.COLOR_BG_LIGHT,
                border_color=AppStyle.COLOR_SECONDARY,
                border_width=2,
            )
        else:
            self.shank_entry.configure(
                state="disabled",
                fg_color=AppStyle.COLOR_MAIN_BG,
                border_color=AppStyle.COLOR_MUTED,
                border_width=1,
            )
            self.on_diam_change()

        self.update_callback()

    def on_coating_change(self, _=None):
        """Aktualizuje listę dostępnych długości po zmianie rodzaju powłoki."""
        if not hasattr(self, "coat_combo") or not hasattr(self, "len_combo"):
            return

        selected = self.coat_combo.get()
        lengths = database.get_unique_coating_lengths(selected)
        if not lengths:
            lengths = ["100"]

        self.len_combo.configure(values=lengths)
        self.len_combo.set(lengths[0])
        self.update_callback()

    def _on_main_qty_change(self, _=None):
        """
        Synchronizuje ilości w usługach dodatkowych:
        zmniejsza ilość usługi tylko wtedy, gdy główna ilość spadnie poniżej niej.
        """
        raw_main_qty = self.qty_entry.get().strip()
        if raw_main_qty.isdigit():
            new_main_qty = int(raw_main_qty)
            for key, var in self.service_vars.items():
                if var.get():
                    ent = self.service_qty_entries[key]
                    raw_service_qty = ent.get().strip()
                    if raw_service_qty.isdigit() and int(raw_service_qty) > new_main_qty:
                        ent.delete(0, "end")
                        ent.insert(0, str(new_main_qty))
        self.update_callback()

    def _on_service_toggle(self):
        """Pokazuje lub ukrywa pola ilości i kontener mnożnika dla zaznaczonych usług."""
        main_qty = self.qty_entry.get().strip()
        fallback_qty = main_qty if main_qty.isdigit() else "1"

        for key, var in self.service_vars.items():
            ent = self.service_qty_entries[key]
            if var.get():
                if not ent.winfo_ismapped():
                    ent.delete(0, "end")
                    ent.insert(0, fallback_qty)
                    ent.pack(side="left", padx=AppStyle.PAD_SMALL)
            else:
                ent.pack_forget()

        if hasattr(self, "mult_frame"):
            if self.service_vars["opuszczenie"].get():
                self.mult_frame.pack(side="left", padx=AppStyle.PAD_MEDIUM)
            else:
                self.mult_frame.pack_forget()
                self.opuszczenie_mult = 1
                if hasattr(self, "lbl_mult_val"):
                    self.lbl_mult_val.configure(text="10 mm (x1)")

        self.update_callback()

    def _change_multiplier(self, delta):
        """Zmienia mnożnik długości opuszczenia (zaniżenia średnicy)."""
        new_val = self.opuszczenie_mult + delta
        if new_val >= 1:
            self.opuszczenie_mult = new_val
            mm_text = f"{new_val * 10} mm"
            if hasattr(self, "lbl_mult_val"):
                self.lbl_mult_val.configure(text=f"{mm_text} (x{new_val})")
            self.update_callback()

    def get_services_qty_dict(self, fallback_qty=1):
        """Zwraca słownik ilości sztuk dla poszczególnych usług."""
        res = {}
        for k in self.service_vars:
            if self.service_vars[k].get():
                val_s = self.service_qty_entries[k].get().strip()
                res[k] = int(val_s) if val_s.isdigit() else int(fallback_qty)
            else:
                res[k] = 0
        return res

    def update_service_price_labels(self, calc_diam, services_qty_dict):
        """Aktualizuje etykiety cenowe wyświetlane obok checkboxów usług."""
        for key in self.service_vars:
            if key == "zuzycie":
                if self.service_vars[key].get():
                    self.service_price_labels[key].configure(
                        text=f"+5% ({services_qty_dict.get(key, 0)} szt.)"
                    )
                else:
                    self.service_price_labels[key].configure(text="")
                continue

            if self.service_vars[key].get():
                db_name = (
                    "Cięcie"
                    if key == "ciecie"
                    else "Zaniżenie średnicy"
                    if key == "opuszczenie"
                    else "Polerowanie rowka"
                )
                try:
                    price = database.get_service_price_refined(db_name, float(calc_diam))
                    if key == "opuszczenie":
                        price = price * self.opuszczenie_mult
                    s_cost = price * services_qty_dict.get(key, 0)
                    self.service_price_labels[key].configure(text=f"+{s_cost:.2f} zł")
                except (ValueError, TypeError):
                    self.service_price_labels[key].configure(text="")
            else:
                self.service_price_labels[key].configure(text="")

    def load_base_item_data(self, item_data):
        """Ładuje dane wspólne (ilość, chwyt, powłoka, usługi) do formularza edycji."""
        if not item_data:
            return

        if "qty" in item_data and hasattr(self, "qty_entry"):
            self.qty_entry.delete(0, "end")
            self.qty_entry.insert(0, str(item_data["qty"]))

        if "tag" in item_data:
            tag_val = str(item_data.get("tag") or "")
            if hasattr(self, "tag_var"):
                self.tag_var.set(tag_val)
            elif hasattr(self, "tag_entry"):
                self.tag_entry.delete(0, "end")
                self.tag_entry.insert(0, tag_val)

        if "shank_override" in item_data:
            self.shank_override.set(bool(item_data["shank_override"]))
            self.toggle_shank()

        if "shank_diam" in item_data and hasattr(self, "shank_entry"):
            self.shank_entry.configure(state="normal")
            self.shank_entry.delete(0, "end")
            self.shank_entry.insert(0, str(item_data["shank_diam"]))
            if not self.shank_override.get():
                self.shank_entry.configure(state="disabled")

        if (
            "coat_name" in item_data
            and hasattr(self, "coat_combo")
            and item_data["coat_name"] in self.coat_combo.cget("values")
        ):
            self.coat_combo.set(item_data["coat_name"])
            self.on_coating_change()
            if (
                "coat_len" in item_data
                and hasattr(self, "len_combo")
                and item_data["coat_len"] in self.len_combo.cget("values")
            ):
                self.len_combo.set(item_data["coat_len"])

        if "services_status" in item_data:
            for k, val in item_data["services_status"].items():
                if k in self.service_vars:
                    self.service_vars[k].set(val)

        if "services_qty" in item_data:
            for k, q_val in item_data["services_qty"].items():
                if k in self.service_qty_entries:
                    self.service_qty_entries[k].delete(0, "end")
                    self.service_qty_entries[k].insert(0, str(q_val))

        if "opuszczenie_mult" in item_data:
            self.opuszczenie_mult = int(item_data["opuszczenie_mult"])
            mm_text = f"{self.opuszczenie_mult * 10} mm"
            if hasattr(self, "lbl_mult_val"):
                self.lbl_mult_val.configure(text=f"{mm_text} (x{self.opuszczenie_mult})")

        self._on_service_toggle()
