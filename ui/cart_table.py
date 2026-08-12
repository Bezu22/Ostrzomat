import customtkinter as ctk
from ui.style import AppStyle

class CartTable(ctk.CTkFrame):
    def __init__(self, parent, on_notes_click=None):
        super().__init__(parent)
        
        # Zapamiętujemy funkcja zwrotną otwierającą uwagi
        self.on_notes_click = on_notes_click
        
        # Pobieranie czcionek z centralnego pliku konfiguracji stylów
        self.font_header = AppStyle.get_header_font()
        self.font_normal = AppStyle.get_normal_font()
        self.font_bold   = AppStyle.get_bold_font()     
        
        # Definicja i sztywne szerokości kolumn - dodano WART. USŁ. przed REGEN./SZT
        self.cols = [
            ("L.p.", 40),          # idx 0
            ("TYP NARZĘDZIA", 130), # idx 1
            ("Ø ROB.", 70),        # idx 2
            ("Ø CHWYT", 50),       # idx 3
            ("Z", 40),             # idx 4
            ("ZUŻ.", 55),          # idx 5
            ("CIAC", 55),          # idx 6
            ("ZAN.", 55),          # idx 7
            ("POL.", 55),          # idx 8
            ("SZT.", 60),          # idx 9
            ("WART. USŁ.", 90),    # idx 10 (NOWA KOLUMNA)
            ("REGEN./SZT", 100),   # idx 11
            ("WARTOŚĆ R.", 110),   # idx 12
            ("POWŁOKA", 100),      # idx 13
            ("L", 100),            # idx 14
            ("POWŁ./SZT", 80),     # idx 15
            ("WARTOŚĆ P.", 90),    # idx 16
            ("SUMA POZ.", 100),    # idx 17
            ("UWAGI", 250)         # idx 18
        ]
        self.selected_idx = None
        self.row_frames = {}

        self.setup_headers()
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=(0, 15), pady=5)

    def setup_headers(self):
        """Konfiguracja nagłówków kolumn przy użyciu GRID dla idealnego centrowania."""
        h_frame = ctk.CTkFrame(self, fg_color=AppStyle.COLOR_BG_LIGHT, height=35, corner_radius=0)
        h_frame.pack(fill="x", padx=(0, 15)) 
        
        for i, (_, width) in enumerate(self.cols):
            h_frame.columnconfigure(i, weight=0, minsize=width)
        
        for i, (text, width) in enumerate(self.cols):
            lbl = ctk.CTkLabel(h_frame, text=text, font=self.font_header, anchor="center", justify="center")
            lbl.grid(row=0, column=i, padx=2, pady=5, sticky="ew")

    def toggle_select_row(self, idx):
        """Logika wizualnego zaznaczania wiersza po kliknięciu."""
        if self.selected_idx == idx:
            self.selected_idx = None
        else:
            self.selected_idx = idx
        self.update_row_backgrounds()

    def update_row_backgrounds(self):
        """Przywraca standardowe kolory lub nakłada kolor zaznaczenia."""
        for idx, row_frame in self.row_frames.items():
            if idx == self.selected_idx:
                row_frame.configure(fg_color=AppStyle.COLOR_PRIMARY)
            else:
                bg_color = AppStyle.COLOR_BG_DARK if idx % 2 == 0 else AppStyle.COLOR_BG_LIGHT
                row_frame.configure(fg_color=bg_color)
    
    def get_selected_index(self):
        """Zwraca indeks zaznaczonego wiersza lub None."""
        return self.selected_idx
    
    def refresh(self, items):
        """Odświeżanie tabeli z poprawnym rozdzieleniem wartości regeneracji i usług."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.row_frames.clear()
        if self.selected_idx is not None and self.selected_idx >= len(items):
            self.selected_idx = None

        for idx, item in enumerate(items):
            bg_color = AppStyle.COLOR_BG_DARK if idx % 2 == 0 else AppStyle.COLOR_BG_LIGHT
            row = ctk.CTkFrame(self.scroll_frame, fg_color=bg_color, height=45, corner_radius=5)
            row.pack(fill="x", pady=1)
            
            self.row_frames[idx] = row
            row.bind("<Button-1>", lambda event, i=idx: self.toggle_select_row(i))

            for i, (_, width) in enumerate(self.cols):
                row.columnconfigure(i, weight=0, minsize=width)

            def get_v(k): return float(item.get(k, 0.0))

            qty = int(item.get("qty", 1))
            
            # --- POPRAWIONE WYLICZENIA WARTOŚCI ---
            regen_unit = get_v("tool_unit")      # Czysta cena ostrzenia za 1 sztukę
            regen_total = get_v("total_tool")    # Czysta wartość ostrzenia (tool_unit * qty)
            extra_total = get_v("total_extra")   # Łączna wartość usług dodatkowych
            coat_unit   = get_v("coat_unit")
            coat_total  = get_v("total_coat")
            
            # Suma końcowa pozycji
            suma_calkowita_pozycji = regen_total + extra_total + coat_total

            def create_cell_label(column, text, font, text_color=None):
                lbl = ctk.CTkLabel(row, text=text, anchor="center", font=font)
                if text_color:
                    lbl.configure(text_color=text_color)
                lbl.bind("<Button-1>", lambda event, i=idx: self.toggle_select_row(i))
                lbl.grid(row=0, column=column, padx=2, pady=5, sticky="ew")

            create_cell_label(0, str(idx + 1), self.font_normal)
            
            lbl_type = ctk.CTkLabel(row, text=item.get("type", "-"), anchor="center", wraplength=self.cols[1][1]-5, justify="center", font=self.font_normal)
            lbl_type.bind("<Button-1>", lambda event, i=idx: self.toggle_select_row(i))
            lbl_type.grid(row=0, column=1, padx=2, pady=5, sticky="ew")

            create_cell_label(2, item.get("diam", "-"), self.font_normal)
            shank_val = item.get("shank_diam", item.get("diam", "-"))
            create_cell_label(3, shank_val, self.font_normal)
            create_cell_label(4, item.get("z", "-"), self.font_normal)

            # --- SEKCJA USŁUG DODATKOWYCH (LICZBA SZTUK) ---
            status = item.get("services_status", {})
            sq = item.get("services_qty", {})

            def get_service_display(key):
                if status.get(key):
                    return str(sq.get(key, qty))
                return "-"

            # ZUŻYCIE
            zuzycie_val = get_service_display("zuzycie")
            is_wear = zuzycie_val != "-"
            create_cell_label(5, zuzycie_val, self.font_bold, AppStyle.COLOR_SUCCESS if is_wear else "#555")

            # CIĘCIE
            ciecie_val = get_service_display("ciecie")
            is_c = ciecie_val != "-"
            create_cell_label(6, ciecie_val, self.font_bold, AppStyle.COLOR_SUCCESS if is_c else "#555")

            # ZANIŻENIE ŚREDNICY
            opuszczenie_val = get_service_display("opuszczenie")
            is_o = opuszczenie_val != "-"
            create_cell_label(7, opuszczenie_val, self.font_bold, AppStyle.COLOR_SUCCESS if is_o else "#555")

            # POLEROWANIE ROWKA
            polerowanie_val = get_service_display("polerowanie")
            is_p = polerowanie_val != "-"
            create_cell_label(8, polerowanie_val, self.font_bold, AppStyle.COLOR_SUCCESS if is_p else "#555")

            # ILOŚĆ SZTUK
            create_cell_label(9, str(qty), self.font_bold)

            # --- DANE FINANSKOWE (ZAKTUALIZOWANE KOLUMNY) ---
            # 10: WART. USŁ. (Łączna wartość usług w pozycji)
            has_extra = extra_total > 0
            create_cell_label(10, f"{extra_total:.2f}" if has_extra else "-", self.font_bold if has_extra else self.font_normal, AppStyle.COLOR_SUCCESS if has_extra else None)

            # 11: REGEN./SZT (Sama cena jednostkowa ostrzenia)
            create_cell_label(11, f"{regen_unit:.2f}", self.font_normal)

            # 12: WARTOŚĆ R. (Wartość ostrzenia dla wszystkich sztuk)
            create_cell_label(12, f"{regen_total:.2f}", self.font_bold, AppStyle.COLOR_SUCCESS)

            # --- POWŁOKI I SUMA ---
            has_coat = item.get("coat_name") != "Brak"
            
            lbl_coat = ctk.CTkLabel(row, text=item.get("coat_name", "Brak"), anchor="center", wraplength=self.cols[13][1]-5, justify="center", font=self.font_normal)
            lbl_coat.bind("<Button-1>", lambda event, i=idx: self.toggle_select_row(i))
            lbl_coat.grid(row=0, column=13, padx=2, pady=5, sticky="ew")

            create_cell_label(14, item.get("coat_len", "-") if has_coat else "-", self.font_normal)
            create_cell_label(15, f"{coat_unit:.2f}" if has_coat else "-", self.font_normal)
            create_cell_label(16, f"{coat_total:.2f}" if has_coat else "-", self.font_bold, "#3498db" if has_coat else None)
            create_cell_label(17, f"{suma_calkowita_pozycji:.2f} zł", self.font_bold)
            
            # --- UWAGI ---
            full_notes_text = item.get("notes", "").strip()
            
            if len(full_notes_text) > 80:
                short_notes_text = full_notes_text[:80] + "..."
            else:
                short_notes_text = full_notes_text if full_notes_text else "-"

            lbl_notes = ctk.CTkLabel(
                row, 
                text=short_notes_text, 
                anchor="center", 
                wraplength=self.cols[18][1] - 5, 
                justify="center", 
                text_color=AppStyle.COLOR_WARNING if full_notes_text else AppStyle.COLOR_TEXT_MUTED,
                font=self.font_normal,
                cursor="hand2"
            )
            
            def _on_enter(event, label=lbl_notes, has_text=bool(full_notes_text)):
                hover_color = AppStyle.COLOR_WARNING_HOVER if has_text else AppStyle.COLOR_TEXT_LIGHT
                label.configure(text_color=hover_color)

            def _on_leave(event, label=lbl_notes, has_text=bool(full_notes_text)):
                original_color = AppStyle.COLOR_WARNING if has_text else AppStyle.COLOR_TEXT_MUTED
                label.configure(text_color=original_color)

            lbl_notes.bind("<Enter>", _on_enter)
            lbl_notes.bind("<Leave>", _on_leave)
            lbl_notes.bind("<Button-1>", lambda event, i=idx: self._handle_notes_click(i))
            
            lbl_notes.grid(row=0, column=18, padx=2, pady=5, sticky="ew")

        self.update_row_backgrounds()

    def _handle_notes_click(self, index):
        """Prawidłowa i bezpośrednia obsługa kliknięcia komórki uwagi."""
        self.toggle_select_row(index)
        if self.on_notes_click:
            self.on_notes_click(index)