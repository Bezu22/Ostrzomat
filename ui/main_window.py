import customtkinter as ctk
from tkinter import messagebox,filedialog
import database
import sys, os
from ui.price_editor import PriceEditor
from ui.calc_window import ToolCalcWindow

class OstrzomatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ostrzomat 0.2")
        self.geometry("1450x850")

        # Inicjalizacja listy koszyka
        self.basket_items = []

        # --- MONITOROWANIE BAZY ---
        self.error_bar = ctk.CTkFrame(self, fg_color="#b22222", height=40)
        self.error_label = ctk.CTkLabel(self.error_bar, text="BRAK BAZY DANYCH! Sprawdź folder 'data'.", text_color="white")
        self.error_label.pack(pady=5)
        self.is_monitoring = False
        
        # --- UKŁAD GŁÓWNY ---
        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200)
        self.sidebar_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Main Content Area
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # --- 1. GÓRA: KLIENT ---
        self.client_frame = ctk.CTkFrame(self.content_frame, height=60)
        self.client_frame.pack(fill="x", pady=(0, 10))
        self.client_title = ctk.CTkLabel(self.client_frame, text="KLIENT: ", font=("Arial", 16, "bold"))
        self.client_title.pack(side="left", padx=20, pady=15)
        self.client_name = ctk.CTkLabel(self.client_frame, text="Nieokreślony (kliknij, aby edytować)", font=("Arial", 16), text_color="gray")
        self.client_name.pack(side="left", pady=15)

        # --- 2. ŚRODEK: TABELA KOSZYKA ---
        self.basket_frame = ctk.CTkFrame(self.content_frame)
        self.basket_frame.pack(fill="both", expand=True)

        self.setup_table_headers()

        self.items_scroll_frame = ctk.CTkScrollableFrame(self.basket_frame, fg_color="transparent")
        self.items_scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # --- 3. DÓŁ: PODSUMOWANIE I AKCJE ---
        self.footer_frame = ctk.CTkFrame(self.content_frame, height=150) # Zwiększona wysokość na 3 przyciski
        self.footer_frame.pack(fill="x", pady=(10, 0))

        # Suma po prawej
        self.total_label = ctk.CTkLabel(self.footer_frame, text="ŁĄCZNIE DO ZAPŁATY: 0.00 zł", font=("Arial", 22, "bold"), text_color="#28a745")
        self.total_label.pack(side="right", padx=40, pady=20)

        # Kontener na przyciski po lewej
        self.actions_container = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        self.actions_container.pack(side="left", padx=20, pady=10)
        
        # Przyciski jeden pod drugim (pack bez side="left" układa pionowo)
        self.btn_save_project = ctk.CTkButton(self.actions_container, text="ZAPISZ KOSZYK", 
                                             fg_color="#1f538d", command=self.manual_save_basket)
        self.btn_save_project.pack(pady=5, fill="x")

        self.btn_load_project = ctk.CTkButton(self.actions_container, text="WCZYTAJ KOSZYK", 
                                             fg_color="#444", command=self.manual_load_basket)
        self.btn_load_project.pack(pady=5, fill="x")

        self.btn_clear = ctk.CTkButton(self.actions_container, text="WYCZYŚĆ KOSZYK", 
                                       fg_color="#c0392b", hover_color="#a93226", command=self.clear_basket)
        self.btn_clear.pack(pady=5, fill="x")

        # --- SIDEBAR BUTTONS ---
        self.btn_frez = ctk.CTkButton(self.sidebar_frame, text="➕ DODAJ FREZ", command=lambda: self.open_calc("Frezy"))
        self.btn_frez.pack(pady=20, padx=20, fill="x")

        self.btn_oferta = ctk.CTkButton(self.sidebar_frame, text="📄 GENERUJ OFERTĘ", fg_color="#28a745")
        self.btn_oferta.pack(pady=10, padx=20, fill="x")

        self.edit_price_btn = ctk.CTkButton(self.sidebar_frame, text="⚙ USTAWIENIA CENNIKA", 
                                             fg_color="#444", hover_color="#666",
                                             command=self.open_price_editor)
        self.edit_price_btn.pack(side="bottom", fill="x", padx=20, pady=20)

        # --- LOGIKA STARTOWA ---
        # Wczytanie cache i odświeżenie UI
        client_cache, items_cache = database.load_basket_from_file()
        self.basket_items = items_cache
        self.client_name.configure(text=client_cache)
        self.refresh_basket_ui()

        self.check_initial_connection()

    def setup_table_headers(self):
        """Nowe nagłówki z uwzględnieniem parametrów technicznych."""
        h_frame = ctk.CTkFrame(self.basket_frame, fg_color="#333", height=35, corner_radius=0)
        h_frame.pack(fill="x")
        
        # Definicja kolumn: (Nazwa, Szerokość)
        # Z = Liczba ostrzy
        cols = [
            ("TYP NARZĘDZIA", 220), ("Ø", 60), ("Z", 40), ("SZT.", 50), 
            ("OSTRZENIE", 100), ("POWŁOKA", 120), ("L [mm]", 70), 
            ("POWŁ. JEDN.", 100), ("POWŁ. SUMA", 100), ("USŁUGI", 100), ("SUMA", 120)
        ]
        
        for text, width in cols:
            lbl = ctk.CTkLabel(h_frame, text=text, width=width, font=("Arial", 11, "bold"))
            lbl.pack(side="left", padx=5)

    def add_item_to_basket(self, item):
        """Odbiera dane, odświeża UI i aktualizuje cache."""
        self.basket_items.append(item)
        self.refresh_basket_ui()
        database.save_basket_to_file(self.basket_items) # Auto-save

    def clear_basket(self):
        if messagebox.askyesno("Czyszczenie", "Czy na pewno wyczyścić cały koszyk?"):
            self.basket_items = []
            self.refresh_basket_ui()
            database.save_basket_to_file(self.basket_items) # Czyści też cache

    def manual_save_basket(self):
        """Ręczny zapis do pliku wybranego przez usera."""
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Pliki wyceny", "*.json")],
            initialdir="data",
            title="Zapisz wycenę jako..."
        )
        if path:
            database.save_basket_to_file(self.basket_items, path)
            messagebox.showinfo("Sukces", "Koszyk został zapisany.")

    def manual_load_basket(self):
        """Ręczny odczyt z pliku wybranego przez usera."""
        path = filedialog.askopenfilename(
            filetypes=[("Pliki wyceny", "*.json")],
            initialdir="data"
        )
        if path:
            loaded_data = database.load_basket_from_file(path)
            if loaded_data:
                self.basket_items = loaded_data
                self.refresh_basket_ui()
                database.save_basket_to_file(self.basket_items) # Aktualizuje cache bieżący      

    def refresh_basket_ui(self):
        """Odświeża widok tabeli koszyka z wycentrowanymi danymi i czystszą powłoką."""
        for widget in self.items_scroll_frame.winfo_children():
            widget.destroy()

        grand_total = 0.0

        for idx, item in enumerate(self.basket_items):
            bg_color = "#2b2b2b" if idx % 2 == 0 else "#333"
            row = ctk.CTkFrame(self.items_scroll_frame, fg_color=bg_color, height=40, corner_radius=5)
            row.pack(fill="x", pady=2)

            # Pomocnicza funkcja do sumowania
            def to_float(val):
                if not val: return 0.0
                try: return float(str(val).replace(' zł', '').replace(',', '.').strip())
                except: return 0.0

            line_total = to_float(item["total_tool"]) + to_float(item["total_coat"]) + to_float(item["total_extra"])
            grand_total += line_total

            # Przygotowanie tekstów dla powłoki (zamiana 0.00 zł na myslnik)
            has_coating = item.get("coat_name") != "Brak"
            c_unit = item.get("coat_unit", "-") if has_coating and to_float(item.get("coat_unit")) > 0 else "-"
            c_total = item.get("total_coat", "-") if has_coating and to_float(item.get("total_coat")) > 0 else "-"
            c_len = item.get("coat_len", "-") if has_coating else "-"

            # --- RENDEROWANIE KOLUMN ---
            # 1. Typ Narzędzia (wyrównany do lewej dla czytelności)
            ctk.CTkLabel(row, text=item.get("type", "-"), width=220, anchor="w").pack(side="left", padx=5)
            
            # 2. Parametry techniczne (Centrowanie: anchor="center")
            ctk.CTkLabel(row, text=item.get("diam", "-"), width=60, anchor="center").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=item.get("z", "-"), width=40, anchor="center").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=item.get("qty", "-"), width=50, anchor="center").pack(side="left", padx=5)
            
            # 3. Ceny ostrzenia
            ctk.CTkLabel(row, text=item.get("tool_unit", "-"), width=100, anchor="center").pack(side="left", padx=5)
            
            # 4. Dane powłoki (z myślnikami zamiast zer)
            ctk.CTkLabel(row, text=item.get("coat_name", "Brak"), width=120, anchor="center").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=c_len, width=70, anchor="center").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=c_unit, width=100, anchor="center").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=c_total, width=100, anchor="center").pack(side="left", padx=5)
            
            # 5. Usługi i suma końcowa
            ctk.CTkLabel(row, text=item.get("extra_unit", "-") if to_float(item.get("extra_unit")) > 0 else "-", 
                         width=100, anchor="center").pack(side="left", padx=5)
            
            ctk.CTkLabel(row, text=f"{line_total:.2f} zł", width=120, font=("Arial", 12, "bold"), 
                         text_color="#3498db", anchor="center").pack(side="left", padx=5)

        self.total_label.configure(text=f"ŁĄCZNIE DO ZAPŁATY: {grand_total:.2f} zł")

    
    def check_initial_connection(self):
        if not database.is_db_accessible(): self.show_connection_error()

    def show_connection_error(self):
        if not self.is_monitoring:
            self.error_bar.pack(fill="x", side="top")
            self.is_monitoring = True
            self.check_loop()

    def check_loop(self):
        if database.is_db_accessible():
            self.error_bar.pack_forget()
            self.is_monitoring = False
        else:
            self.after(5000, self.check_loop)

    def open_price_editor(self):
        try:
            database.get_connection().close()
            if not hasattr(self, "editor_window") or not self.editor_window.winfo_exists():
                self.editor_window = PriceEditor(self)
            else: self.editor_window.focus()
        except: self.show_connection_error()

    def open_calc(self, category):
        ToolCalcWindow(self, category)