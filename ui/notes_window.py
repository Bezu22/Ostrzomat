import customtkinter as ctk
from ui.style import AppStyle  # Integracja ze stylem

class NotesWindow(ctk.CTkToplevel):
    def __init__(self, parent, current_text, on_save_callback):
        super().__init__(parent)
        self.parent = parent
        self.on_save_callback = on_save_callback
        
        self.title("Uwagi do pozycji")
        
        width, height = 450, 300
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        self.attributes("-topmost", True)
        self.grab_set()
        self.resizable(False, False)
        
        # Kontener główny (Kolor ramki powiązany z kolorem ostrzeżeń/uwag)
        self.main_frame = ctk.CTkFrame(self, corner_radius=15, border_width=2, border_color=AppStyle.COLOR_WARNING)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Nagłówek
        self.lbl_title = ctk.CTkLabel(self.main_frame, text="ZARZĄDZANIE UWAGAMI", font=AppStyle.get_bold_font(), text_color=AppStyle.COLOR_WARNING)
        self.lbl_title.pack(pady=(15, 5))
        
        # Checkbox aktywujący wpisywanie
        self.has_notes_var = ctk.BooleanVar(value=bool(current_text.strip()))
        self.cb_enable = ctk.CTkCheckBox(
            self.main_frame, 
            text="Dodaj / Edytuj własną uwagę dla tej pozycji", 
            variable=self.has_notes_var,
            command=self.toggle_textbox,
            font=AppStyle.get_normal_font()
        )
        self.cb_enable.pack(pady=10, padx=20, anchor="w")
        
        # Pole tekstowe (Textbox)
        self.txt_notes = ctk.CTkTextbox(self.main_frame, height=100, width=390, font=AppStyle.get_normal_font())
        self.txt_notes.pack(padx=20, pady=5)
        self.txt_notes.insert("0.0", current_text)
        
        # Przyciski dolne
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", padx=20, pady=15)
        
        self.btn_save = ctk.CTkButton(btn_frame, text="ZAPISZ", fg_color=AppStyle.COLOR_SUCCESS, font=AppStyle.get_bold_font(), width=180, command=self.save_notes)
        self.btn_save.pack(side="left", padx=5, expand=True)
        
        self.btn_cancel = ctk.CTkButton(btn_frame, text="ANULUJ", fg_color=AppStyle.COLOR_DANGER, font=AppStyle.get_bold_font(), width=180, command=self.destroy)
        self.btn_cancel.pack(side="right", padx=5, expand=True)
        
        self.toggle_textbox()

    def toggle_textbox(self):
        """Włącza lub wyłącza pole tekstowe w zależności od stanu checkboxa."""
        if self.has_notes_var.get():
            self.txt_notes.configure(state="normal", fg_color=["#F9F9FA", "#1D1E20"])
        else:
            self.txt_notes.configure(state="normal")
            self.txt_notes.delete("0.0", "end")
            self.txt_notes.configure(state="disabled", fg_color=[AppStyle.COLOR_TEXT_MUTED, "#141414"])

    def save_notes(self):
        final_text = self.txt_notes.get("0.0", "end").strip() if self.has_notes_var.get() else ""
        self.on_save_callback(final_text)
        self.destroy()