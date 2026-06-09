import customtkinter as ctk

class CartTable(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # --- GLOBALNA ZMIENNA ROZMIARU CZCIONKI ---
        # Zmień tę liczbę tutaj (np. na 11, 12, 14), aby zmienić rozmiar w całej tabeli:
        BASE_SIZE = 12
        FONT_FAMILY = "Arial"
        
        # Tworzymy krotki bezpośrednio na podstawie zmiennej
        self.font_header = (FONT_FAMILY, BASE_SIZE - 1, "bold") 
        self.font_normal = (FONT_FAMILY, BASE_SIZE)              
        self.font_bold   = (FONT_FAMILY, BASE_SIZE, "bold")     
        
        # Definicja i sztywne szerokości kolumn
        self.cols = [
            ("L.p.", 40),
            ("TYP NARZĘDZIA", 130),
            ("Ø ROB.", 70),
            ("Ø CHWYT", 50),
            ("Z", 40),
            ("ZUŻ.", 55),      
            ("C", 55),
            ("ZAN.", 55),
            ("POL.", 55),     
            ("SZT.", 60),
            ("REGEN./SZT", 100),
            ("WARTOŚĆ R.", 110),
            ("POWŁOKA", 100),
            ("L", 100),
            ("POWŁ./SZT", 80),
            ("WARTOŚĆ P.", 90),
            ("SUMA POZ.", 100),
            ("UWAGI", 250)     
        ]
        self.selected_idx = None
        self.row_frames = {}  # Słownik do przechowywania referencji do ramek wierszy

        self.setup_headers()
        
        # Margines z prawej (15px) rezerwuje miejsce na suwak (scrollbar)
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=(0, 15), pady=5)

    def setup_headers(self):
        """Konfiguracja nagłówków kolumn przy użyciu GRID dla idealnego centrowania."""
        h_frame = ctk.CTkFrame(self, fg_color="#333", height=35, corner_radius=0)
        h_frame.pack(fill="x", padx=(0, 15)) 
        
        # Konfigurujemy minimalne szerokości kolumn w siatce nagłówka
        for i, (_, width) in enumerate(self.cols):
            h_frame.columnconfigure(i, weight=0, minsize=width)
        
        for i, (text, width) in enumerate(self.cols):
            lbl = ctk.CTkLabel(h_frame, text=text, font=self.font_header, anchor="center", justify="center")
            lbl.grid(row=0, column=i, padx=2, pady=5, sticky="ew")

    def toggle_select_row(self, idx):
        """Logika wizualnego zaznaczania wiersza po kliknięciu."""
        # Jeśli kliknięto ten sam wiersz, który jest zaznaczony -> odznacz go
        if self.selected_idx == idx:
            self.selected_idx = None
        else:
            self.selected_idx = idx

        # Przerysowanie tła wierszy, aby uwzględnić zmianę zaznaczenia
        self.update_row_backgrounds()

    def update_row_backgrounds(self):
        """Przywraca standardowe kolory lub nakłada kolor zaznaczenia."""
        for idx, row_frame in self.row_frames.items():
            if idx == self.selected_idx:
                # Kolor dla zaznaczonego wiersza (ładny odcień niebieskiego)
                row_frame.configure(fg_color="#1f538d")
            else:
                # Standardowe naprzemienne kolory
                bg_color = "#2b2b2b" if idx % 2 == 0 else "#333"
                row_frame.configure(fg_color=bg_color)
    
    def get_selected_index(self):
        """Zwraca indeks zaznaczonego wiersza lub None."""
        return self.selected_idx
    
    def refresh(self, items):
        """Odświeżanie tabeli z podpięciem zdarzenia kliknięcia w celach edycji."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.row_frames.clear()
        # Resetujemy zaznaczenie przy przeładowaniu całego koszyka (np. usunięcie/wczytanie)
        if self.selected_idx is not None and self.selected_idx >= len(items):
            self.selected_idx = None

        for idx, item in enumerate(items):
            bg_color = "#2b2b2b" if idx % 2 == 0 else "#333"
            row = ctk.CTkFrame(self.scroll_frame, fg_color=bg_color, height=45, corner_radius=5)
            row.pack(fill="x", pady=1)
            
            # Zapisujemy referencję do ramki wiersza
            self.row_frames[idx] = row

            # Bindowanie kliknięcia w tło wiersza
            row.bind("<Button-1>", lambda event, i=idx: self.toggle_select_row(i))

            for i, (_, width) in enumerate(self.cols):
                row.columnconfigure(i, weight=0, minsize=width)

            def get_v(k): return float(item.get(k, 0.0))

            qty = int(item.get("qty", 1))
            regen_unit = get_v("tool_unit") + get_v("extra_unit")
            regen_total = regen_unit * qty
            coat_unit = get_v("coat_unit")
            coat_total = get_v("total_coat")
            suma_calkowita_pozycji = regen_total + coat_total

            # Funkcja pomocnicza tworząca label automatycznie dziedziczący kliknięcie wiersza
            def create_cell_label(column, text, font, text_color=None):
                lbl = ctk.CTkLabel(row, text=text, anchor="center", font=font)
                if text_color:
                    lbl.configure(text_color=text_color)
                
                # KLUCZOWE: Jeśli klikniemy w tekst, zdarzenie przechodzi na ramkę wiersza
                lbl.bind("<Button-1>", lambda event, i=idx: self.toggle_select_row(i))
                lbl.grid(row=0, column=column, padx=2, pady=5, sticky="ew")

            # --- RENDEROWANIE KOLUMN (teraz przez funkcję pomocniczą) ---
            create_cell_label(0, str(idx + 1), self.font_normal)
            
            # Dla typu narzędzia zachowujemy wraplength i justify
            lbl_type = ctk.CTkLabel(row, text=item.get("type", "-"), anchor="center", wraplength=self.cols[1][1]-5, justify="center", font=self.font_normal)
            lbl_type.bind("<Button-1>", lambda event, i=idx: self.toggle_select_row(i))
            lbl_type.grid(row=0, column=1, padx=2, pady=5, sticky="ew")

            create_cell_label(2, item.get("diam", "-"), self.font_normal)
            shank_val = item.get("shank_diam", item.get("diam", "-"))
            create_cell_label(3, shank_val, self.font_normal)
            create_cell_label(4, item.get("z", "-"), self.font_normal)

            status = item.get("services_status", {})
            
            is_wear = status.get("zuzycie", False)
            create_cell_label(5, "+" if is_wear else "-", self.font_bold, "#e74c3c" if is_wear else "#555")

            is_c = status.get("ciecie", False)
            create_cell_label(6, "+" if is_c else "-", self.font_bold, "#28a745" if is_c else "#555")

            is_o = status.get("opuszczenie", False)
            create_cell_label(7, "+" if is_o else "-", self.font_bold, "#28a745" if is_o else "#555")

            is_p = status.get("polerowanie", False)
            create_cell_label(8, "+" if is_p else "-", self.font_bold, "#28a745" if is_p else "#555")

            create_cell_label(9, str(qty), self.font_bold)
            create_cell_label(10, f"{regen_unit:.2f}", self.font_normal)
            create_cell_label(11, f"{regen_total:.2f}", self.font_bold, "#28a745")

            has_coat = item.get("coat_name") != "Brak"
            
            lbl_coat = ctk.CTkLabel(row, text=item.get("coat_name", "Brak"), anchor="center", wraplength=self.cols[12][1]-5, justify="center", font=self.font_normal)
            lbl_coat.bind("<Button-1>", lambda event, i=idx: self.toggle_select_row(i))
            lbl_coat.grid(row=0, column=12, padx=2, pady=5, sticky="ew")

            create_cell_label(13, item.get("coat_len", "-") if has_coat else "-", self.font_normal)
            create_cell_label(14, f"{coat_unit:.2f}" if has_coat else "-", self.font_normal)
            create_cell_label(15, f"{coat_total:.2f}" if has_coat else "-", self.font_bold, "#3498db" if has_coat else None)
            create_cell_label(16, f"{suma_calkowita_pozycji:.2f} zł", self.font_bold)
            
            # 17. UWAGI (Kolumna dynamiczna z inteligentnym skracaniem tekstu do 20 znaków)
            full_notes_text = item.get("notes", "").strip()
            
            # Algorytm skracania do 100 znaków
            if len(full_notes_text) > 80:
                short_notes_text = full_notes_text[:80] + "..."
            else:
                short_notes_text = full_notes_text if full_notes_text else "-"

            lbl_notes = ctk.CTkLabel(
                row, 
                text=short_notes_text, 
                anchor="center", 
                wraplength=self.cols[17][1]-5, 
                justify="center", 
                text_color="#e67e22" if full_notes_text else "#888", # Pomarańczowy kolor wyróżni wiersze z uwagami
                font=self.font_normal
            )
            
            # Podwójne bindowanie: Kliknięcie zaznacza wiersz ORAZ otwiera dedykowany edytor uwag!
            lbl_notes.bind("<Button-1>", lambda event, i=idx: self._handle_notes_click(i))
            lbl_notes.grid(row=0, column=17, padx=2, pady=5, sticky="ew")

        # Na koniec upewniamy się, że nowo wyrenderowany zaznaczony wiersz zachowa kolor
        self.update_row_backgrounds()

    def _handle_notes_click(self, index):
        """Zaznacza wiersz w tabeli i natychmiast zgłasza chęć edycji samej uwagi."""
        self.toggle_select_row(index)
        
        if hasattr(self.master.master, 'open_notes_editor'):
            self.master.master.open_notes_editor()