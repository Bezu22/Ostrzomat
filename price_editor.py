import customtkinter as ctk
from tkinter import messagebox
import database  # Upewnij się, że plik database.py jest w tym samym folderze

class PriceEditor(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Zarządzanie Cennikiem - Tryb Edycji")
        self.geometry("1150x750")
        self.attributes("-topmost", True)
        
        # Zmienne stanu
        self.selected_row_data = None
        self.selected_frame = None

        # --- PANEL GÓRNY (FILTRY I AKCJE) ---
        self.top_bar = ctk.CTkFrame(self)
        self.top_bar.pack(fill="x", padx=10, pady=10)

        # Filtrowanie
        ctk.CTkLabel(self.top_bar, text="Filtruj typ:").pack(side="left", padx=10)
        
        # Pobieramy typy z bazy
        try:
            tool_types = ["Wszystkie"] + database.get_unique_tool_types()
        except:
            tool_types = ["Wszystkie"]

        self.combo_filter = ctk.CTkComboBox(self.top_bar, 
                                           values=tool_types, 
                                           command=self.refresh_list)
        self.combo_filter.set("Wszystkie")
        self.combo_filter.pack(side="left", padx=5)

        # Przycisk EDYTUJ
        self.btn_edit = ctk.CTkButton(self.top_bar, text="EDYTUJ", state="disabled", 
                                      width=100, fg_color="#1f538d", command=self.open_edit_form)
        self.btn_edit.pack(side="left", padx=10)

        # Przycisk USUŃ
        self.btn_delete = ctk.CTkButton(self.top_bar, text="USUŃ", state="disabled", 
                                        width=100, fg_color="#dc3545", hover_color="#c82333",
                                        command=self.delete_top_action)
        self.btn_delete.pack(side="left", padx=10)

        # Przycisk DODAJ
        ctk.CTkButton(self.top_bar, text="+ DODAJ NOWE", fg_color="#28a745", hover_color="#218838",
                      command=lambda: self.open_edit_form(None)).pack(side="right", padx=10)

        # --- NAGŁÓWKI ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(10, 0))
        headers = [("Typ", 180), ("Ostrza", 100), ("Ø Min", 80), ("Ø Max", 80), 
                   ("1 szt", 80), ("2-4 szt", 80), ("5-10 szt", 80), ("11+ szt", 80)]
        
        for text, width in headers:
            ctk.CTkLabel(self.header_frame, text=text, font=("Arial", 12, "bold"), 
                         width=width, anchor="w").pack(side="left", padx=5)

        # --- LISTA (SCROLL) ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#1a1a1a")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Pierwsze ładowanie listy
        self.refresh_list()

    def refresh_list(self, _=None):
        """Pobiera dane i renderuje listę z efektem zebry."""
        # Reset stanu zaznaczenia przed czyszczeniem
        self.selected_row_data = None
        self.selected_frame = None
        self.btn_edit.configure(state="disabled")
        self.btn_delete.configure(state="disabled")

        # Czyszczenie listy
        for child in list(self.scroll_frame.winfo_children()):
            child.destroy()
        
        # Pobieranie danych z bazy
        selected_type = self.combo_filter.get()
        data = database.get_filtered_prices(selected_type)
        
        # Renderowanie wierszy
        for index, row in enumerate(data):
            is_even = index % 2 == 0
            self.render_row_item(row, is_even)

    def render_row_item(self, row, is_even):
        """Tworzy wiersz z naprzemiennym tłem."""
        bg_color = "transparent" if is_even else "#2b2b2b"
        
        row_frame = ctk.CTkFrame(self.scroll_frame, fg_color=bg_color, corner_radius=0)
        row_frame.pack(fill="x", pady=0, padx=5)
        row_frame.original_bg = bg_color

        widths = [180, 100, 80, 80, 80, 80, 80, 80]
        # row[1:] pomija ID przy wyświetlaniu
        for i, val in enumerate(row[1:]):
            lbl = ctk.CTkLabel(row_frame, text=str(val), width=widths[i], anchor="w")
            lbl.pack(side="left", padx=5, pady=4)
            lbl.bind("<Button-1>", lambda e, r=row, f=row_frame: self.on_row_select(r, f))

        row_frame.bind("<Button-1>", lambda e, r=row, f=row_frame: self.on_row_select(r, f))

    def on_row_select(self, row_data, frame):
        """Podświetla wiersz i aktywuje przyciski."""
        try:
            if self.selected_frame and self.selected_frame.winfo_exists():
                self.selected_frame.configure(fg_color=self.selected_frame.original_bg)
        except:
            pass
        
        self.selected_row_data = row_data
        self.selected_frame = frame
        
        if self.selected_frame.winfo_exists():
            self.selected_frame.configure(fg_color="#1f538d") 
            self.btn_edit.configure(state="normal")
            self.btn_delete.configure(state="normal")

    def delete_top_action(self):
        """Usuwanie z głównego panelu."""
        if self.selected_row_data:
            msg = f"Czy na pewno chcesz usunąć:\n{self.selected_row_data[1]} (Ø{self.selected_row_data[3]}-{self.selected_row_data[4]})?"
            if messagebox.askyesno("Potwierdzenie", msg):
                database.delete_price_row(self.selected_row_data[0])
                self.refresh_list()
                messagebox.showinfo("Sukces", "Pozycja została usunięta.")

    def open_edit_form(self, existing_data=None):
        """Otwiera wysoki formularz edycji."""
        data = existing_data if existing_data else self.selected_row_data
        
        form = ctk.CTkToplevel(self)
        form.title("Edycja" if data else "Nowa Pozycja")
        form.geometry("450x750")
        form.attributes("-topmost", True)
        form.grab_set()

        labels = ["Typ narzędzia", "Ilość ostrzy", "Średnica MIN", "Średnica MAX", 
                  "Cena (1)", "Cena (2-4)", "Cena (5-10)", "Cena (11-20)"]
        entries = []

        for i, txt in enumerate(labels):
            ctk.CTkLabel(form, text=txt, font=("Arial", 12, "bold")).pack(pady=(15, 0))
            if txt == "Ilość ostrzy":
                ctk.CTkLabel(form, text="(np. '2-4', '6' lub 'pozostałe')", 
                            font=("Arial", 10), text_color="gray").pack()
            
            e = ctk.CTkEntry(form, width=300)
            if data:
                e.insert(0, str(data[i+1]))
            e.pack(pady=5)
            entries.append(e)

        def save_action():
            try:
                new_vals = [e.get().replace(',', '.') for e in entries]
                if data:
                    database.update_price_row(data[0], new_vals)
                else:
                    database.add_price_row(new_vals)
                form.destroy()
                self.refresh_list()
                messagebox.showinfo("Sukces", "Zapisano pomyślnie.")
            except Exception as ex:
                messagebox.showerror("Błąd", f"Błąd zapisu: {ex}")

        ctk.CTkButton(form, text="ZAPISZ I ZAMKNIJ", fg_color="#28a745", height=45,
                      command=save_action).pack(pady=40)