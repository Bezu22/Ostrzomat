import customtkinter as ctk

class CartTable(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Nagłówki tabeli
        self.setup_headers()
        
        # Przewijany obszar na wiersze z narzędziami
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def setup_headers(self):
        """Konfiguracja nagłówków kolumn."""
        h_frame = ctk.CTkFrame(self, fg_color="#333", height=35, corner_radius=0)
        h_frame.pack(fill="x")
        
        # Struktura: TYP | Ø | Z | SZT | OSTRZ. JEDN | OSTRZ. RAZEM | POWŁOKA | L | POWŁ. RAZEM | CIĘCIE | ZANIŻ. | POLER. | USŁ. RAZEM | RAZEM
        cols = [
            ("TYP NARZĘDZIA", 200), ("Ø", 50), ("Z", 40), ("SZT.", 50), 
            ("OSTRZ. JEDN.", 90), ("OSTRZ. RAZEM", 100), 
            ("POWŁOKA", 100), ("L", 50), ("POWŁ. RAZEM", 100),
            ("CIĘCIE", 60), ("ZANIŻ.", 60), ("POLER.", 60), 
            ("USŁ. RAZEM", 100), ("RAZEM", 120)
        ]
        
        for text, width in cols:
            align = "w" if "TYP" in text else "center"
            lbl = ctk.CTkLabel(h_frame, text=text, width=width, font=("Arial", 10, "bold"), anchor=align)
            lbl.pack(side="left", padx=5)

    def refresh(self, items):
        """Czyści i renderuje listę przedmiotów w koszyku."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        for idx, item in enumerate(items):
            bg_color = "#2b2b2b" if idx % 2 == 0 else "#333"
            row = ctk.CTkFrame(self.scroll_frame, fg_color=bg_color, height=50, corner_radius=5)
            row.pack(fill="x", pady=2)

            # Pomocnicza funkcja parsująca tekst na float
            def to_f(val):
                if not val or val == "-": return 0.0
                try: return float(str(val).replace(' zł', '').replace(',', '.').strip())
                except: return 0.0

            s_tool = to_f(item.get("total_tool"))
            s_coat = to_f(item.get("total_coat"))
            s_extra = to_f(item.get("total_extra"))
            line_total = s_tool + s_coat + s_extra

            # 1. Dane podstawowe
            ctk.CTkLabel(row, text=item.get("type", "-"), width=200, anchor="w", wraplength=190, justify="left").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=item.get("diam", "-"), width=50, anchor="center").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=item.get("z", "-"), width=40, anchor="center").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=item.get("qty", "-"), width=50, anchor="center").pack(side="left", padx=5)
            
            # 2. Ostrzenie
            ctk.CTkLabel(row, text=item.get("tool_unit", "-"), width=90, anchor="center").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"{s_tool:.2f} zł", width=100, anchor="center", text_color="#aaa").pack(side="left", padx=5)
            
            # 3. Powłoka
            has_c = item.get("coat_name") != "Brak"
            ctk.CTkLabel(row, text=item.get("coat_name", "Brak"), width=100, anchor="center", wraplength=90).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=item.get("coat_len", "-") if has_c else "-", width=50, anchor="center").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"{s_coat:.2f} zł" if s_coat > 0 else "-", width=100, anchor="center").pack(side="left", padx=5)
            
            # 4. Usługi (Statusy + Suma)
            status = item.get("services_status", {})
            for s_key in ["ciecie", "opuszczenie", "polerowanie"]:
                is_active = status.get(s_key, False)
                val = "+" if is_active else "-"
                color = "#28a745" if is_active else "#555"
                ctk.CTkLabel(row, text=val, width=60, anchor="center", text_color=color, font=("Arial", 14, "bold")).pack(side="left", padx=5)
            
            ctk.CTkLabel(row, text=f"{s_extra:.2f} zł" if s_extra > 0 else "-", width=100, anchor="center").pack(side="left", padx=5)
            
            # 5. Suma wiersza (Razem)
            ctk.CTkLabel(row, text=f"{line_total:.2f} zł", width=120, font=("Arial", 13, "bold"), text_color="#3498db", anchor="center").pack(side="left", padx=5)