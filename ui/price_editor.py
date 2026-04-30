import customtkinter as ctk
from tkinter import messagebox
import database

class PriceEditor(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Zarządzanie Cennikami Ostrzomat 2.0")
        self.geometry("1200x800")
        self.attributes("-topmost", True)
        
        self.selected_row_data = None
        self.selected_frame = None

        # --- PANEL GÓRNY ---
        self.top_bar = ctk.CTkFrame(self)
        self.top_bar.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(self.top_bar, text="Kategoria:").pack(side="left", padx=5)
        self.main_cat_combo = ctk.CTkComboBox(self.top_bar, values=["Narzędzia", "Powłoki", "Usługi"], command=self.on_main_cat_change)
        self.main_cat_combo.set("Narzędzia")
        self.main_cat_combo.pack(side="left", padx=5)

        ctk.CTkLabel(self.top_bar, text="Filtr:").pack(side="left", padx=5)
        self.sub_filter_combo = ctk.CTkComboBox(self.top_bar, values=["Wszystkie"], command=self.refresh_list)
        self.sub_filter_combo.pack(side="left", padx=5)

        self.btn_edit = ctk.CTkButton(self.top_bar, text="EDYTUJ", state="disabled", width=100, command=self.open_edit_form)
        self.btn_edit.pack(side="left", padx=10)

        self.btn_delete = ctk.CTkButton(self.top_bar, text="USUŃ", state="disabled", fg_color="#dc3545", width=100, command=self.delete_action)
        self.btn_delete.pack(side="left", padx=5)

        # Naprawione: Jawne przekazanie None przy dodawaniu
        ctk.CTkButton(self.top_bar, text="+ DODAJ", fg_color="#28a745", width=100, command=lambda: self.open_edit_form(is_new=True)).pack(side="right", padx=10)

        # --- NAGŁÓWKI ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=5)

        # --- LISTA (SCROLLABLE) ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#1a1a1a")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.status_label = ctk.CTkLabel(self.top_bar, text="", text_color="#28a745", font=("Arial", 12, "bold"))
        self.status_label.pack(side="right", padx=20)
        
        self.on_main_cat_change()

    def on_main_cat_change(self, _=None):
        cat = self.main_cat_combo.get()
        if cat == "Narzędzia":
            vals = ["Wszystkie", "Frezy", "Wiertła", "Inne"]
            self.headers = [("Typ", 180), ("Ostrza", 100), ("Ø Min", 80), ("Ø Max", 80), ("1 szt", 80), ("2-4", 80), ("5-10", 80), ("11+", 80)]
        elif cat == "Powłoki":
            vals = ["Wszystkie"] + database.get_unique_coating_names()
            self.headers = [("Nazwa powłoki", 250), ("Ø Max", 120), ("Długość", 120), ("Cena", 120)]
        else:
            vals = ["Wszystkie"] + database.get_unique_service_names()
            self.headers = [("Nazwa usługi", 250), ("Param Min", 150), ("Param Max", 150), ("Cena", 120)]

        self.sub_filter_combo.configure(values=vals)
        self.sub_filter_combo.set("Wszystkie")
        
        for child in self.header_frame.winfo_children(): child.destroy()
        for text, width in self.headers:
            ctk.CTkLabel(self.header_frame, text=text, font=("Arial", 12, "bold"), width=width, anchor="w").pack(side="left", padx=5)
            
        self.refresh_list()

    def refresh_list(self, _=None):
        """Czyści listę w sposób bezpieczny dla silnika renderującego i ładuje dane."""
        self.selected_row_data = None
        self.btn_edit.configure(state="disabled")
        self.btn_delete.configure(state="disabled")
        
        # 1. Zatrzymujemy aktualizacje widoku na chwilę
        self.scroll_frame.update_idletasks()
        
        # 2. Bezpieczne usuwanie dzieci
        for child in self.scroll_frame.winfo_children():
            # Najpierw usuwamy z widoku, potem niszczymy obiekt
            child.pack_forget()
            child.destroy()
        
        # 3. Reset skrola
        self._parent_canvas = getattr(self.scroll_frame, "_parent_canvas", None)
        if self._parent_canvas:
            self._parent_canvas.yview_moveto(0)

        cat = self.main_cat_combo.get()
        filt = self.sub_filter_combo.get()

        # 4. Pobieranie danych (bez zmian)
        if cat == "Narzędzia":
            data = database.get_filtered_tools(filt, "Wszystkie")
            # 8 kolumn szerokości -> d_slice musi wycinać dokładnie 8 kolumn (od 2 do 10)
            col_widths, d_slice = [180, 100, 80, 80, 80, 80, 80, 80], slice(2, 10)
        elif cat == "Powłoki":
            data = database.get_filtered_coatings(filt)
            # 4 kolumny szerokości -> d_slice musi wycinać dokładnie 4 kolumny (od 1 do 5)
            col_widths, d_slice = [250, 120, 120, 120], slice(1, 5)
        else: # Usługi
            data = database.get_filtered_services(filt)
            # 4 kolumny szerokości -> d_slice musi wycinać dokładnie 4 kolumny (od 1 do 5)
            col_widths, d_slice = [250, 150, 150, 120], slice(1, 5)

        # 5. Renderowanie nowych wierszy
        for index, row in enumerate(data):
            self.render_row_item(row, index % 2 == 0, col_widths, d_slice)

    def render_row_item(self, row, is_even, widths, d_slice):
        bg = "transparent" if is_even else "#2b2b2b"
        f = ctk.CTkFrame(self.scroll_frame, fg_color=bg, corner_radius=0)
        f.pack(fill="x", pady=0, padx=5)
        f.original_bg = bg

        # Pobieramy wycinek danych z wiersza
        display_data = row[d_slice]
        
        # Upewniamy się, że nie kręcimy pętli więcej razy niż mamy zdefiniowanych szerokości
        limit = min(len(display_data), len(widths))

        for i in range(limit):
            val = display_data[i]
            lbl = ctk.CTkLabel(f, text=str(val), width=widths[i], anchor="w")
            lbl.pack(side="left", padx=5, pady=4)
            lbl.bind("<Button-1>", lambda e: self.on_row_select(row, f))
        
        f.bind("<Button-1>", lambda e: self.on_row_select(row, f))

    def on_row_select(self, data, frame):
        if self.selected_frame and self.selected_frame.winfo_exists():
            self.selected_frame.configure(fg_color=self.selected_frame.original_bg)
        self.selected_row_data = data
        self.selected_frame = frame
        self.selected_frame.configure(fg_color="#1f538d")
        self.btn_edit.configure(state="normal")
        self.btn_delete.configure(state="normal")

    def delete_action(self):
        cat = self.main_cat_combo.get()
        table = "pricelist_tools" if cat == "Narzędzia" else "pricelist_coatings" if cat == "Powłoki" else "pricelist_services"
        if messagebox.askyesno("Usuń", "Na pewno usunąć?"):
            database.delete_row(table, self.selected_row_data[0])
            self.refresh_list()

    def open_edit_form(self, is_new=False):
        """
        Otwiera formularz. 
        Jeśli is_new=True i coś jest zaznaczone, kopiuje dane do nowego wpisu.
        Jeśli is_new=False, edytuje istniejący rekord.
        """
        cat = self.main_cat_combo.get()
        
        # Logika wyboru danych:
        # Jeśli edytujemy -> bierzemy zaznaczone (data = self.selected_row_data)
        # Jeśli nowy -> bierzemy zaznaczone jako wzór, ale wyzerujemy ID w bazie
        data = self.selected_row_data 
        
        form = ctk.CTkToplevel(self)
        # Dynamiczny tytuł informujący o trybie pracy
        mode_text = "Nowy (na wzór)" if is_new and data else "Nowy" if is_new else "Edycja"
        form.title(f"{cat} - {mode_text}")
        form.geometry("500x850")
        form.attributes("-topmost", True)
        form.grab_set()

        # Definicje pól i poprawne indeksowanie kolumn z bazy danych
        if cat == "Narzędzia":
            # Wyświetlamy 9 pól. W bazie danych zaczynają się od indeksu 1 (category) do 9 (price_11_20)
            labels = ["Kategoria", "Typ narzędzia", "Ostrza", "Ø MIN", "Ø MAX", 
                      "Cena 1 szt.", "Cena 2-4 szt.", "Cena 5-10 szt.", "Cena 11-20 szt."]
            db_slice = slice(1, 10) # Pobiera kolumny o indeksach 1, 2, 3, 4, 5, 6, 7, 8, 9
        elif cat == "Powłoki":
            labels = ["Nazwa powłoki", "Ø MAX", "Długość", "Cena"]
            db_slice = slice(1, 5) # Pobiera kolumny 1, 2, 3, 4
        else: # Usługi
            labels = ["Nazwa usługi", "Param MIN", "Param MAX", "Cena"]
            db_slice = slice(1, 5) # Pobiera kolumny 1, 2, 3, 4

        entries = []
        for i, txt in enumerate(labels):
            ctk.CTkLabel(form, text=txt, font=("Arial", 12, "bold")).pack(pady=(10, 0))
            e = ctk.CTkEntry(form, width=350)
            
            # Wstawiamy dane jeśli edytujemy lub kopiujemy wzór
            if data:
                try:
                    # Pobieramy dane z wiersza bazy według ustalonego wyżej zakresu
                    row_content = data[db_slice]
                    e.insert(0, str(row_content[i]))
                except IndexError:
                    pass
            e.pack(pady=5)
            entries.append(e)

        def show_status(self, message, color="#28a745"):
            """Wyświetla krótki komunikat na froncie i ukrywa go po 3s."""
            self.status_label.configure(text=message, text_color=color)
            # self.after planuje wykonanie czyszczenia za 3000ms (3 sekundy)
            self.after(3000, lambda: self.status_label.configure(text=""))


        def save_action():
            """Pobiera dane z pól, zapisuje do bazy i wyświetla status na froncie."""
            try:
                # 1. Pobranie i wstępne czyszczenie danych z pól Entry
                # Usuwamy białe znaki i ujednolicamy format liczb (kropka zamiast przecinka)
                vals = [e.get().strip().replace(',', '.') for e in entries]
                
                # 2. Wybór odpowiedniej ścieżki zapisu w zależności od kategorii i trybu (Nowy/Edycja)
                if cat == "Narzędzia":
                    if is_new:
                        database.add_tool_row(vals) # Dodawanie nowego narzędzia
                    else:
                        database.update_tool_row(data[0], vals) # Edycja po ID
                
                elif cat == "Powłoki":
                    if is_new:
                        database.add_coating_row(vals) # Dodawanie nowej powłoki
                    else:
                        database.update_coating_row(data[0], vals) # Edycja po ID
                
                else: # Usługi
                    if is_new:
                        database.add_service_row(vals) # Dodawanie nowej usługi
                    else:
                        database.update_service_row(data[0], vals) # Edycja po ID

                # 3. Finalizacja operacji
                form.destroy()          # Zamknięcie okna formularza
                self.refresh_list()     # Odświeżenie tabeli w głównym oknie
                
                # Wyświetlenie nowoczesnego komunikatu na froncie zamiast messagebox
                self.show_status("ZAPISANO POMYŚLNIE!", color="#28a745")

            except Exception as ex:
                # W przypadku błędu wyświetlamy informację na czerwono
                self.show_status(f"BŁĄD ZAPISU: {ex}", color="#dc3545")
                print(f"Log błędu: {ex}")