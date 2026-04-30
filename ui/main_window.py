import customtkinter as ctk
import database
import sys, os
from ui.price_editor import PriceEditor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class OstrzomatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ostrzomat 2.0")
        self.geometry("1200x720")

        # --- MONITOROWANIE BAZY ---
        self.is_monitoring = False
        self.error_bar = ctk.CTkFrame(self, fg_color="#b22222", height=40)
        self.error_label = ctk.CTkLabel(self.error_bar, text="BRAK BAZY DANYCH! Sprawdź folder 'data'.", text_color="white")
        self.error_label.pack(pady=5)
        
        # --- SIDEBAR (Z Twojego kodu) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=250)
        self.sidebar_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Przycisk Edycji na dole sidebaru
        self.edit_price_btn = ctk.CTkButton(self.sidebar_frame, text="⚙ USTAWIENIA CENNIKA", 
                                             fg_color="#444", hover_color="#666",
                                             command=self.open_price_editor)
        self.edit_price_btn.pack(side="bottom", fill="x", padx=20, pady=20)

        # Sprawdzamy bazę na starcie
        self.check_initial_connection()

    def check_initial_connection(self):
        """Sprawdza połączenie przy uruchomieniu."""
        if not database.is_db_accessible():
            self.show_connection_error()

    def show_connection_error(self):
        """Uruchamia pasek błędu i pętlę sprawdzającą."""
        if not self.is_monitoring:
            self.error_bar.pack(fill="x", side="top")
            self.is_monitoring = True
            self.check_loop()

    def check_loop(self):
        """Pętla 5-sekundowa działająca tylko w błędzie."""
        if database.is_db_accessible():
            self.error_bar.pack_forget()
            self.is_monitoring = False
            print("Połączenie przywrócone.")
        else:
            self.after(5000, self.check_loop)

    def open_price_editor(self):
        """Otwiera okno edytora cen."""
        try:
            # Próba połączenia przed otwarciem edytora
            database.get_connection().close()
            if not hasattr(self, "editor_window") or not self.editor_window.winfo_exists():
                self.editor_window = PriceEditor(self)
            else:
                self.editor_window.focus()
        except (FileNotFoundError, Exception):
            self.show_connection_error()