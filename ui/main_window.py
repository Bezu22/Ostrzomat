import customtkinter as ctk
from tkinter import messagebox, filedialog
import database as database
from ui.cart_table import CartTable
from ui.cart_footer import CartFooter
from ui.calc_window import ToolCalcWindow
from ui.price_editor import PriceEditor

class OstrzomatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ostrzomat v0.2")
        
        # Uruchamianie na pełnym ekranie
        self.minsize(1450, 800)
        self.after(0, lambda: self.state('zoomed'))

        # Dane aplikacji
        self.cart_items = []

        # --- UKŁAD GŁÓWNY ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200)
        self.sidebar_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # 1. Nagłówek Klienta
        self.client_frame = ctk.CTkFrame(self.content_frame, height=60)
        self.client_frame.pack(fill="x", pady=(0, 10))
        self.client_name = ctk.CTkLabel(self.client_frame, text="Nieokreślony klient", font=("Arial", 16, "bold"))
        self.client_name.pack(side="left", padx=20, pady=15)

        # 2. Tabela (Nowy komponent)
        self.cart_table = CartTable(self.content_frame)
        self.cart_table.pack(fill="both", expand=True)

        # 3. Stopka (Nowy komponent - przekazujemy funkcje do przycisków)
        self.cart_footer = CartFooter(
            self.content_frame, 
            on_save=self.manual_save_cart, 
            on_load=self.manual_load_cart, 
            on_clear=self.clear_cart
        )
        self.cart_footer.pack(fill="x", pady=(10, 0))

        # --- PRZYCISKI SIDEBAR ---
        self.btn_frez = ctk.CTkButton(self.sidebar_frame, text="➕ DODAJ FREZ", command=lambda: self.open_calc("Frezy"))
        self.btn_frez.pack(pady=20, padx=20, fill="x")

        self.edit_price_btn = ctk.CTkButton(self.sidebar_frame, text="⚙ CENNIK", fg_color="#444", command=self.open_price_editor)
        self.edit_price_btn.pack(side="bottom", fill="x", padx=20, pady=20)

        # Wczytanie cache przy starcie
        self.load_initial_data()

    def load_initial_data(self):
        """Ładowanie danych z ostatniej sesji."""
        client_cache, items_cache = database.load_cart_from_file() 
        self.cart_items = items_cache 
        self.client_name.configure(text=client_cache)
        self.refresh_cart_ui()

    def refresh_cart_ui(self):
        """Aktualizuje tabelę i stopkę."""
        self.cart_table.refresh(self.cart_items)
        
        # Obliczanie sumy całkowitej
        total = 0.0
        for item in self.cart_items:
            def clean_val(k):
                return float(str(item.get(k, "0")).replace(' zł', '').replace(',', '.').strip())
            
            total += clean_val("total_tool") + clean_val("total_coat") + clean_val("total_extra")
        
        self.cart_footer.update_total(total)

    def add_item_to_cart(self, item):
        """Publiczna metoda dla okien potomnych (np. CalcWindow)."""
        self.cart_items.append(item)
        self.refresh_cart_ui()
        database.save_cart_to_file(self.cart_items, self.client_name.cget("text"))

    def manual_save_cart(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Projekt Ostrzomat", "*.json")], initialdir="data")
        if path:
            database.save_cart_to_file(self.cart_items, self.client_name.cget("text"), path)
            messagebox.showinfo("Zapis", "Projekt zapisany pomyślnie.")

    def manual_load_cart(self):
        path = filedialog.askopenfilename(filetypes=[("Projekt Ostrzomat", "*.json")], initialdir="data")
        if path:
            client, items = database.load_cart_from_file(path)
            self.cart_items = items
            self.client_name.configure(text=client)
            self.refresh_cart_ui()
            database.save_cart_to_file(items, client)

    def clear_cart(self):
        if messagebox.askyesno("Czyszczenie", "Czy na pewno wyczyścić cały koszyk?"):
            self.cart_items = []
            self.refresh_cart_ui()
            database.save_cart_to_file([], "Nieokreślony klient")

    def open_price_editor(self):
        if not hasattr(self, "editor_window") or not self.editor_window.winfo_exists():
            self.editor_window = PriceEditor(self)
        else: self.editor_window.focus()

    def open_calc(self, category):
        ToolCalcWindow(self, category)