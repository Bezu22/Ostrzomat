import customtkinter as ctk
import database
from logic import cart_logic

class FrezModule(ctk.CTkFrame):
    def __init__(self, parent, update_callback, settings):
        super().__init__(parent, fg_color="transparent")
        self.update_callback = update_callback
        self.settings = settings
        self.shank_override = ctk.BooleanVar(value=False)
        
        f_bold = ("Arial", 12, "bold")
        px = 20 # padding wewnętrzny
        
        # TYP I OSTRZA
        self.add_label("Typ narzędzia:", f_bold)
        self.type_combo = ctk.CTkComboBox(self, width=300, values=database.get_unique_tool_types("Frezy"), command=self.update_callback)
        self.type_combo.set(settings.get("last_tool_type", "Frez prosty"))
        self.type_combo.pack(pady=(0, 10), padx=px, anchor="w")

        self.add_label("Liczba ostrzy:", f_bold)
        self.blades_entry = ctk.CTkEntry(self, width=300)
        self.blades_entry.insert(0, settings.get("last_blades", "4"))
        self.blades_entry.pack(pady=(0, 10), padx=px, anchor="w")
        self.blades_entry.bind("<KeyRelease>", lambda e: self.update_callback())

        # ŚREDNICA ROBOCZA
        self.add_label("Średnica robocza (Ø):", f_bold)
        self.diam_entry = ctk.CTkEntry(self, width=300)
        self.diam_entry.insert(0, settings.get("last_diam", "10.0"))
        self.diam_entry.pack(pady=(0, 10), padx=px, anchor="w")
        self.diam_entry.bind("<KeyRelease>", self.on_diam_change)

        # CHWYT 
        self.add_label("Średnica chwytu (d):", f_bold)
        s_frame = ctk.CTkFrame(self, fg_color="transparent")
        s_frame.pack(fill="x", pady=(0, 10), padx=px, anchor="w")
        
        self.shank_entry = ctk.CTkEntry(s_frame, width=140)
        self.shank_entry.insert(0, settings.get("last_shank", "10.0"))
        self.shank_entry.pack(side="left")
        
        self.shank_cb = ctk.CTkCheckBox(s_frame, text="Ręcznie", variable=self.shank_override, command=self.toggle_shank)
        self.shank_cb.pack(side="left", padx=10)


        # ILOŚĆ SZTUK 
        self.add_label("Ilość sztuk:", f_bold)
        self.qty_entry = ctk.CTkEntry(self, width=300)
        self.qty_entry.insert(0, "1")
        self.qty_entry.pack(pady=(0, 10), padx=px, anchor="w")
        self.qty_entry.bind("<KeyRelease>", lambda e: self.update_callback())

        # POWŁOKA I USŁUGI
        self.setup_extras(f_bold, px)
        
        # Inicjalizacja stanu chwytu
        self.toggle_shank()

    def add_label(self, text, font):
        ctk.CTkLabel(self, text=text, font=font).pack(pady=(5, 0), padx=20, anchor="w")

    def setup_extras(self, font, px):
        self.add_label("Powłoka:", font)
        self.coat_combo = ctk.CTkComboBox(
            self, 
            width=300, 
            values=["Brak"] + database.get_unique_coating_names(), 
            command=self.on_coating_change 
        )
        self.coat_combo.set("Brak")
        self.coat_combo.pack(pady=(0, 5), padx=px, anchor="w")

        # --- DYNAMICZNE POLE DŁUGOŚCI ---
        self.len_label = ctk.CTkLabel(self, text="Długość powłoki (L):", font=font)
        self.len_combo = ctk.CTkComboBox(self, width=300, values=[], command=self.update_callback)
        
        self.add_label("Usługi dodatkowe:", font)
        self.service_vars = {
            "ciecie": ctk.BooleanVar(),
            "opuszczenie": ctk.BooleanVar(),
            "polerowanie": ctk.BooleanVar()
        }
        for k in self.service_vars:
            txt = "Cięcie" if k=="ciecie" else "Zaniżenie" if k=="opuszczenie" else "Polerowanie"
            ctk.CTkCheckBox(self, text=txt, variable=self.service_vars[k], command=self.update_callback).pack(anchor="w", padx=px+10, pady=2)

    def on_diam_change(self, _=None):
        """Synchronizacja chwytu ze średnicą."""
        if not self.shank_override.get():
            val = self.diam_entry.get()
            self.shank_entry.configure(state="normal")
            self.shank_entry.delete(0, "end")
            self.shank_entry.insert(0, val)
            self.shank_entry.configure(state="disabled")
        self.update_callback()

    def on_coating_change(self, _=None):
        """Wywoływane przy zmianie powłoki - aktualizuje listę długości."""
        selected_coat = self.coat_combo.get()
        
        if selected_coat != "Brak":
            lengths = database.get_unique_coating_lengths(selected_coat)
            if lengths:
                self.len_combo.configure(values=lengths)
                self.len_combo.set(lengths[0])
                # Pokazujemy pola długości
                self.len_label.pack(after=self.coat_combo, pady=(5, 0), padx=20, anchor="w")
                self.len_combo.pack(after=self.len_label, pady=(0, 10), padx=20, anchor="w")
        else:
            # Ukrywamy pola, jeśli brak powłoki
            self.len_label.pack_forget()
            self.len_combo.pack_forget()
            
        self.update_callback()

    def toggle_shank(self):
        if self.shank_override.get():
            self.shank_entry.configure(state="normal")
        else:
            self.shank_entry.configure(state="disabled")
            self.on_diam_change()
        self.update_callback()

    def get_full_item_data(self):
        """Przygotowuje obiekt Item dla koszyka."""
        try:
            diam = self.diam_entry.get().replace(',', '.')
            qty = self.qty_entry.get() or "1" 
            t_type = self.type_combo.get()
            blades = self.blades_entry.get()
            coat = self.coat_combo.get()
            
            # Pobieramy długość jeśli pole istnieje, inaczej domyślne 100
            # Upewnij się, że self.len_combo jest zdefiniowane w setup_extras
            try:
                coat_len = self.len_combo.get() if coat != "Brak" else "100"
            except AttributeError:
                coat_len = "100"

            # 1. OSTRZENIE - Twoje cart_logic zwraca (jednostkowa, razem)
            tool_jedn, tool_razem = cart_logic.calculate_tool_price(t_type, blades, diam, qty)
            
            # 2. POWŁOKA - Twoje cart_logic zwraca (jednostkowa, razem)
            coat_jedn, coat_razem = cart_logic.calculate_coating_price(coat, diam, coat_len, qty)
            
            # 3. USŁUGI - Twoje cart_logic zwraca (jednostkowa_suma, razem_suma, lista_aktywnych)
            extra_jedn, extra_razem, active_services = cart_logic.calculate_extra_services(self.service_vars, diam, qty)

            # Aktualizacja cache ustawień
            database.save_user_settings({
                "last_tool_type": t_type,
                "last_blades": blades,
                "last_diam": diam,
                "last_shank": self.shank_entry.get()
            })

            # Zwracamy słownik z poprawnymi nazwami zmiennych
            return {
                "type": t_type,
                "diam": diam,
                "z": blades,
                "qty": qty,
                "tool_unit": f"{tool_jedn:.2f} zł",
                "total_tool": f"{tool_razem:.2f} zł",
                "coat_name": coat,
                "coat_len": coat_len if coat != "Brak" else "-",
                "coat_unit": f"{coat_jedn:.2f} zł",   # Dodana cena jednostkowa powłoki
                "total_coat": f"{coat_razem:.2f} zł",
                "services_status": {k: v.get() for k, v in self.service_vars.items()},
                "extra_unit": f"{extra_jedn:.2f} zł",  # Dodana cena jednostkowa usług
                "total_extra": f"{extra_razem:.2f} zł"
            }
        except Exception as e:
            print(f"Błąd w get_full_item_data: {e}")
            return None