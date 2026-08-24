import math
import customtkinter as ctk
import database
from logic import cart_logic
from ui.style import AppStyle


class SpecialModule(ctk.CTkFrame):
    def __init__(self, parent, update_callback, settings):
        super().__init__(parent, fg_color="transparent")
        self.update_callback = update_callback
        self.settings = settings
        self.shank_override = ctk.BooleanVar(value=False)
        self.opuszczenie_mult = 1

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

        self.add_label(self.left_col, "Typ narzędzia:", AppStyle.get_bold_font())
        self.type_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.type_entry.insert(0, settings.get("last_special_type", "Specjalne"))
        self.type_entry.pack(pady=py_small, padx=px, anchor="w")
        self.type_entry.bind("<KeyRelease>", lambda e: self.update_callback())

        self.add_label(self.left_col, "Liczba ostrzy:", AppStyle.get_bold_font())
        self.blades_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.blades_entry.insert(0, settings.get("last_special_blades", "4"))
        self.blades_entry.pack(pady=py_small, padx=px, anchor="w")
        self.blades_entry.bind("<KeyRelease>", lambda e: self.update_callback())

        self.add_label(self.left_col, "Średnica robocza:", AppStyle.get_bold_font())
        self.diam_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.diam_entry.insert(0, settings.get("last_special_diam", "10.0"))
        self.diam_entry.pack(pady=py_small, padx=px, anchor="w")
        self.diam_entry.bind("<KeyRelease>", self.on_diam_change)

        self.add_label(self.left_col, "Promień (R):", AppStyle.get_bold_font())
        self.radius_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.radius_entry.insert(0, settings.get("last_special_radius", "0.5"))
        self.radius_entry.pack(pady=py_small, padx=px, anchor="w")
        self.radius_entry.bind("<KeyRelease>", lambda e: self.update_callback())

        self.add_label(self.left_col, "Średnica chwytu:", AppStyle.get_bold_font())
        s_frame = ctk.CTkFrame(self.left_col, fg_color="transparent")
        s_frame.pack(fill="x", pady=py_small, padx=px)

        self.shank_entry = ctk.CTkEntry(s_frame, width=140, **AppStyle.get_entry_style())
        self.shank_entry.insert(0, settings.get("last_special_shank", "10.0"))
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

        self.add_label(self.left_col, "Powłoka:", AppStyle.get_bold_font())
        self.coat_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.coat_entry.insert(0, settings.get("last_special_coating", "Brak"))
        self.coat_entry.pack(pady=py_small, padx=px, anchor="w")
        self.coat_entry.bind("<KeyRelease>", lambda e: self.update_callback())

        self.add_label(self.left_col, "Długość powłoki (L):", AppStyle.get_bold_font())
        self.len_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.len_entry.insert(0, settings.get("last_special_length", "100"))
        self.len_entry.pack(pady=py_small, padx=px, anchor="w")
        self.len_entry.bind("<KeyRelease>", lambda e: self.update_callback())

        self.add_label(self.left_col, "Ilość sztuk:", AppStyle.get_bold_font())
        self.qty_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.qty_entry.insert(0, settings.get("last_special_qty", "1"))
        self.qty_entry.pack(pady=(0, AppStyle.PAD_MEDIUM), padx=px, anchor="w")
        self.qty_entry.bind("<KeyRelease>", self._on_main_qty_change)

        self.add_label(self.left_col, "Cena za sztukę [zł]:", AppStyle.get_bold_font())
        self.unit_price_entry = ctk.CTkEntry(self.left_col, width=300, **AppStyle.get_entry_style())
        self.unit_price_entry.insert(0, settings.get("last_special_unit_price", "0.00"))
        self.unit_price_entry.pack(pady=py_small, padx=px, anchor="w")
        self.unit_price_entry.bind("<KeyRelease>", lambda e: self.update_callback())

        self.add_label(self.right_col, "Usługi dodatkowe:", AppStyle.get_bold_font())
        self.service_vars = {
            "ciecie": ctk.BooleanVar(),
            "opuszczenie": ctk.BooleanVar(),
            "polerowanie": ctk.BooleanVar(),
            "zuzycie": ctk.BooleanVar(),
        }
        self.service_qty_entries = {}
        self.service_price_labels = {}

        services_info = [
            ("ciecie", "Cięcie narzędzia (skracanie)"),
            ("opuszczenie", "Zaniżenie średnicy (szyjka)"),
            ("polerowanie", "Polerowanie rowka wiórowego"),
            ("zuzycie", "Ciężkie zużycie / wyszczerbienia (+5%)"),
        ]

        for key, text in services_info:
            row_frame = ctk.CTkFrame(self.right_col, fg_color="transparent")
            row_frame.pack(fill="x", padx=px, pady=2, anchor="w")

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

            qty_ent = ctk.CTkEntry(row_frame, width=45, **AppStyle.get_entry_style())
            qty_ent.insert(0, "1")
            qty_ent.bind("<KeyRelease>", lambda e: self.update_callback())
            self.service_qty_entries[key] = qty_ent

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

            lbl_p = ctk.CTkLabel(row_frame, text="", font=AppStyle.get_normal_font(), text_color=AppStyle.COLOR_SUCCESS, width=90, anchor="e")
            lbl_p.pack(side="right", padx=AppStyle.PAD_SMALL)
            self.service_price_labels[key] = lbl_p

        self.toggle_shank()
        self._on_service_toggle()

    def add_label(self, parent_frame, text, font):
        ctk.CTkLabel(parent_frame, text=text, font=font, text_color=AppStyle.COLOR_TEXT_DARK).pack(pady=(AppStyle.PAD_SMALL, 0), padx=AppStyle.PAD_LARGE, anchor="w")

    def _on_main_qty_change(self, _=None):
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
            self.lbl_mult_val.configure(text=f"{new_val * 10} mm (x{new_val})")
            self.update_callback()

    def toggle_shank(self):
        if self.shank_override.get():
            self.shank_entry.configure(state="normal", fg_color=AppStyle.COLOR_BG_LIGHT, border_color=AppStyle.COLOR_SECONDARY, border_width=2)
        else:
            self.shank_entry.configure(state="disabled", fg_color=AppStyle.COLOR_MAIN_BG, border_color=AppStyle.COLOR_MUTED, border_width=1)
        self.update_callback()

    def on_diam_change(self, _=None):
        if not self.shank_override.get():
            raw_val = self.diam_entry.get()
            try:
                d = float(raw_val.replace(',', '.'))
                if d <= 0:
                    self.shank_entry.delete(0, "end")
                    self.shank_entry.insert(0, "")
                else:
                    value = math.ceil(d)
                    if value % 2 != 0:
                        value += 1
                    self.shank_entry.delete(0, "end")
                    self.shank_entry.insert(0, str(int(value)))
            except ValueError:
                pass
        self.update_callback()

    def validate_all(self, diam, z, qty, shank, unit_price):
        try:
            float(diam)
            float(shank)
            float(unit_price)
            if not z.isdigit() or not qty.isdigit():
                raise ValueError()
            return True
        except ValueError:
            from ui.components import OstrzomatPopup
            OstrzomatPopup(self.master, title="Błąd", message="Wprowadzono nieprawidłowe wartości. Popraw je przed kalkulacją!", type="error")
            return False

    def set_item_data(self, item_data):
        if not item_data:
            return

        if "type" in item_data:
            self.type_entry.delete(0, "end")
            self.type_entry.insert(0, str(item_data["type"]))

        if "diam" in item_data:
            self.diam_entry.delete(0, "end")
            self.diam_entry.insert(0, str(item_data["diam"]))

        if "z" in item_data:
            self.blades_entry.delete(0, "end")
            self.blades_entry.insert(0, str(item_data["z"]))

        if "qty" in item_data:
            self.qty_entry.delete(0, "end")
            self.qty_entry.insert(0, str(item_data["qty"]))

        if "shank_diam" in item_data:
            self.shank_entry.delete(0, "end")
            self.shank_entry.insert(0, str(item_data["shank_diam"]))

        if "coat_name" in item_data:
            self.coat_entry.delete(0, "end")
            self.coat_entry.insert(0, str(item_data["coat_name"]))

        if "coat_len" in item_data:
            self.len_entry.delete(0, "end")
            self.len_entry.insert(0, str(item_data["coat_len"]))

        if "tool_unit" in item_data:
            self.unit_price_entry.delete(0, "end")
            self.unit_price_entry.insert(0, str(item_data["tool_unit"]))

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
            self.lbl_mult_val.configure(text=f"{self.opuszczenie_mult * 10} mm (x{self.opuszczenie_mult})")

        self._on_service_toggle()

    def get_full_item_data(self, run_validation=False):
        try:
            diam = self.diam_entry.get().replace(',', '.').strip()
            shank = self.shank_entry.get().replace(',', '.').strip()
            qty = self.qty_entry.get().strip() or "1"
            t_type = self.type_entry.get().strip() or "Specjalne"
            blades = self.blades_entry.get().strip() or "1"
            coat = self.coat_entry.get().strip() or "Brak"
            coat_len = self.len_entry.get().replace(',', '.').strip() or "0"
            unit_price = self.unit_price_entry.get().replace(',', '.').strip() or "0"

            if run_validation:
                if not self.validate_all(diam, blades, qty, shank, unit_price):
                    return None

            services_qty_dict = {}
            for key in self.service_vars:
                if self.service_vars[key].get():
                    val_s = self.service_qty_entries[key].get().strip()
                    services_qty_dict[key] = int(val_s) if val_s.isdigit() else int(qty)
                else:
                    services_qty_dict[key] = 0

            heavy_wear_qty = services_qty_dict.get("zuzycie", 0)
            tool_unit = float(unit_price)
            total_tool = tool_unit * int(qty)

            c_j, c_r = (0.0, 0.0)
            if coat and coat != "Brak":
                c_j, c_r = cart_logic.calculate_coating_price(coat, diam, coat_len, qty)

            e_j_total, e_r_total, active_labels = cart_logic.calculate_extra_services(
                self.service_vars,
                services_qty_dict,
                diam,
                qty,
                opuszczenie_multiplier=self.opuszczenie_mult,
            )

            for key in self.service_vars:
                if key == "zuzycie":
                    if self.service_vars[key].get():
                        self.service_price_labels[key].configure(text=f"+5% ({services_qty_dict[key]} szt.)")
                    else:
                        self.service_price_labels[key].configure(text="")
                    continue

                if self.service_vars[key].get():
                    db_name = "Cięcie" if key == "ciecie" else "Zaniżenie średnicy" if key == "opuszczenie" else "Polerowanie rowka"
                    price = database.get_service_price_refined(db_name, float(diam))
                    if key == "opuszczenie":
                        price = price * self.opuszczenie_mult
                    s_cost = price * services_qty_dict[key]
                    self.service_price_labels[key].configure(text=f"+{s_cost:.2f} zł")
                else:
                    self.service_price_labels[key].configure(text="")

            database.save_user_settings({
                "last_special_type": t_type,
                "last_special_blades": blades,
                "last_special_diam": diam,
                "last_special_radius": self.radius_entry.get().strip(),
                "last_special_shank": shank,
                "last_special_coating": coat,
                "last_special_length": coat_len,
                "last_special_qty": qty,
                "last_special_unit_price": unit_price,
            })

            display_type = t_type
            radius_val = self.radius_entry.get().replace(',', '.').strip()
            if radius_val:
                try:
                    float(radius_val)
                    display_type = f"{t_type} R{radius_val}"
                except ValueError:
                    pass

            return {
                "type": display_type,
                "diam": diam,
                "shank_diam": shank,
                "shank_override": self.shank_override.get(),
                "z": blades,
                "qty": qty,
                "tool_unit": tool_unit,
                "total_tool": total_tool,
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
