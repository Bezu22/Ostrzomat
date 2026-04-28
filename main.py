import customtkinter as ctk
import sqlite3
from price_editor import PriceEditor

class OstrzomatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ostrzomat 2.0")
        self.geometry("1200x720")
        
        # --- SIDEBAR ---
        self.sidebar_frame = ctk.CTkFrame(self, width=250)
        self.sidebar_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Przycisk Edycji na dole sidebaru
        self.edit_price_btn = ctk.CTkButton(self.sidebar_frame, text="⚙ USTAWIENIA CENNIKA", 
                                             fg_color="#444", hover_color="#666",
                                             command=self.open_price_editor)
        self.edit_price_btn.pack(side="bottom", fill="x", padx=20, pady=20)

    def open_price_editor(self):
        # Sprawdzamy, czy okno już nie jest otwarte, żeby nie dublować
        if not hasattr(self, "editor_window") or not self.editor_window.winfo_exists():
            self.editor_window = PriceEditor(self)
        else:
            self.editor_window.focus()

    def save_prices(self, window):
        conn = sqlite3.connect('ostrzomat.db')
        cursor = conn.cursor()
        
        for db_id, row_data in self.entries:
            cursor.execute('''
                UPDATE pricelist SET 
                tool_type=?, blades=?, diam_range=?, price_1=?, price_2_4=?, price_5_10=?, price_11_20=?
                WHERE id=?
            ''', (
                row_data[0].get(), row_data[1].get(), row_data[2].get(),
                row_data[3].get(), row_data[4].get(), row_data[5].get(), row_data[6].get(),
                db_id
            ))
        
        conn.commit()
        conn.close()
        print("Cennik zapisany pomyślnie!")
        window.destroy()

if __name__ == "__main__":
    app = OstrzomatApp()
    app.mainloop()