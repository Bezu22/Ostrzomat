import customtkinter as ctk
from tkinter import messagebox, filedialog
import database as database
from ui.cart_table import CartTable
from ui.cart_footer import CartFooter
from ui.calc_window import ToolCalcWindow
from ui.price_editor import PriceEditor
from ui.components import OstrzomatPopup
from ui.notes_window import NotesWindow
from ui.style import Style

class OstrzomatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Wymuszenie globalnego motywu
        Style.apply_theme()
        
        self.title("Ostrzomat v0.2")
        self.configure(fg_color=Style.COLOR_BG_DARK)
        self.minsize(1450, 800)
        self.after(0, lambda: self.state('zoomed'))

        self.cart_items = []

        # --- UKŁAD GŁÓWNY ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, fg_color=Style.COLOR_SIDEBAR_BG, corner_radius=Style.CORNER_RADIUS)
        self.sidebar_frame.pack(side="left", fill="y", padx=Style.PAD_MEDIUM, pady=Style.PAD_MEDIUM)

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(side="right", fill="both", expand=True, padx=Style.PAD_MEDIUM, pady=Style.PAD_MEDIUM)

        # 1. Nagłówek Klienta
        self.client_frame = ctk.CTkFrame(self.content_frame, height=60, fg_color=Style.COLOR_CARD_BG, corner_radius=Style.CORNER_RADIUS)
        self.client_frame.pack(fill="x", pady=(0, Style.PAD_MEDIUM))
        self.client_name = ctk.CTkLabel(self.client_frame, text="Nieokreślony klient", font=Style.FONT_TITLE, text_color=Style.COLOR_TEXT_DARK)
        self.client_name.pack(side="left", padx=Style.PAD_LARGE, pady=15)

        # 2. Tabela 
        self.cart_table = CartTable(self.content_frame)
        self.cart_table.pack(fill="both", expand=True)

        # 3. Stopka
        self.cart_footer = CartFooter(
            self.content_frame, 
            on_save=self.manual_save_cart, 
            on_load=self.manual_load_cart, 
            on_clear=self.clear_cart,
            on_edit=self.edit_selected_item,
            on_delete=self.delete_selected_item
        )
        self.cart_footer.pack(fill="x", pady=(Style.PAD_MEDIUM, 0))
        
        # --- PRZYCISKI SIDEBAR ---
        self.btn_frez = ctk.CTkButton(
            self.sidebar_frame, 
            text="➕ DODAJ FREZ", 
            font=Style.FONT_BOLD,
            fg_color=Style.COLOR_PRIMARY,
            hover_color=Style.COLOR_PRIMARY_HOVER,
            text_color=Style.COLOR_TEXT_LIGHT,
            command=lambda: self.open_calc("Frezy")
        )
        self.btn_frez.pack(pady=Style.PAD_LARGE, padx=Style.PAD_LARGE, fill="x")

        self.edit_price_btn = ctk.CTkButton(
            self.sidebar_frame, 
            text="⚙ CENNIK", 
            font=Style.FONT_BOLD,
            fg_color=Style.COLOR_SECONDARY, 
            hover_color=Style.COLOR_SECONDARY_HOVER,
            text_color=Style.COLOR_TEXT_LIGHT,
            command=self.open_price_editor
        )
        self.edit_price_btn.pack(side="bottom", fill="x", padx=Style.PAD_LARGE, pady=Style.PAD_LARGE)

        self.load_initial_data()

    def load_initial_data(self):
        client_cache, items_cache = database.load_cart_from_file() 
        self.cart_items = items_cache 
        self.client_name.configure(text=client_cache)
        self.refresh_cart_ui()

    def refresh_cart_ui(self):
        self.cart_table.refresh(self.cart_items)
        
        total = 0.0
        for item in self.cart_items:
            def clean_val(k):
                return float(str(item.get(k, "0")).replace(' zł', '').replace(',', '.').strip())
            
            total += clean_val("total_tool") + clean_val("total_coat") + clean_val("total_extra")
        
        self.cart_footer.update_total(total)

    def add_item_to_cart(self, item):
        self.cart_items.append(item)
        self.refresh_cart_ui()
        database.save_cart_to_file(self.cart_items, self.client_name.cget("text"))

    def edit_selected_item(self):
        selected_idx = self.cart_table.get_selected_index()
        
        if selected_idx is None:
            OstrzomatPopup(
                self,
                title="Brak zaznaczenia",
                message="Proszę najpierw zaznaczyć pozycję w tabeli (klikając na nią), którą chcesz edytować.",
                type="error"
            )
            return
            
        item_data = self.cart_items[selected_idx]
        
        ToolCalcWindow(
            self, 
            tool_category=self.cart_items[selected_idx].get("tool_category", "Frezy"), 
            edit_mode=True, 
            item_data=item_data, 
            item_index=selected_idx
        )

    def delete_selected_item(self):
        selected_idx = self.cart_table.get_selected_index()
        
        if selected_idx is None:
            OstrzomatPopup(
                self,
                title="Brak zaznaczenia",
                message="Proszę wybrać pozycję do usunięcia.",
                type="error"
            )
            return
            
        item = self.cart_items[selected_idx]
        msg = f"Czy na pewno chcesz usunąć pozycję {selected_idx + 1}?\n({item.get('type')} Ø{item.get('diam')})"
        
        def execute_delete():
            self.cart_items.pop(selected_idx)
            self.cart_table.selected_idx = None
            self.refresh_cart_ui()
            database.save_cart_to_file(self.cart_items, self.client_name.cget("text"))
            
        OstrzomatPopup(
            self,
            title="Potwierdzenie usunięcia",
            message=msg,
            type="confirm",
            on_confirm=execute_delete  
        )

    def update_item_in_cart(self, idx, updated_item):
        if 0 <= idx < len(self.cart_items):
            self.cart_items[idx] = updated_item
            self.refresh_cart_ui()
            database.save_cart_to_file(self.cart_items, self.client_name.cget("text"))

    def manual_save_cart(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Projekt Ostrzomat", "*.json")], initialdir="data")
        if path:
            database.save_cart_to_file(self.cart_items, self.client_name.cget("text"), path)
            OstrzomatPopup(
                self, 
                title="Zapis projektu", 
                message="Projekt został pomyślnie zapisany na dysku.", 
                type="success")

    def manual_load_cart(self):
        path = filedialog.askopenfilename(filetypes=[("Projekt Ostrzomat", "*.json")], initialdir="data")
        if path:
            client, items = database.load_cart_from_file(path)
            self.cart_items = items
            self.client_name.configure(text=client)
            self.refresh_cart_ui()
            database.save_cart_to_file(items, client)
            OstrzomatPopup(
                self, 
                title="Wczytanie projektu", 
                message="Projekt został pomyślnie załadowany do koszyka.", 
                type="success"
            )

    def clear_cart(self):
        OstrzomatPopup(
            self,
            title="Czyszczenie koszyka",
            message="Czy na pewno chcesz bezpowrotnie wyczyścić cały koszyk?",
            type="confirm",
            on_confirm=lambda: [
                setattr(self, 'cart_items', []),
                self.refresh_cart_ui(),
                database.save_cart_to_file([], "Nieokreślony klient")
            ]
        )

    def open_price_editor(self):
        if not hasattr(self, "editor_window") or not self.editor_window.winfo_exists():
            self.editor_window = PriceEditor(self)
        else: self.editor_window.focus()

    def open_calc(self, category):
        ToolCalcWindow(self, category)

    def open_notes_editor(self):
        selected_idx = self.cart_table.get_selected_index()
        if selected_idx is None:
            return
            
        current_item = self.cart_items[selected_idx]
        current_notes = current_item.get("notes", "")
        
        def save_notes_callback(new_text):
            self.cart_items[selected_idx]["notes"] = new_text
            self.refresh_cart_ui()
            database.save_cart_to_file(self.cart_items, self.client_name.cget("text"))
            
            OstrzomatPopup(self, title="Sukces", message="Uwaga została pomyślnie zaktualizowana!", type="success")
            
        NotesWindow(self, current_notes, save_notes_callback)