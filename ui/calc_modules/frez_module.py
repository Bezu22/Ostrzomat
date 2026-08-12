import math
import re
import customtkinter as ctk
import database
from logic import cart_logic
from ui.style import AppStyle

class FrezModule(ctk.CTkFrame):
    def __init__(self, parent, update_callback, settings):
        super().__init__(parent, fg_color="transparent")
        self.update_callback = update_callback
        self.settings = settings
        self.shank_override = ctk.BooleanVar(value=False)
        
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
        self.type_combo = ctk.CTkComboBox(
            self.left_col, 
            width=300, 
            values=database.get_unique_tool_types("Frezy"), 
            command=self._on_type_change,
            **AppStyle.get_combo_style()
        )
        self.type_combo.set(settings.get("last_tool_type", "Frez prosty"))
        self.type_combo.configure(state="readonly") 
        self.type_combo.pack(pady=py_small, padx=px, anchor="w")

        # --- POLE PROMIENIA ---
        self.radius_frame = ctk.CTkFrame(self.left_col, fg_color="transparent")
        lbl_r = ctk.CTkLabel(self.radius_frame, text="Promień (R):", font=AppStyle.get_bold_font(), text_color=AppStyle.COLOR_TEXT_DARK)
        lbl_r.pack(anchor="w")
        
        self.radius_entry = ctk.CTkEntry(self.radius_frame, width=300, **AppStyle.get_entry_style())
        self.radius_entry.insert(0, "0.5")
        self.radius_entry.pack(pady=py_small, anchor="w")
        self.radius_entry.bind("<KeyRelease>", lambda e: self.update_callback())

        self.add_label(self.left_col, "Liczba ostrzy:", AppStyle.get_bold_font())
        self.blades_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.blades_entry.insert(0, settings.get("last_blades", "4"))
        self.blades_entry.pack(pady=py_small, padx=px, anchor="w")
        self.blades_entry.bind("<KeyRelease>", lambda e: self.update_callback())

        # --- 2. ŚREDNICA ROBOCZA ---
        self.add_label(self.left_col, "Średnica robocza:", AppStyle.get_bold_font())
        self.diam_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.diam_entry.insert(0, settings.get("last_diam", "10.0"))
        self.diam_entry.pack(pady=py_small, padx=px, anchor="w")
        self.diam_entry.bind("<KeyRelease>", self.on_diam_change)

        # --- 3. CHWYT ---
        self.add_label(self.left_col, "Średnica chwytu:", AppStyle.get_bold_font())
        s_frame = ctk.CTkFrame(self.left_col, fg_color="transparent")
        s_frame.pack(fill="x", pady=py_small, padx=px)
        
        self.shank_entry = ctk.CTkEntry(s_frame, width=140, **AppStyle.get_entry_style())
        self.shank_entry.insert(0, settings.get("last_shank", "10.0"))
        self.shank_entry.pack(side="left")
        
        self.shank_cb = ctk.CTkCheckBox(
            s_frame, text="", width=24, variable=self.shank_override, command=self.toggle_shank,
            fg_color=AppStyle.COLOR_PRIMARY, hover_color=AppStyle.COLOR_PRIMARY_HOVER
        )
        self.shank_cb.pack(side="left", padx=AppStyle.PAD_MEDIUM)

        # --- 4. POWŁOKA ---
        self.add_label(self.left_col, "Powłoka:", AppStyle.get_bold_font())
        self.coat_combo = ctk.CTkComboBox(
            self.left_col, width=300, values=["Brak"] + database.get_unique_coating_names(), 
            command=self.on_coating_change, **AppStyle.get_combo_style()
        )
        self.coat_combo.set("Brak")
        self.coat_combo.configure(state="readonly")
        self.coat_combo.pack(pady=py_small, padx=px, anchor="w")

        self.len_label = ctk.CTkLabel(self.left_col, text="Długość (L):", font=AppStyle.get_bold_font(), text_color=AppStyle.COLOR_TEXT_DARK)
        self.len_label.pack(pady=(AppStyle.PAD_SMALL, 0), padx=px, anchor="w")

        self.len_combo = ctk.CTkComboBox(self.left_col, width=300, values=[], command=self.update_callback, **AppStyle.get_combo_style())
        self.len_combo.configure(state="readonly")
        self.len_combo.pack(pady=(0, AppStyle.PAD_MEDIUM), padx=px, anchor="w")

        # --- 6. ILOŚĆ SZTUK ---
        self.add_label(self.left_col, "Ilość sztuk:", AppStyle.get_bold_font())
        self.qty_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.qty_entry.insert(0, "1")
        self.qty_entry.pack(pady=(0, AppStyle.PAD_MEDIUM), padx=px, anchor="w")
        self.qty_entry.bind("<KeyRelease>", self._on_main_qty_change)

        # ================= KOLUMNA PRAWA =================
        # --- 5. USŁUGI DODATKOWE ---
        self.add_label(self.right_col, "Usługi dodatkowe:", AppStyle.get_bold_font())
        self.service_vars = {
            "ciecie": ctk.BooleanVar(),
            "opuszczenie": ctk.BooleanVar(),
            "polerowanie": ctk.BooleanVar(),
            "zuzycie": ctk.BooleanVar()
        }
        self.service_qty_entries = {}
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

            # Pole do wpisania ilości sztuk dla danej usługi
            qty_ent = ctk.CTkEntry(row_frame, width=45, **AppStyle.get_entry_style())
            qty_ent.insert(0, "1")
            qty_ent.bind("<KeyRelease>", lambda e: self.update_callback())
            self.service_qty_entries[key] = qty_ent

            if key == "opuszczenie":
                self.mult_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
                btn_minus = ctk.CTkButton(
                    self.mult_frame, text="-", width=20, height=20, 
                    fg_color=AppStyle.COLOR_MUTED, hover_color=AppStyle.COLOR_MUTED_HOVER, 
                    command=lambda: self._change_multiplier(-1)
                )
                btn_minus.pack(side="left", padx=2)
                
                self.lbl_mult_val = ctk.CTkLabel(
                    self.mult_frame, text="10 mm (x1)", font=AppStyle.get_bold_font(), 
                    text_color=AppStyle.COLOR_TEXT_ACCENT, width=70
                )
                self.lbl_mult_val.pack(side="left", padx=AppStyle.PAD_SMALL)
                
                btn_plus = ctk.CTkButton(
                    self.mult_frame, text="+", width=20, height=20, 
                    fg_color=AppStyle.COLOR_MUTED, hover_color=AppStyle.COLOR_MUTED_HOVER, 
                    command=lambda: self._change_multiplier(1)
                )
                btn_plus.pack(side="left", padx=2)

            lbl_p = ctk.CTkLabel(row_frame, text="", font=AppStyle.get_normal_font(), text_color=AppStyle.COLOR_SUCCESS, width=90, anchor="e")
            lbl_p.pack(side="right", padx=AppStyle.PAD_SMALL)
            self.service_price_labels[key] = lbl_p

        self._on_type_change()
        self.on_coating_change()
        self.toggle_shank()

    def _on_main_qty_change(self, _=None):
        """
        Reaguje na zmianę w głównym polu ilości sztuk.
        Zmniejsza ilości w usługach tylko wtedy, gdy główna ilość stanie się mniejsza od nich.
        Puste pole lub niepoprawne znaki są ignorowane, aby nie niszczyć wpisanych wartości.
        """
        raw_main_qty = self.qty_entry.get().strip()
        
        # Sprawdzamy, czy w głównym polu znajduje się poprawna cyfra
        if raw_main_qty.isdigit():
            new_main_qty = int(raw_main_qty)
            
            for key, var in self.service_vars.items():
                if var.get():
                    ent = self.service_qty_entries[key]
                    raw_service_qty = ent.get().strip()
                    
                    # Jeśli w usłudze jest poprawna cyfra i jest większa od nowej głównej ilości -> zmniejszamy
                    if raw_service_qty.isdigit():
                        if int(raw_service_qty) > new_main_qty:
                            ent.delete(0, "end")
                            ent.insert(0, str(new_main_qty))
                            
        self.update_callback()

    def _on_service_toggle(self):
        """
        Obsługuje włączanie/wyłączanie poszczególnych usług.
        Uzupełnia pole ilości wartością z formularza TYLKO w momencie włączania danej usługi.
        """
        main_qty = self.qty_entry.get().strip()
        fallback_qty = main_qty if main_qty.isdigit() else "1"

        for key, var in self.service_vars.items():
            ent = self.service_qty_entries[key]
            
            if var.get():
                # Jeśli pole nie jest jeszcze widoczne na ekranie -> usługa została właśnie włączona!
                if not ent.winfo_ismapped():
                    ent.delete(0, "end")
                    ent.insert(0, fallback_qty)
                    ent.pack(side="left", padx=AppStyle.PAD_SMALL)
            else:
                # Usługa wyłączona -> ukrywamy pole
                ent.pack_forget()

        if self.service_vars["opuszczenie"].get():
            self.mult_frame.pack(side="left", padx=AppStyle.PAD_MEDIUM)
        else:
            self.mult_frame.pack_forget()
            self.opuszczenie_mult = 1
            self.lbl_mult_val.configure(text="10 mm (x1)")
            
        self.update_callback()

    def _on_type_change(self, _=None):
        selected_type = self.type_combo.get()
        px = AppStyle.PAD_LARGE
        py_small = (0, AppStyle.PAD_SMALL)

        if "promieniowy" in selected_type.lower():
            self.radius_frame.pack(after=self.type_combo, pady=py_small, padx=px, anchor="w", fill="x")
        else:
            self.radius_frame.pack_forget()

        self.update_callback()

    def set_item_data(self, item_data):
        """Wypełnia formularz danymi pozycji przychodzącej do EDYCJI z koszyka."""
        if not item_data:
            return

        raw_type = item_data.get("type", "Frez prosty")
        radius_val = "0.5"

        match = re.search(r"^(.*?)\s+R([\d\.,]+)$", raw_type, re.IGNORECASE)
        if match:
            clean_type = match.group(1).strip()
            radius_val = match.group(2).replace(',', '.').strip()
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

        if "services_qty" in item_data:
            for k, q_val in item_data["services_qty"].items():
                if k in self.service_qty_entries:
                    self.service_qty_entries[k].delete(0, "end")
                    self.service_qty_entries[k].insert(0, str(q_val))

        if "opuszczenie_mult" in item_data:
            self.opuszczenie_mult = item_data["opuszczenie_mult"]
            mm_text = f"{self.opuszczenie_mult * 10} mm"
            self.lbl_mult_val.configure(text=f"{mm_text} (x{self.opuszczenie_mult})")

        self._on_service_toggle()

    def add_label(self, parent_frame, text, font):
        ctk.CTkLabel(parent_frame, text=text, font=font, text_color=AppStyle.COLOR_TEXT_DARK).pack(pady=(AppStyle.PAD_SMALL, 0), padx=AppStyle.PAD_LARGE, anchor="w")

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
                state="normal", 
                fg_color=AppStyle.COLOR_BG_LIGHT,
                border_color=AppStyle.COLOR_SECONDARY,
                border_width=2
            )
        else:
            self.shank_entry.configure(
                state="disabled", 
                fg_color=AppStyle.COLOR_MAIN_BG,
                border_color=AppStyle.COLOR_MUTED,
                border_width=1
            )
            self.on_diam_change()
            
        self.update_callback()

    def on_coating_change(self, _=None):
        selected = self.coat_combo.get()
        lengths = database.get_unique_coating_lengths(selected)
        if not lengths:
            raise ValueError("Błąd bazy danych: Brak długości w tabeli pricelist_coatings.")
        self.len_combo.configure(values=lengths)
        self.len_combo.set(lengths[0])
        self.update_callback()

    def validate_all(self, diam, z, qty, shank):
        try:
            float(diam)
            float(shank)
            if not z.isdigit() or not qty.isdigit():
                raise ValueError()
            
            if "promieniowy" in self.type_combo.get().lower():
                r_val = self.radius_entry.get().replace(',', '.').strip()
                float(r_val)

            return True
        except ValueError:
            from ui.components import OstrzomatPopup
            OstrzomatPopup(self.master, title="Błąd", message="Wprowadzono nieprawidłowe wartości. Popraw je przed kalkulacją!", type="error")
            return False
    
    def get_full_item_data(self, run_validation=False):
        try:
            diam = self.diam_entry.get().replace(',', '.').strip()
            shank = self.shank_entry.get().replace(',', '.').strip()
            qty = self.qty_entry.get().strip() or "1" 
            t_type = self.type_combo.get()
            blades = self.blades_entry.get()
            coat = self.coat_combo.get()
            coat_len = self.len_combo.get() if hasattr(self, 'len_combo') else "100"

            if run_validation:
                if not self.validate_all(diam, blades, qty, shank):
                    return None
            
            calc_diam = diam

            # Odczyt ilości sztuk dla każdej z usług
            services_qty_dict = {}
            for k in self.service_vars:
                if self.service_vars[k].get():
                    val_s = self.service_qty_entries[k].get().strip()
                    services_qty_dict[k] = int(val_s) if val_s.isdigit() else int(qty)
                else:
                    services_qty_dict[k] = 0

            heavy_wear_qty = services_qty_dict.get("zuzycie", 0)
            
            # Wycena narzędzia i usług z indywidualnymi ilościami
            t_j, t_r = cart_logic.calculate_tool_price(t_type, blades, calc_diam, qty, heavy_wear_qty=heavy_wear_qty)
            c_j, c_r = cart_logic.calculate_coating_price(coat, calc_diam, coat_len, qty)
            
            e_j_total, e_r_total, active_labels = cart_logic.calculate_extra_services(
                self.service_vars, services_qty_dict, calc_diam, qty, opuszczenie_multiplier=self.opuszczenie_mult
            )

            # Aktualizacja podglądu cen przy opcjach
            for key in self.service_vars:
                if key == "zuzycie":
                    if self.service_vars[key].get():
                        self.service_price_labels[key].configure(text=f"+5% ({services_qty_dict[key]} szt.)")
                    else:
                        self.service_price_labels[key].configure(text="")
                    continue

                if self.service_vars[key].get():
                    db_name = "Cięcie" if key == "ciecie" else "Zaniżenie średnicy" if key == "opuszczenie" else "Polerowanie rowka"
                    price = database.get_service_price_refined(db_name, float(calc_diam))
                    if key == "opuszczenie":
                        price = price * self.opuszczenie_mult
                    
                    s_cost = price * services_qty_dict[key]
                    self.service_price_labels[key].configure(text=f"+{s_cost:.2f} zł")
                else:
                    self.service_price_labels[key].configure(text="")

            database.save_user_settings({
                "last_tool_type": t_type, "last_blades": blades,
                "last_diam": diam, "last_shank": shank
            })

            display_type = t_type
            if "promieniowy" in t_type.lower():
                r_text = self.radius_entry.get().replace(',', '.').strip() or "0.5"
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
                "total_extra": e_r_total
            }
        except Exception as e:
            print(f"Błąd w module FrezModule: {e}")
            return None
    
    
    def _change_multiplier(self, delta):
        new_val = self.opuszczenie_mult + delta
        if new_val >= 1:
            self.opuszczenie_mult = new_val
            mm_text = f"{new_val * 10} mm"
            self.lbl_mult_val.configure(text=f"{mm_text} (x{new_val})")
            self.update_callback()