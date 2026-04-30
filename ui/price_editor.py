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

        # Powiadomienie statusu na froncie
        self.status_label = ctk.CTkLabel(self.top_bar, text="", font=("Arial", 12, "bold"))
        self.status_label.pack(side="right", padx=20)

        ctk.CTkButton(self.top_bar, text="+ DODAJ", fg_color="#28a745", width=100, command=lambda: self.open_edit_form(is_new=True)).pack(side="right", padx=10)

        # --- NAGŁÓWKI ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=5)

        # --- LISTA (SCROLLABLE) ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#1a1a1a")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.on_main_cat_change()

    def show_status(self, message, color="#28a745"):
        """Wyświetla krótki komunikat na froncie i ukrywa go po 3s."""
        self.status_label.configure(text=message, text_color=color)
        self.after(3000, lambda: self.status_label.configure(text=""))

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
        """Bezpiecznie odświeża listę rekordów."""
        self.selected_row_data = None
        self.btn_edit.configure(state="disabled")
        self.btn_delete.configure(state="disabled")
        
        self.scroll_frame.update_idletasks()
        for child in self.scroll_frame.winfo_children():
            child.pack_forget()
            child.destroy()
        
        # Resetowanie pozycji przewijania
        canvas = getattr(self.scroll_frame, "_parent_canvas", None)
        if canvas: canvas.yview_moveto(0)

        cat = self.main_cat_combo.get()
        filt = self.sub_filter_combo.get()

        if cat == "Narzędzia":
            data = database.get_filtered_tools(filt, "Wszystkie")
            col_widths, d_slice = [180, 100, 80, 80, 80, 80, 80, 80], slice(2, 10)
        elif cat == "Powłoki":
            data = database.get_filtered_coatings(filt)
            col_widths, d_slice = [250, 120, 120, 120], slice(1, 5)
        else:
            data = database.get_filtered_services(filt)
            col_widths, d_slice = [250, 150, 150, 120], slice(1, 5)

        for index, row in enumerate(data):
            self.render_row_item(row, index % 2 == 0, col_widths, d_slice)

    def render_row_item(self, row, is_even, widths, d_slice):
        bg = "transparent" if is_even else "#2b2b2b"
        f = ctk.CTkFrame(self.scroll_frame, fg_color=bg, corner_radius=0)
        f.pack(fill="x", pady=0, padx=5)
        f.original_bg = bg

        display_data = row[d_slice]
        limit = min(len(display_data), len(widths))

        for i in range(limit):
            lbl = ctk.CTkLabel(f, text=str(display_data[i]), width=widths[i], anchor="w")
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
        if messagebox.askyesno("Usuń", "Na pewno usunąć wybrany rekord?"):
            database.delete_row(table, self.selected_row_data[0])
            self.refresh_list()
            self.show_status("REKORD USUNIĘTY", color="#dc3545")

    def open_edit_form(self, is_new=False):
        cat = self.main_cat_combo.get()
        data = self.selected_row_data if (is_new or self.selected_row_data) else None
        
        form = ctk.CTkToplevel(self)
        mode = "Nowy (na wzór)" if is_new and data else "Nowy" if is_new else "Edycja"
        form.title(f"{cat} - {mode}")
        form.geometry("500x850")
        form.attributes("-topmost", True)
        form.grab_set()

        if cat == "Narzędzia":
            labels = ["Kategoria", "Typ narzędzia", "Ostrza", "Ø MIN", "Ø MAX", "Cena 1", "Cena 2-4", "Cena 5-10", "Cena 11+"]
            db_slice = slice(1, 10)
        elif cat == "Powłoki":
            labels = ["Nazwa powłoki", "Ø MAX", "Długość", "Cena"]
            db_slice = slice(1, 5)
        else:
            labels = ["Nazwa usługi", "Param MIN", "Param MAX", "Cena"]
            db_slice = slice(1, 5)

        entries = []
        for i, txt in enumerate(labels):
            ctk.CTkLabel(form, text=txt, font=("Arial", 12, "bold")).pack(pady=(10, 0))
            e = ctk.CTkEntry(form, width=350)
            if data:
                try:
                    e.insert(0, str(data[db_slice][i]))
                except IndexError: pass
            e.pack(pady=5)
            entries.append(e)

        def save_action():
            try:
                vals = [e.get().strip().replace(',', '.') for e in entries]
                if cat == "Narzędzia":
                    if is_new: database.add_tool_row(vals)
                    else: database.update_tool_row(data[0], vals)
                elif cat == "Powłoki":
                    if is_new: database.add_coating_row(vals)
                    else: database.update_coating_row(data[0], vals)
                else:
                    if is_new: database.add_service_row(vals)
                    else: database.update_service_row(data[0], vals)
                
                form.destroy()
                self.refresh_list()
                self.show_status("ZAPISANO POMYŚLNIE!")
            except Exception as ex:
                self.show_status(f"BŁĄD: {ex}", color="#dc3545")

        ctk.CTkButton(form, text="ZAPISZ ZMIANY", fg_color="#28a745", height=40, font=("Arial", 13, "bold"), command=save_action).pack(pady=30, padx=20, fill="x")