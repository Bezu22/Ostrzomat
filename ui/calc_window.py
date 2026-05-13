import customtkinter as ctk
from tkinter import messagebox
import database
from ui.calc_modules.frez_module import FrezModule

class ToolCalcWindow(ctk.CTkToplevel):
    def __init__(self, parent, tool_category="Frezy"):
        super().__init__(parent)
        self.parent = parent
        self.tool_category = tool_category
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
            self.update_calculation()
        else:
            ctk.CTkLabel(self.main_scroll, text="Błąd ładowania modułu").pack()
    
    def setup_price_preview(self):
        """Tworzy sekcję wyświetlającą ceny przed dodaniem do koszyka."""
        self.preview_frame = ctk.CTkFrame(self.main_scroll, fg_color=["#EBEBEB", "#2B2B2B"])
        self.preview_frame.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(self.preview_frame, text="PODGLĄD KOSZTÓW", font=("Arial", 13, "bold")).pack(pady=5)
        
        # Słownik na etykiety, żeby łatwo je aktualizować
        self.price_labels = {}
        fields = [
            ("Ostrzenie:", "tool_price"),
            ("Powlekanie:", "coat_price"),
            ("Usługi dodatkowe:", "extra_price"),
            ("SUMA JEDNOSTKOWA:", "total_price")
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

        self.add_btn = ctk.CTkButton(btn_frame, text="DODAJ DO KOSZYKA", 
                                     height=50, font=("Arial", 14, "bold"), 
                                     fg_color="#28a745", command=self.add_to_cart)
        self.add_btn.pack(fill="x", pady=5)

        self.close_btn = ctk.CTkButton(btn_frame, text="ZAMKNIJ", 
                                      height=40, fg_color="#666", command=self.destroy)
        self.close_btn.pack(fill="x", pady=5)

    def update_calculation(self, _=None):
        """Pobiera dane z modułu i aktualizuje etykiety podglądu."""
        if not self.tool_module: return
        
        data = self.tool_module.get_full_item_data()
        if data:
            # Wyciągamy wartości jednostkowe (tool_unit, total_coat, total_extra)
            # Uwaga: dane w słowniku są sformatowane jako stringi "0.00 zł"
            self.price_labels["tool_price"].configure(text=data["tool_unit"])
            self.price_labels["coat_price"].configure(text=data["total_coat"])
            self.price_labels["extra_price"].configure(text=data["total_extra"])
            
            # Obliczamy sumę jednostkową do podglądu
            try:
                t = float(data["tool_unit"].split()[0])
                c = float(data["total_coat"].split()[0])
                e = float(data["total_extra"].split()[0])
                self.price_labels["total_price"].configure(text=f"{(t+c+e):.2f} zł", text_color="#28a745")
            except:
                pass
        else:
            for lbl in self.price_labels.values():
                lbl.configure(text="---", text_color="gray")

    def add_to_cart(self):
        item_data = self.tool_module.get_full_item_data()
        if item_data:
            self.parent.add_item_to_cart(item_data)
            messagebox.showinfo("Ostrzomat", "Dodano narzędzie do koszyka!")
        else:
            messagebox.showerror("Błąd", "Sprawdź poprawność wprowadzonych danych.")

    def add_to_cart(self):
        # Pobieramy pełne dane przygotowane przez moduł
        item_data = self.tool_module.get_full_item_data()
        
        if item_data:
            self.parent.add_item_to_cart(item_data)
            messagebox.showinfo("Ostrzomat", "Narzędzie zostało dodane do koszyka!")
        else:
            messagebox.showerror("Błąd", "Nie udało się obliczyć ceny. Sprawdź poprawność danych (liczby!).")