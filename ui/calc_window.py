import customtkinter as ctk
from tkinter import messagebox
import database as database
from logic import cart_logic
from ui.calc_modules.frez_module import FrezModule

class ToolCalcWindow(ctk.CTkToplevel):
    def __init__(self, parent, tool_category="Frezy"):
        super().__init__(parent)
        self.parent = parent
        self.tool_category = tool_category
        self.title(f"Konfiguracja: {tool_category}")
        self.geometry("550x950")
        
        self.attributes("-topmost", True)
        self.grab_set()

        self.settings = database.get_user_settings()
        
        self.main_scroll = ctk.CTkScrollableFrame(self)
        self.main_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # --- 1. MODUŁ NARZĘDZIA ---
        if tool_category == "Frezy":
            # Przekazujemy self, aby moduł mógł czytać parametry z okna głównego (np. średnicę)
            self.tool_module = FrezModule(self.main_scroll, self.update_calculation, self.settings, self)
            self.tool_module.pack(fill="x", padx=30, pady=(10, 20))
        
        # --- 2. WSPÓLNE PARAMETRY ---
        self.setup_common_ui()
        self.update_calculation()

    def setup_common_ui(self):
        f_bold = ("Arial", 12, "bold")
        px = 30
        
        last_diam = self.settings.get("last_diam", "10.0")
        
        self.diam_label = ctk.CTkLabel(self.main_scroll, text="Średnica robocza (Ø):", font=f_bold)
        self.diam_label.pack(padx=px, anchor="w")
        
        self.diam_entry = ctk.CTkEntry(self.main_scroll, width=280)
        self.diam_entry.insert(0, last_diam) # Wstawiamy z cache
        self.diam_entry.pack(pady=(0, 10), padx=px, anchor="w")
        self.diam_entry.bind("<KeyRelease>", self.on_diam_change)

        # Ilość sztuk
        ctk.CTkLabel(self.main_scroll, text="Ilość sztuk:", font=f_bold).pack(padx=px, anchor="w")
        self.qty_entry = ctk.CTkEntry(self.main_scroll, width=280)
        self.qty_entry.insert(0, "1")
        self.qty_entry.pack(pady=(0, 10), padx=px, anchor="w")
        self.qty_entry.bind("<KeyRelease>", self.update_calculation)

        # Usługi dodatkowe
        ctk.CTkLabel(self.main_scroll, text="Usługi dodatkowe:", font=f_bold).pack(padx=px, pady=(10, 5), anchor="w")
        self.service_vars = {
            "ciecie": ctk.BooleanVar(),
            "opuszczenie": ctk.BooleanVar(),
            "polerowanie": ctk.BooleanVar()
        }
        serv_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        serv_frame.pack(fill="x", padx=px)
        
        for k, v in self.service_vars.items():
            cb_text = "Cięcie" if k == "ciecie" else "Zaniżenie" if k == "opuszczenie" else "Polerowanie"
            ctk.CTkCheckBox(serv_frame, text=cb_text, variable=v, command=self.update_calculation, font=("Arial", 11)).pack(side="left", padx=(0, 15))

        # Powłoka
        ctk.CTkLabel(self.main_scroll, text="Powłoka:", font=f_bold).pack(padx=px, pady=(15, 0), anchor="w")
        self.coat_combo = ctk.CTkComboBox(self.main_scroll, width=280, 
                                          values=["Brak"] + database.get_unique_coating_names(), 
                                          command=self.on_coat_change)
        self.coat_combo.set("Brak")
        self.coat_combo.pack(padx=px, pady=5, anchor="w")
        
        self.len_combo = ctk.CTkComboBox(self.main_scroll, width=280, values=["100"], command=self.update_calculation)

        # Sekcja wyników
        self.res_frame = ctk.CTkFrame(self.main_scroll, fg_color="#222", corner_radius=10)
        self.res_frame.pack(fill="x", padx=px, pady=25)
        
        self.res_tool = ctk.CTkLabel(self.res_frame, text="", font=("Arial", 16, "bold"), text_color="#28a745")
        self.res_tool.pack(pady=(10, 5))
        self.res_extra = ctk.CTkLabel(self.res_frame, text="", font=("Arial", 12), text_color="#3498db")
        self.res_extra.pack(pady=2)
        self.res_coat = ctk.CTkLabel(self.res_frame, text="", font=("Arial", 12), text_color="#f1c40f")
        self.res_coat.pack(pady=(2, 10))

        self.add_btn = ctk.CTkButton(self.main_scroll, text="DODAJ DO KOSZYKA (CART)", 
                                     height=55, font=("Arial", 14, "bold"), 
                                     fg_color="#1f538d", command=self.add_to_cart)
        self.add_btn.pack(fill="x", padx=px, pady=20)

    def on_diam_change(self, event=None):
        """Specjalna funkcja: przy zmianie średnicy aktualizuje obliczenia ORAZ chwyt w module."""
        if hasattr(self, 'tool_module') and hasattr(self.tool_module, 'sync_shank_with_diam'):
            self.tool_module.sync_shank_with_diam()
        self.update_calculation()

    def on_coat_change(self, choice):
        """Obsługa dynamicznego pojawiania się wyboru długości powłoki."""
        if choice != "Brak":
            lengths = database.get_coating_lengths(choice)
            self.len_combo.configure(values=lengths)
            self.len_combo.set("100" if "100" in lengths else lengths[0])
            self.len_combo.pack(padx=30, pady=5, anchor="w", after=self.coat_combo)
        else:
            self.len_combo.pack_forget()
        self.update_calculation()

    def validate(self):
        """Sprawdza czy dane wejściowe są liczbami."""
        try:
            float(self.diam_entry.get().replace(',', '.'))
            int(self.qty_entry.get())
            return True
        except:
            return False

    def update_calculation(self, _=None):
        """Łączy dane z modułu narzędzia i pól wspólnych, oblicza cenę w czasie rzeczywistym."""
        if not self.validate():
            self.res_tool.configure(text="BŁĘDNE DANE", text_color="#e74c3c")
            self.res_extra.configure(text="")
            self.res_coat.configure(text="")
            return

        t_data = self.tool_module.get_data()
        diam = self.diam_entry.get().replace(',', '.')
        qty = self.qty_entry.get()
        
        # Obliczenia z Logic Engine
        p_u, p_total = cart_logic.calculate_tool_price(t_data['type'], t_data['z'], diam, qty)
        e_u, e_total, labs = cart_logic.calculate_extra_services(self.service_vars, diam, qty)
        
        coat = self.coat_combo.get()
        c_u, c_total = 0.0, 0.0
        if coat != "Brak":
            c_u, c_total = cart_logic.calculate_coating_price(coat, diam, self.len_combo.get(), qty)

        # Aktualizacja UI
        self.res_tool.configure(text=f"OSTRZENIE: {p_total:.2f} zł", text_color="#28a745")
        self.res_extra.configure(text=f"USŁUGI ({', '.join(labs)}): +{e_total:.2f} zł" if labs else "")
        self.res_coat.configure(text=f"POWŁOKA ({coat}): +{c_total:.2f} zł" if c_total > 0 else "")

    def add_to_cart(self):
        """Pakuje dane, zapisuje ustawienia do cache i przesyła do okna głównego."""
        if not self.validate():
            messagebox.showerror("Błąd", "Popraw dane przed dodaniem!")
            return

        # 1. Pobieranie danych z pól i modułów
        t_data = self.tool_module.get_data()
        diam = self.diam_entry.get().replace(',', '.')
        qty = self.qty_entry.get()
        coat_name = self.coat_combo.get()
        coat_len = self.len_combo.get() if coat_name != "Brak" else "100"
        
        # 2. Obliczanie finalnych cen przez logic engine
        p_u, p_t = cart_logic.calculate_tool_price(t_data['type'], t_data['z'], diam, qty)
        c_u, c_t = cart_logic.calculate_coating_price(coat_name, diam, coat_len, qty)
        e_u, e_t, _ = cart_logic.calculate_extra_services(self.service_vars, diam, qty)

        # 3. AKTUALIZACJA CACHE (Zapisujemy to, co user właśnie wybrał)
        new_settings = {
            "last_tool_type": t_data['type'],
            "last_blades": t_data['z'],
            "last_diam": diam,
            "last_shank": t_data.get('shank', diam) # Zapisujemy chwyt jeśli moduł go posiada
        }
        database.save_user_settings(new_settings)

        # 4. Przygotowanie obiektu pozycji do koszyka (Item)
        item = {
            "type": t_data['type'],
            "diam": diam,
            "z": t_data['z'],
            "qty": qty,
            "tool_unit": f"{p_u:.2f} zł",
            "total_tool": f"{p_t:.2f} zł",
            "coat_name": coat_name,
            "coat_len": coat_len if coat_name != "Brak" else "-",
            "total_coat": f"{c_t:.2f} zł",
            "services_status": {k: v.get() for k, v in self.service_vars.items()},
            "total_extra": f"{e_t:.2f} zł"
        }
        
        # 5. Przesłanie do głównego okna i zamknięcie kalkulatora
        self.parent.add_item_to_cart(item)
        self.destroy()