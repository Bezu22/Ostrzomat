import customtkinter as ctk

class CartTable(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_headers()
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def setup_headers(self):
        h_frame = ctk.CTkFrame(self, fg_color="#333", height=35, corner_radius=0)
        h_frame.pack(fill="x")
        
        # Nowy układ: Typ(100) | Ø(40) | Z(30) | Szt(40) | Ostrz.J(80) | Ostrz.Σ(80) | Powłoka(100) | L(40) | Powł.J(80) | C(35) | Z(35) | P(35) | Usł.Σ(80) | Powł.Σ(80) | SUMA (wew)(100)
        self.cols = [
            ("TYP", 100), ("Ø", 40), ("Z", 30), ("SZT.", 40), 
            ("OSTRZ. J.", 80), ("OSTRZ. Σ", 80), 
            ("POWŁOKA", 100), ("L", 40), ("POWŁ. J.", 80),
            ("C", 35), ("Z", 35), ("P", 35), # Skrócone statusy
            ("USŁ. Σ", 80), ("POWŁ. Σ", 80), ("SUMA (WEW)", 100)
        ]
        
        for text, width in self.cols:
            lbl = ctk.CTkLabel(h_frame, text=text, width=width, font=("Arial", 9, "bold"), anchor="center")
            lbl.pack(side="left", padx=2)

    def refresh(self, items):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        for idx, item in enumerate(items):
            bg_color = "#2b2b2b" if idx % 2 == 0 else "#333"
            row = ctk.CTkFrame(self.scroll_frame, fg_color=bg_color, height=40, corner_radius=5)
            row.pack(fill="x", pady=1)

            # Pomocnicza funkcja do pobierania liczb
            def get_v(k): return float(item.get(k, 0.0))

            s_tool = get_v("total_tool")
            s_coat = get_v("total_coat")
            s_extra = get_v("total_extra")
            suma_wew = s_tool + s_extra

            # --- RENDEROWANIE KOLUMN  ---
            
            # 1. Dane podstawowe
            # Typ zostawiamy na "w" (do lewej), bo przy długich nazwach środek wygląda bałaganiarsko, 
            # ale jeśli chcesz wszystko w punkt, zmień "w" na "center".
            ctk.CTkLabel(row, text=item.get("type", "-"), width=100, anchor="w", font=("Arial", 11)).pack(side="left", padx=2)
            
            ctk.CTkLabel(row, text=item.get("diam", "-"), width=40, anchor="center").pack(side="left", padx=2)
            ctk.CTkLabel(row, text=item.get("z", "-"), width=30, anchor="center").pack(side="left", padx=2)
            ctk.CTkLabel(row, text=item.get("qty", "-"), width=40, anchor="center").pack(side="left", padx=2)
            
            # 2. Ostrzenie (J / Σ)
            ctk.CTkLabel(row, text=f"{get_v('tool_unit'):.2f}", width=80, anchor="center").pack(side="left", padx=2)
            ctk.CTkLabel(row, text=f"{s_tool:.2f}", width=80, anchor="center", text_color="#aaa").pack(side="left", padx=2)
            
            # 3. Powłoka (Nazwa / L / J)
            has_c = item.get("coat_name") != "Brak"
            ctk.CTkLabel(
                row, 
                text=item.get("coat_name", "Brak"), 
                width=100, 
                anchor="center",
                wraplength=95,    
                justify="center" 
            ).pack(side="left", padx=2, fill="y") 
            
            ctk.CTkLabel(row, text=item.get("coat_len", "-"), width=40, anchor="center").pack(side="left", padx=2)
            ctk.CTkLabel(row, text=f"{get_v('coat_unit'):.2f}" if has_c else "-", width=80, anchor="center").pack(side="left", padx=2)
            
            # 4. Usługi (Statusy C/Z/P)
            status = item.get("services_status", {})
            for s_key in ["ciecie", "opuszczenie", "polerowanie"]:
                val = "+" if status.get(s_key) else "-"
                color = "#28a745" if val == "+" else "#555"
                ctk.CTkLabel(row, text=val, width=35, anchor="center", text_color=color, font=("Arial", 12, "bold")).pack(side="left", padx=2)
            
            # 5. Sumy końcowe (Usługi / Powłoka Razem / SUMA WEW)
            ctk.CTkLabel(row, text=f"{s_extra:.2f}", width=80, anchor="center").pack(side="left", padx=2)
            ctk.CTkLabel(row, text=f"{s_coat:.2f}", width=80, anchor="center", text_color="#3498db").pack(side="left", padx=2)
            ctk.CTkLabel(row, text=f"{suma_wew:.2f} zł", width=100, anchor="center", font=("Arial", 11, "bold"), text_color="#28a745").pack(side="left", padx=2)