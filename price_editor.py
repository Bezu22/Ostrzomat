import customtkinter as ctk
import sqlite3
from tkinter import messagebox

class PriceEditor(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Panel Zarządzania Cennikiem")
        self.geometry("1100x700")
        
        self.selected_row_data = None
        self.selected_frame = None
        self.all_rows = []

        # --- PANEL STEROWANIA ---
        self.top_panel = ctk.CTkFrame(self)
        self.top_panel.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(self.top_panel, text="Dodaj Nowy", fg_color="green", width=120,
                      command=self.add_new).pack(side="left", padx=5)
        
        self.edit_btn = ctk.CTkButton(self.top_panel, text="Edytuj Zaznaczone", state="disabled",
                                      command=self.open_edit_form)
        self.edit_btn.pack(side="left", padx=5)
        
        ctk.CTkButton(self.top_panel, text="Usuń", fg_color="#922", width=100,
                      command=self.delete_selected).pack(side="right", padx=5)

        # --- NAGŁÓWKI TABELI ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20)
        headers = ["Typ", "Ostrza", "Zakres Ø", "1 szt", "2-4 szt", "5-10 szt", "11-20 szt"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(self.header_frame, text=h, font=("Arial", 12, "bold"), width=140).grid(row=0, column=i, padx=2)

        # --- LISTA DANYCH (Scrollable) ---
        self.table_container = ctk.CTkScrollableFrame(self, fg_color="#222")
        self.table_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.refresh_table()

    def refresh_table(self):
        """Czyści i ładuje dane z bazy jako klikalne wiersze."""
        for child in self.table_container.winfo_children():
            child.destroy()
        self.all_rows = []
        
        conn = sqlite3.connect('ostrzomat.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pricelist")
        
        for idx, data in enumerate(cursor.fetchall()):
            row_frame = ctk.CTkFrame(self.table_container, fg_color="transparent", corner_radius=0)
            row_frame.pack(fill="x", pady=1)
            
            # Tworzymy widok wiersza (Labels zamiast Entries)
            # data[0] to ID, reszta to wartości
            for i, val in enumerate(data[1:]):
                lbl = ctk.CTkLabel(row_frame, text=str(val), width=140)
                lbl.grid(row=0, column=i, padx=2)
                # Bindowanie kliknięcia do każdego elementu wiersza
                lbl.bind("<Button-1>", lambda e, d=data, f=row_frame: self.select_row(d, f))

            row_frame.bind("<Button-1>", lambda e, d=data, f=row_frame: self.select_row(d, f))
            self.all_rows.append((row_frame, data))
            
        conn.close()

    def select_row(self, data, frame):
        """Podświetla wybrany wiersz i aktywuje przyciski."""
        if self.selected_frame:
            self.selected_frame.configure(fg_color="transparent")
        
        self.selected_row_data = data
        self.selected_frame = frame
        self.selected_frame.configure(fg_color="#3b3b3b") # Kolor zaznaczenia
        
        self.edit_btn.configure(state="normal")

    def open_edit_form(self):
        """Otwiera małe okno z formularzem edycji dla JEDNEGO wiersza."""
        if not self.selected_row_data: return
        
        form = ctk.CTkToplevel(self)
        form.title("Edycja pozycji")
        form.geometry("400x550")
        form.attributes("-topmost", True)

        fields = ["Typ", "Ostrza", "Zakres", "Cena 1", "Cena 2-4", "Cena 5-10", "Cena 11-20"]
        entries = []

        for i, label_text in enumerate(fields):
            ctk.CTkLabel(form, text=label_text).pack(pady=(10, 0))
            e = ctk.CTkEntry(form, width=250)
            e.insert(0, str(self.selected_row_data[i+1]))
            e.pack(pady=5)
            entries.append(e)

        def save_and_close():
            try:
                new_vals = [e.get() for e in entries]
                # Tu dodalibyśmy walidację (float)
                conn = sqlite3.connect('ostrzomat.db')
                cursor = conn.cursor()
                cursor.execute('''UPDATE pricelist SET 
                                  tool_type=?, blades=?, diam_range=?, 
                                  price_1=?, price_2_4=?, price_5_10=?, price_11_20=? 
                                  WHERE id=?''', (*new_vals, self.selected_row_data[0]))
                conn.commit()
                conn.close()
                form.destroy()
                self.refresh_table()
            except Exception as e:
                messagebox.showerror("Błąd", str(e))

        ctk.CTkButton(form, text="Zapisz", fg_color="green", command=save_and_close).pack(pady=20)

    def delete_selected(self):
        if not self.selected_row_data: return
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno usunąć ten wiersz?"):
            conn = sqlite3.connect('ostrzomat.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM pricelist WHERE id=?", (self.selected_row_data[0],))
            conn.commit()
            conn.close()
            self.refresh_table()

    def add_new(self):
        # Logika dodawania nowego rekordu (pusty formularz)
        # Podobna do open_edit_form, ale z INSERT zamiast UPDATE
        pass