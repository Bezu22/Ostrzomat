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

        # 1. Wybór Głównej Kategorii
        ctk.CTkLabel(self.top_bar, text="Kategoria:").pack(side="left", padx=5)
        self.main_cat_combo = ctk.CTkComboBox(self.top_bar, 
                                             values=["Narzędzia", "Powłoki", "Usługi"],
                                             command=self.on_main_cat_change)
        self.main_cat_combo.set("Narzędzia")
        self.main_cat_combo.pack(side="left", padx=5)

        # 2. Wybór Typu (Filtrowanie)
        ctk.CTkLabel(self.top_bar, text="Filtr:").pack(side="left", padx=5)
        self.sub_filter_combo = ctk.CTkComboBox(self.top_bar, values=["Wszystkie"], command=self.refresh_list)
        self.sub_filter_combo.pack(side="left", padx=5)

        # Przyciski
        self.btn_edit = ctk.CTkButton(self.top_bar, text="EDYTUJ", state="disabled", width=100, command=self.open_edit_form)
        self.btn_edit.pack(side="left", padx=10)

        self.btn_delete = ctk.CTkButton(self.top_bar, text="USUŃ", state="disabled", fg_color="#dc3545", width=100, command=self.delete_action)
        self.btn_delete.pack(side="left", padx=5)

        # --- PANEL NAGŁÓWKÓW ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=5)

        # --- LISTA ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#1a1a1a")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.on_main_cat_change()

    def on_main_cat_change(self, _=None):
        """Aktualizuje filtr podrzędny i nagłówki przy zmianie kategorii głównej."""
        cat = self.main_cat_combo.get()
        
        if cat == "Narzędzia":
            vals = ["Wszystkie", "Frezy", "Wiertła", "Inne"]
            self.headers = [("Typ", 180), ("Ostrza", 100), ("Ø Min", 80), ("Ø Max", 80), ("1 szt", 80), ("2-4", 80), ("5-10", 80), ("11+", 80)]
        elif cat == "Powłoki":
            vals = ["Wszystkie"] + database.get_unique_coating_names()
            self.headers = [("Nazwa powłoki", 250), ("Ø Max", 120), ("Długość", 120), ("Cena", 120)]
        else: # Usługi
            vals = ["Wszystkie"] + database.get_unique_service_names()
            self.headers = [("Nazwa usługi", 250), ("Param Min", 150), ("Param Max", 150), ("Cena", 120)]

        self.sub_filter_combo.configure(values=vals)
        self.sub_filter_combo.set("Wszystkie")
        
        # Odśwież nagłówki wizualnie
        for child in self.header_frame.winfo_children(): child.destroy()
        for text, width in self.headers:
            ctk.CTkLabel(self.header_frame, text=text, font=("Arial", 12, "bold"), width=width, anchor="w").pack(side="left", padx=5)
            
        self.refresh_list()

    def refresh_list(self, _=None):
        self.selected_row_data = None
        self.btn_edit.configure(state="disabled")
        self.btn_delete.configure(state="disabled")
        for child in list(self.scroll_frame.winfo_children()): child.destroy()

        cat = self.main_cat_combo.get()
        filt = self.sub_filter_combo.get()

        if cat == "Narzędzia":
            # Mapowanie: W Twoim ComboBoxie są "Frezy", "Wiertła", 
            # a w bazie category to "Frezy", "Wiertła", "Inne"
            data = database.get_filtered_tools(filt, "Wszystkie")
            col_widths = [180, 100, 80, 80, 80, 80, 80, 80]
            # Przeskakujemy ID (0) i Category (1) w wyświetlaniu dla narzędzi
            display_slice = slice(2, 10) 
        elif cat == "Powłoki":
            data = database.get_filtered_coatings(filt)
            col_widths = [250, 120, 120, 120]
            display_slice = slice(1, 5)
        else:
            data = database.get_filtered_services(filt)
            col_widths = [250, 150, 150, 120]
            display_slice = slice(1, 5)

        for index, row in enumerate(data):
            self.render_row_item(row, index % 2 == 0, col_widths, display_slice)

    def render_row_item(self, row, is_even, widths, d_slice):
        bg = "transparent" if is_even else "#2b2b2b"
        f = ctk.CTkFrame(self.scroll_frame, fg_color=bg, corner_radius=0)
        f.pack(fill="x", pady=0, padx=5)
        f.original_bg = bg

        for i, val in enumerate(row[d_slice]):
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
        if messagebox.askyesno("Usuń", "Czy na pewno usunąć ten wpis?"):
            database.delete_row(table, self.selected_row_data[0])
            self.refresh_list()

    def open_edit_form(self, existing_data=None):
        """Dynamiczny formularz dostosowujący się do kategorii (Narzędzia/Powłoki/Usługi)."""
        cat = self.main_cat_combo.get()
        data = existing_data if existing_data else self.selected_row_data
        
        form = ctk.CTkToplevel(self)
        form.title(f"{cat} - {'Edycja' if data else 'Nowa pozycja'}")
        form.geometry("450x800")
        form.attributes("-topmost", True)
        form.grab_set()

        # Definicja pól w zależności od kategorii
        if cat == "Narzędzia":
            # Pamiętaj: w bazie tools mamy: id, category, tool_type, blades, d_min, d_max, p1, p2, p3, p4
            labels = ["Kategoria (Frezy/Wiertła/Inne)", "Typ narzędzia", "Ilość ostrzy", 
                      "Ø MIN", "Ø MAX", "Cena (1)", "Cena (2-4)", "Cena (5-10)", "Cena (11+)"]
            db_slice = slice(1, 10) # Indeksy danych z bazy (bez ID)
        elif cat == "Powłoki":
            labels = ["Nazwa powłoki", "Ø MAX", "Długość", "Cena"]
            db_slice = slice(1, 5)
        else: # Usługi
            labels = ["Nazwa usługi", "Parametr MIN", "Parametr MAX", "Cena"]
            db_slice = slice(1, 5)

        entries = []
        for i, txt in enumerate(labels):
            ctk.CTkLabel(form, text=txt, font=("Arial", 12, "bold")).pack(pady=(15, 0))
            
            # Podpowiedź dla ostrzy
            if txt == "Ilość ostrzy":
                ctk.CTkLabel(form, text="(np. '2-4', '6' lub 'pozostałe')", 
                            font=("Arial", 10), text_color="gray").pack()

            e = ctk.CTkEntry(form, width=300)
            if data:
                # Wypełniamy pola danymi z bazy, używając wybranego wycinka (slice)
                current_values = data[db_slice]
                e.insert(0, str(current_values[i]))
            e.pack(pady=5)
            entries.append(e)

        def save_action():
            try:
                # Pobranie wartości i zamiana przecinków na kropki
                raw_vals = [e.get().strip().replace(',', '.') for e in entries]
                
                # Walidacja: czy pola liczbowe są poprawne (zależnie od kategorii)
                # Dla uproszczenia sprawdzamy od 3-go pola wzwyż dla Narzędzi i od 2-go dla reszty
                start_num = 3 if cat == "Narzędzia" else 1
                for val in raw_vals[start_num:]:
                    float(val) # Jeśli nie liczba, wyrzuci błąd do except

                # Wybór odpowiedniej funkcji zapisu z database.py
                if cat == "Narzędzia":
                    if data: database.update_tool_row(data[0], raw_vals)
                    else: database.add_tool_row(raw_vals)
                elif cat == "Powłoki":
                    if data: database.update_coating_row(data[0], raw_vals)
                    else: database.add_coating_row(raw_vals)
                else: # Usługi
                    if data: database.update_service_row(data[0], raw_vals)
                    else: database.add_service_row(raw_vals)

                form.destroy()
                self.refresh_list()
                messagebox.showinfo("Sukces", "Zapisano zmiany w cenniku.")
            except ValueError:
                messagebox.showerror("Błąd danych", "Pola wymiarów i cen muszą być liczbami!")
            except Exception as ex:
                messagebox.showerror("Błąd", f"Błąd zapisu: {ex}")

        ctk.CTkButton(form, text="ZAPISZ I ZAMKNIJ", fg_color="#28a745", height=45, 
                      command=save_action).pack(pady=40)