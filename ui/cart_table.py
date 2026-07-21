import customtkinter as ctk
from ui.style import Style

class CartTable(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.font_header = Style.FONT_HEADER
        self.font_normal = Style.FONT_NORMAL
        self.font_bold   = Style.FONT_BOLD
        
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
        self.scroll_frame.pack(fill="both", expand=True, padx=(0, 15), pady=Style.PAD_SMALL)

    def setup_headers(self):
        h_frame = ctk.CTkFrame(self, fg_color=Style.COLOR_HEADER_BG, height=35, corner_radius=Style.CORNER_RADIUS)
        h_frame.pack(fill="x", padx=(0, 15)) 
        
        for i, (_, width) in enumerate(self.cols):
            h_frame.columnconfigure(i, weight=0, minsize=width)
        
        for i, (text, _) in enumerate(self.cols):
            lbl = ctk.CTkLabel(h_frame, text=text, font=self.font_header, text_color=Style.COLOR_TEXT_DARK, anchor="center", justify="center")
            lbl.grid(row=0, column=i, padx=2, pady=5, sticky="ew")

    def toggle_select_row(self, idx):
        if self.selected_idx == idx:
            self.selected_idx = None
        else:
            self.selected_idx = idx
        self.update_row_backgrounds()

    def update_row_backgrounds(self):
        for idx, row_frame in self.row_frames.items():
            if idx == self.selected_idx:
                row_frame.configure(fg_color=Style.COLOR_ROW_SELECTED)
            else:
                bg_color = Style.COLOR_ROW_EVEN if idx % 2 == 0 else Style.COLOR_ROW_ODD
                row_frame.configure(fg_color=bg_color)
    
    def get_selected_index(self):
        return self.selected_idx
    
    def refresh(self, items):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.row_frames.clear()
        if self.selected_idx is not None and self.selected_idx >= len(items):
            self.selected_idx = None

        for idx, item in enumerate(items):
            bg_color = Style.COLOR_ROW_EVEN if idx % 2 == 0 else Style.COLOR_ROW_ODD
            row = ctk.CTkFrame(self.scroll_frame, fg_color=bg_color, height=45, corner_radius=Style.CORNER_RADIUS)
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

            def create_cell_label(column, text, font, text_color=Style.COLOR_TEXT_DARK):
                lbl = ctk.CTkLabel(row, text=text, anchor="center", font=font, text_color=text_color)
                lbl.bind("<Button-1>", lambda event, i=idx: self.toggle_select_row(i))
                lbl.grid(row=0, column=column, padx=2, pady=5, sticky="ew")

            create_cell_label(0, str(idx + 1), self.font_normal)
            
            lbl_type = ctk.CTkLabel(row, text=item.get("type", "-"), text_color=Style.COLOR_TEXT_DARK, anchor="center", wraplength=self.cols[1][1]-5, justify="center", font=self.font_normal)
            lbl_type.bind("<Button-1>", lambda event, i=idx: self.toggle_select_row(i))
            lbl_type.grid(row=0, column=1, padx=2, pady=5, sticky="ew")

            create_cell_label(2, item.get("diam", "-"), self.font_normal)
            shank_val = item.get("shank_diam", item.get("diam", "-"))
            create_cell_label(3, shank_val, self.font_normal)
            create_cell_label(4, item.get("z", "-"), self.font_normal)

            status = item.get("services_status", {})
            
            is_wear = status.get("zuzycie", False)
            create_cell_label(5, "+" if is_wear else "-", self.font_bold, Style.COLOR_DANGER if is_wear else Style.COLOR_TEXT_INACTIVE)

            is_c = status.get("ciecie", False)
            create_cell_label(6, "+" if is_c else "-", self.font_bold, Style.COLOR_SUCCESS if is_c else Style.COLOR_TEXT_INACTIVE)

            is_o = status.get("opuszczenie", False)
            if is_o:
                mult = item.get("opuszczenie_mult", 1)
                text_zan = "+" * mult
                color_zan = Style.COLOR_SUCCESS
            else:
                text_zan = "-"
                color_zan = Style.COLOR_TEXT_INACTIVE

            create_cell_label(7, text_zan, self.font_bold, color_zan)

            is_p = status.get("polerowanie", False)
            create_cell_label(8, "+" if is_p else "-", self.font_bold, Style.COLOR_SUCCESS if is_p else Style.COLOR_TEXT_INACTIVE)

            create_cell_label(9, str(qty), self.font_bold)
            create_cell_label(10, f"{regen_unit:.2f}", self.font_normal)
            create_cell_label(11, f"{regen_total:.2f}", self.font_bold, Style.COLOR_SUCCESS)

            has_coat = item.get("coat_name") != "Brak"
            
            lbl_coat = ctk.CTkLabel(row, text=item.get("coat_name", "Brak"), text_color=Style.COLOR_TEXT_DARK, anchor="center", wraplength=self.cols[12][1]-5, justify="center", font=self.font_normal)
            lbl_coat.bind("<Button-1>", lambda event, i=idx: self.toggle_select_row(i))
            lbl_coat.grid(row=0, column=12, padx=2, pady=5, sticky="ew")

            create_cell_label(13, item.get("coat_len", "-") if has_coat else "-", self.font_normal)
            create_cell_label(14, f"{coat_unit:.2f}" if has_coat else "-", self.font_normal)
            create_cell_label(15, f"{coat_total:.2f}" if has_coat else "-", self.font_bold, Style.COLOR_SECONDARY if has_coat else Style.COLOR_TEXT_INACTIVE)
            create_cell_label(16, f"{suma_calkowita_pozycji:.2f} zł", self.font_bold, Style.COLOR_TEXT_ACCENT)
            
            full_notes_text = item.get("notes", "").strip()
            short_notes_text = (full_notes_text[:80] + "...") if len(full_notes_text) > 80 else (full_notes_text if full_notes_text else "-")

            lbl_notes = ctk.CTkLabel(
                row, 
                text=short_notes_text, 
                anchor="center", 
                wraplength=self.cols[17][1]-5, 
                justify="center", 
                text_color=Style.COLOR_ACCENT_YELLOW if full_notes_text else Style.COLOR_TEXT_MUTED,
                font=self.font_normal
            )
            
            lbl_notes.bind("<Button-1>", lambda event, i=idx: self._handle_notes_click(i))
            lbl_notes.grid(row=0, column=17, padx=2, pady=5, sticky="ew")

        self.update_row_backgrounds()

    def _handle_notes_click(self, index):
        self.toggle_select_row(index)
        if hasattr(self.master.master, 'open_notes_editor'):
            self.master.master.open_notes_editor()