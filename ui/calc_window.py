import customtkinter as ctk
from tkinter import messagebox
import database
from ui.calc_modules.frez_module import FrezModule
from ui.components import OstrzomatPopup

class ToolCalcWindow(ctk.CTkToplevel):
    def __init__(self, parent, tool_category="Frezy", edit_mode=False, item_data=None, item_index=None):
        super().__init__(parent)
        self.parent = parent
        self.tool_category = tool_category
        
        # Zapisujemy parametry stanu edycji
        self.edit_mode = edit_mode
        self.item_data = item_data
        self.item_index = item_index
        
        if self.edit_mode:
            self.title(f"Edycja pozycji L.p. {self.item_index + 1}: {tool_category}")
        else:
            self.title(f"Konfiguracja: {tool_category}")
        
        # Przyklejenie do góry ekranu
        width, height = 550, 950
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        self.geometry(f"{width}x{height}+{x}+0")
        
        self.attributes("-topmost", True)
        self.grab_set()

        self.settings = database.get_user_settings()
        
        # Główny kontener przewijany
        self.main_scroll = ctk.CTkScrollableFrame(self)
        self.main_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # --- DYNAMICZNE ŁADOWANIE MODUŁU ---
        self.tool_module = None
        if tool_category == "Frezy":
            self.tool_module = FrezModule(self.main_scroll, self.update_calculation, self.settings)
            self.tool_module.pack(fill="x", padx=10, pady=10)
        
        # Jeśli moduł się załadował, dodaj przyciski i odśwież
        if self.tool_module:
            self.setup_price_preview()
            self.setup_action_buttons()
            
            # Jeśli jesteśmy w trybie edycji, ładujemy stare dane do pól formularza
            if self.edit_mode and self.item_data:
                self.load_item_data_into_form()
                
            self.update_calculation()
        else:
            ctk.CTkLabel(self.main_scroll, text="Błąd ładowania modułu").pack()
    
    def setup_price_preview(self):
        """Tworzy sekcję wyświetlającą ceny przed dodaniem do koszyka."""
        self.preview_frame = ctk.CTkFrame(self.main_scroll, fg_color=["#EBEBEB", "#2B2B2B"])
        self.preview_frame.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(self.preview_frame, text="CENA - PODGLĄD", font=("Arial", 13, "bold")).pack(pady=5)
        
        # Słownik na etykiety, żeby łatwo je aktualizować
        self.price_labels = {}
        fields = [
            ("Ostrzenie:", "tool_price"),
            ("Powlekanie:", "coat_price"),
            ("Usługi dodatkowe:", "extra_price"),
            ("SUMA:", "total_price")
        ]
        
        for label_text, key in fields:
            f = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
            f.pack(fill="x", padx=20)
            ctk.CTkLabel(f, text=label_text, font=("Arial", 11)).pack(side="left")
            self.price_labels[key] = ctk.CTkLabel(f, text="0.00 zł", font=("Arial", 11, "bold"))
            self.price_labels[key].pack(side="right")

    def setup_action_buttons(self):
        btn_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=20)

        # Tryb edycji zmienia wygląd i przeznaczenie głównego przycisku akcji
        btn_text = "ZAPISZ ZMIANY" if self.edit_mode else "DODAJ DO KOSZYKA"
        btn_color = "#e67e22" if self.edit_mode else "#28a745"
        btn_cmd = self.save_changes if self.edit_mode else self.add_to_cart

        self.add_btn = ctk.CTkButton(btn_frame, text=btn_text, 
                                     height=50, font=("Arial", 14, "bold"), 
                                     fg_color=btn_color, command=btn_cmd)
        self.add_btn.pack(fill="x", pady=5)

        self.close_btn = ctk.CTkButton(btn_frame, text="ZAMKNIJ", 
                                      height=40, fg_color="#666", command=self.destroy)
        self.close_btn.pack(fill="x", pady=5)

    def load_item_data_into_form(self):
        """Wstrzykuje dane edytowanej pozycji bezpośrednio do widżetów modułu."""
        try:
            m = self.tool_module
            d = self.item_data
            
            # Wypełnianie pól tekstowych i list rozwijanych
            if hasattr(m, 'type_combo'): m.type_combo.set(d.get("type", ""))
            if hasattr(m, 'blades_entry'): 
                m.blades_entry.delete(0, 'end')
                m.blades_entry.insert(0, d.get("z", ""))
            if hasattr(m, 'diam_entry'):
                m.diam_entry.delete(0, 'end')
                m.diam_entry.insert(0, d.get("diam", ""))
            if hasattr(m, 'qty_entry'):
                m.qty_entry.delete(0, 'end')
                m.qty_entry.insert(0, d.get("qty", ""))
            
            # Obsługa powłoki i wymuszenie odpalenia on_coating_change żeby pokazać pole L
            if hasattr(m, 'coat_combo'): 
                m.coat_combo.set(d.get("coat_name", "Brak"))
                m.on_coating_change() # Odkrywa pole długości (L) jeśli powłoka to nie "Brak"
                if d.get("coat_name") != "Brak" and hasattr(m, 'len_combo'):
                    m.len_combo.set(d.get("coat_len", "100"))
                    
            if hasattr(m, 'shank_entry'):
                m.shank_entry.configure(state="normal")
                m.shank_entry.delete(0, 'end')
                m.shank_entry.insert(0, d.get("shank_diam", d.get("diam", "")))
                # Jeśli średnica chwytu różni się od roboczej, zaznaczamy override
                if d.get("shank_diam") and d.get("shank_diam") != d.get("diam"):
                    m.shank_override.set(True)
                m.toggle_shank()

            # Przywracanie zaznaczenia checkboxów usług dodatkowych
            status = d.get("services_status", {})
            for key in m.service_vars:
                if key in status:
                    m.service_vars[key].set(status[key])
                    
        except Exception as e:
            print(f"Błąd ładowania danych do formularza edycji: {e}")

    def update_calculation(self, _=None):
        """Aktualizuje podgląd cen w formacie: Jednostkowa / Suma."""
        if not self.tool_module: return
        
        data = self.tool_module.get_full_item_data(run_validation=False)
        
        if data:
            try:
                t_j = data.get("tool_unit", 0.0)    
                t_r = data.get("total_tool", 0.0)   
                
                c_j = data.get("coat_unit", 0.0)    
                c_r = data.get("total_coat", 0.0)   
                
                e_j = data.get("extra_unit", 0.0)   
                e_r = data.get("total_extra", 0.0)  
                
                # Aktualizacja etykiet w formacie "Jednostkowa / Suma"
                self.price_labels["tool_price"].configure(text=f"{t_j:.2f} / {t_r:.2f} zł")
                
                if c_r > 0:
                    self.price_labels["coat_price"].configure(text=f"{c_j:.2f} / {c_r:.2f} zł")
                else:
                    self.price_labels["coat_price"].configure(text="---", text_color="gray")

                if e_r > 0:
                    self.price_labels["extra_price"].configure(text=f"{e_j:.2f} / {e_r:.2f} zł")
                else:
                    self.price_labels["extra_price"].configure(text="---", text_color="gray")

                total_final = t_r + c_r + e_r
                self.price_labels["total_price"].configure(text=f"{total_final:.2f} zł", text_color="#28a745")
                
            except Exception as ex:
                print(f"Błąd odświeżania podglądu: {ex}")
                self.price_labels["total_price"].configure(text="Błąd danych", text_color="red")
        else:
            for lbl in self.price_labels.values():
                lbl.configure(text="---", text_color="gray")

    def add_to_cart(self):
        """Standardowe dodawanie nowego rekordu."""
        item_data = self.tool_module.get_full_item_data(run_validation=True)
        if item_data:
            # Zapisujemy kategorię do słownika, żeby przy edycji wiedzieć jaki moduł załadować
            item_data["tool_category"] = self.tool_category
            item_data["shank_diam"] = self.tool_module.shank_entry.get()
            item_data["notes"] = ""
            
            for key in ["tool_unit", "total_tool", "coat_unit", "total_coat", "extra_unit", "total_extra"]:
                if key in item_data:
                    item_data[key] = round(float(item_data[key]), 2)
                    
            self.parent.add_item_to_cart(item_data)
            OstrzomatPopup(
                self, 
                title="Sukces", 
                message=f"Narzędzie {item_data['type']} Ø{item_data['diam']} zostało dodane do koszyka!",
                type="info"
            )
            

    def save_changes(self):
        """Zapisuje zaktualizowane dane pod istniejący indeks (Tryb Edycji)."""
        item_data = self.tool_module.get_full_item_data(run_validation=True)
        if item_data and self.item_index is not None:
            # Zachowujemy kategorię i dane chwytu
            item_data["tool_category"] = self.tool_category
            item_data["shank_diam"] = self.tool_module.shank_entry.get()
            
            # Wywołujemy nową metodę aktualizacji w OstrzomatApp
            self.parent.update_item_in_cart(self.item_index, item_data)
            
            OstrzomatPopup(
                self.parent, 
                title="Sukces", 
                message=f"Pozycja L.p. {self.item_index + 1} została pomyślnie zaktualizowana!",
                type="info"
            )
            self.destroy()