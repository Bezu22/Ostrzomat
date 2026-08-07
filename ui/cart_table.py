import customtkinter as ctk
from ui.style import AppStyle

class CartTable(ctk.CTkFrame):
    def __init__(self, parent, on_notes_click=None):
        super().__init__(parent)
        
        # Zapamiętujemy funkcję zwrotną otwierającą uwagi
        self.on_notes_click = on_notes_click
        
        # Pobieranie czcionek z centralnego pliku konfiguracji stylów
        self.font_header = AppStyle.get_header_font()
        self.font_normal = AppStyle.get_normal_font()
        self.font_bold   = AppStyle.get_bold_font()     
        
        # Definicja i sztywne szerokości kolumn
        self.cols = [
            ("L.p.", 40),
            ("TYP NARZĘDZIA", 130),
            ("Ø ROB.", 70),
            ("Ø CHWYT", 50),
            ("Z", 40),
            ("ZUŻ.", 55),      
            ("CIAC", 55),
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
        """Odświeżanie tabeli z podpięciem zdarzenia kliknięcia."""
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
            regen_unit = get_v("tool_unit") + get_v("extra_unit")
            regen_total = regen_unit * qty
            coat_unit = get_v("coat_unit")
            coat_total = get_v("total_coat")
            suma_calkowita_pozycji = regen_total + coat_total

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

            status = item.get("services_status", {})
            
            is_wear = status.get("zuzycie", False)
            create_cell_label(5, "+" if is_wear else "-", self.font_bold, AppStyle.COLOR_DANGER if is_wear else "#555")

            is_c = status.get("ciecie", False)
            create_cell_label(6, "+" if is_c else "-", self.font_bold, AppStyle.COLOR_SUCCESS if is_c else "#555")

            is_o = status.get("opuszczenie", False)
            if is_o:
                mult = item.get("opuszczenie_mult", 1)
                text_zan = "+" * mult
                color_zan = AppStyle.COLOR_SUCCESS
            else:
                text_zan = "-"
                color_zan = "#555"

            create_cell_label(7, text_zan, self.font_bold, color_zan)

            is_p = status.get("polerowanie", False)
            create_cell_label(8, "+" if is_p else "-", self.font_bold, AppStyle.COLOR_SUCCESS if is_p else "#555")

            create_cell_label(9, str(qty), self.font_bold)
            create_cell_label(10, f"{regen_unit:.2f}", self.font_normal)
            create_cell_label(11, f"{regen_total:.2f}", self.font_bold, AppStyle.COLOR_SUCCESS)

            has_coat = item.get("coat_name") != "Brak"
            
            lbl_coat = ctk.CTkLabel(row, text=item.get("coat_name", "Brak"), anchor="center", wraplength=self.cols[12][1]-5, justify="center", font=self.font_normal)
            lbl_coat.bind("<Button-1>", lambda event, i=idx: self.toggle_select_row(i))
            lbl_coat.grid(row=0, column=12, padx=2, pady=5, sticky="ew")

            create_cell_label(13, item.get("coat_len", "-") if has_coat else "-", self.font_normal)
            create_cell_label(14, f"{coat_unit:.2f}" if has_coat else "-", self.font_normal)
            create_cell_label(15, f"{coat_total:.2f}" if has_coat else "-", self.font_bold, "#3498db" if has_coat else None)
            create_cell_label(16, f"{suma_calkowita_pozycji:.2f} zł", self.font_bold)
            
            full_notes_text = item.get("notes", "").strip()
            
            if len(full_notes_text) > 80:
                short_notes_text = full_notes_text[:80] + "..."
            else:
                short_notes_text = full_notes_text if full_notes_text else "-"

            # --- TWORZENIE ETYKIETY UWAG Z EFEKTEM HOVER ---
            lbl_notes = ctk.CTkLabel(
                row, 
                text=short_notes_text, 
                anchor="center", 
                wraplength=self.cols[17][1] - 5, 
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
            
            lbl_notes.grid(row=0, column=17, padx=2, pady=5, sticky="ew")

        self.update_row_backgrounds()

    def _handle_notes_click(self, index):
        """Prawidłowa i bezpośrednia obsługa kliknięcia komórki uwagi."""
        self.toggle_select_row(index)
        if self.on_notes_click:
            self.on_notes_click(index)