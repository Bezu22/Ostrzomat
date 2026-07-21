import customtkinter as ctk
from ui.style import Style

class OstrzomatPopup(ctk.CTkToplevel):
    def __init__(self, parent, title, message, type="info", on_confirm=None):
        super().__init__(parent)
        self.parent = parent
        self.type = type
        self.on_confirm = on_confirm
        
        self.title(title)
        
        # Kolorystyka i ramka z pliku Style
        if type == "error":
            border_color = Style.COLOR_DANGER
        elif type == "success":
            border_color = Style.COLOR_SUCCESS
        elif type == "confirm":
            border_color = Style.COLOR_WARNING
        else:
            border_color = Style.COLOR_PRIMARY
            
        self.configure(
            fg_color=Style.COLOR_BG_DARK, 
            highlightbackground=border_color, 
            highlightthickness=Style.BORDER_WIDTH
        )
        
        width, height = 400, 180
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        self.attributes("-topmost", True)
        self.grab_set()
        self.resizable(False, False)
        
        self.msg_label = ctk.CTkLabel(
            self, 
            text=message, 
            font=Style.FONT_NORMAL, 
            wraplength=360, 
            justify="center"
        )
        self.msg_label.pack(expand=True, padx=Style.PAD_LARGE, pady=(Style.PAD_LARGE, Style.PAD_MEDIUM))
        
        if self.type == "confirm":
            btn_frame = ctk.CTkFrame(self, fg_color="transparent")
            btn_frame.pack(side="bottom", fill="x", padx=Style.PAD_LARGE, pady=15)
            
            self.btn_yes = ctk.CTkButton(
                btn_frame, 
                text="TAK", 
                fg_color=Style.COLOR_SUCCESS, 
                hover_color=Style.COLOR_SUCCESS_HOVER, 
                width=160, 
                command=self._action_confirm
            )
            self.btn_yes.pack(side="left", padx=Style.PAD_SMALL, expand=True)
            
            self.btn_no = ctk.CTkButton(
                btn_frame, 
                text="NIE", 
                fg_color=Style.COLOR_DANGER, 
                hover_color=Style.COLOR_DANGER_HOVER, 
                width=160,  command=self.destroy
            )
            self.btn_no.pack(side="right", padx=Style.PAD_SMALL, expand=True)
        else:
            self.btn_ok = ctk.CTkButton(
                self, 
                text="OK", 
                fg_color=border_color, 
                width=120, 
                command=self.destroy
            )
            self.btn_ok.pack(side="bottom", pady=15)

    def _action_confirm(self):
        if self.on_confirm:
            self.on_confirm()
        self.destroy()