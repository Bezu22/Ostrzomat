import customtkinter as ctk
from ui.style import AppStyle

class DrillModule(ctk.CTkFrame):
    """
    Moduł do kalkulacji i zarządzania wiertłami.
    Na tym etapie tworzymy podstawowy widok (stub).
    """
    def __init__(self, parent, cart_manager):
        super().__init__(parent, fg_color="transparent")
        
        self.cart_manager = cart_manager
        self._build_ui()

    def _build_ui(self):
        # Nagłówek tymczasowy dla modułu wierteł
        lbl_title = ctk.CTkLabel(
            self, 
            text="🔩 Moduł Wiertła (w budowie)", 
            font=AppStyle.get_total_font(),
            text_color=AppStyle.COLOR_PRIMARY
        )
        lbl_title.pack(padx=20, pady=20, anchor="w")

    def reset_form(self):
        """Metoda wywoływana przy czyszczeniu formularza (interfejs spójny z FrezModule)."""
        pass