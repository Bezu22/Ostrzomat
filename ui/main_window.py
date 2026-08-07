import customtkinter as ctk
from tkinter import filedialog
import database as database
import utils.clients_db as clients_db
import utils.cache_manager as cache_manager
import utils.document_exporter as exporter

from ui.client_popup import ClientSelectionModal
from ui.cart_table import CartTable
from ui.cart_footer import CartFooter
from ui.calc_window import ToolCalcWindow
from ui.price_editor import PriceEditor
from ui.components import OstrzomatPopup
from ui.notes_window import NotesWindow
from ui.style import AppStyle


class OstrzomatApp(ctk.CTk):
    def __init__(self):
        AppStyle.apply_theme()
        super().__init__()

        self.title("Ostrzomat v0.2")
        self.configure(fg_color=AppStyle.COLOR_BG_DARK)

        # 1. Inicjalizacja bazy klientów oraz centralnej pamięci RAM (cache_manager)
        clients_db.init_clients_db()
        cache_manager.preload_all_cache()

        self.minsize(1450, 800)
        self.after(0, lambda: self.state('zoomed'))

        # Dane bieżącej sesji w RAM
        self.cart_items = []
        self.current_client_id = None
        self.current_client_name = "Nieokreślony klient"

        # Zapis stanu koszyka przy zamykaniu okna
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- UKŁAD GŁÓWNY ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, fg_color=AppStyle.COLOR_SIDEBAR_BG)
        self.sidebar_frame.pack(side="left", fill="y", padx=AppStyle.PAD_MEDIUM, pady=AppStyle.PAD_MEDIUM)

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(side="right", fill="both", expand=True, padx=AppStyle.PAD_MEDIUM, pady=AppStyle.PAD_MEDIUM)

        # Nagłówek Klienta
        self.client_frame = ctk.CTkFrame(self.content_frame, height=60, fg_color=AppStyle.COLOR_HEADER_BG)
        self.client_frame.pack(fill="x", pady=(0, 10))

        self.client_btn = ctk.CTkButton(
            self.client_frame,
            text=f"👤 Klient: {self.current_client_name}",
            font=AppStyle.FONT_SUBTITLE,
            fg_color="transparent",
            hover_color=AppStyle.COLOR_ROW_HOVER,
            text_color=AppStyle.COLOR_TEXT_DARK,
            anchor="w",
            command=self.open_client_modal
        )
        self.client_btn.pack(side="left", padx=AppStyle.PAD_LARGE, pady=10)

        # Tabela Koszyka
        self.cart_table = CartTable(self.content_frame)
        self.cart_table.pack(fill="both", expand=True)

        # Stopka Koszyka
        self.cart_footer = CartFooter(
            self.content_frame,
            on_save=self.manual_save_cart,
            on_load=self.manual_load_cart,
            on_clear=self.clear_cart,
            on_edit=self.edit_selected_item,
            on_delete=self.delete_selected_item,
            on_export_pdf=self.export_to_pdf,
            on_export_docx=self.export_to_docx
        )
        self.cart_footer.pack(fill="x", pady=(10, 0))

        # Przyciski Sidebar
        self.btn_frez = ctk.CTkButton(
            self.sidebar_frame,
            text="➕ DODAJ FREZ",
            font=AppStyle.FONT_BOLD,
            fg_color=AppStyle.COLOR_PRIMARY,
            hover_color=AppStyle.COLOR_PRIMARY_HOVER,
            text_color=AppStyle.COLOR_TEXT_LIGHT,
            command=lambda: self.open_calc("Frezy")
        )
        self.btn_frez.pack(pady=20, padx=20, fill="x")

        self.btn_drill = ctk.CTkButton(
            self.sidebar_frame,
            text="➕ DODAJ WIERTŁO",
            font=AppStyle.FONT_BOLD,
            fg_color=AppStyle.COLOR_PRIMARY,
            hover_color=AppStyle.COLOR_PRIMARY_HOVER,
            text_color=AppStyle.COLOR_TEXT_LIGHT,
            command=lambda: self.open_calc("Wiertla")
        )
        self.btn_drill.pack(pady=10, padx=20, fill="x")

        self.edit_price_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="⚙ CENNIK",
            font=AppStyle.FONT_BOLD,
            fg_color=AppStyle.COLOR_SECONDARY,
            hover_color=AppStyle.COLOR_SECONDARY_HOVER,
            text_color=AppStyle.COLOR_TEXT_LIGHT,
            command=self.open_price_editor
        )
        self.edit_price_btn.pack(side="bottom", fill="x", padx=20, pady=20)

        # Wczytanie początkowego stanu z pliku cart_cache.json
        self.load_initial_data()

    def on_closing(self):
        """Zapisuje bieżący stan do cart_cache.json i zamyka aplikację."""
        self.save_cart_state()
        self.destroy()

    def open_client_modal(self):
        """Otwiera okno klientów z danymi pobranymi bezpośrednio z cache_manager."""
        if cache_manager.is_clients_loading():
            OstrzomatPopup(self, title="Ładowanie", message="Trwa wczytywanie bazy klientów. Proszę chwilę poczekać.", type="error")
            return

        clients_data = cache_manager.get_cached_clients()
        ClientSelectionModal(
            parent=self, 
            on_client_selected_callback=self.on_client_selected,
            initial_cache=clients_data
        )

    def on_client_selected(self, client_dict):
        if client_dict:
            self.current_client_id = client_dict['id']
            self.current_client_name = client_dict['name']
        else:
            self.current_client_id = None
            self.current_client_name = "Nieokreślony klient"

        self.client_btn.configure(text=f"👤 Klient: {self.current_client_name}")
        self.save_cart_state()

    def load_initial_data(self):
        """Wczytuje z dysku (JSON) zapisany stan koszyka oraz wybranego klienta."""
        cart_data = database.load_cart_from_file()
        self.cart_items = cart_data.get("items", [])
        self.current_client_id = cart_data.get("client_id")

        if self.current_client_id:
            client = clients_db.get_client_by_id(self.current_client_id)
            if client:
                self.current_client_name = client['name']
            else:
                self.current_client_name = cart_data.get("client_name", "Nieokreślony klient")
        else:
            self.current_client_name = cart_data.get("client_name", "Nieokreślony klient")

        self.client_btn.configure(text=f"👤 Klient: {self.current_client_name}")
        self.refresh_cart_ui()

    def save_cart_state(self, path=database.CART_CACHE_PATH):
        """Zapisuje stan koszyka i klienta do pliku cart_cache.json."""
        database.save_cart_to_file(
            cart_items=self.cart_items,
            client_id=self.current_client_id,
            client_name=self.current_client_name,
            path=path
        )

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
        self.save_cart_state()

    def edit_selected_item(self):
        selected_idx = self.cart_table.get_selected_index()
        if selected_idx is None:
            OstrzomatPopup(self, title="Brak zaznaczenia", message="Proszę najpierw zaznaczyć pozycję w tabeli.", type="error")
            return

        item_data = self.cart_items[selected_idx]
        ToolCalcWindow(self, tool_category=item_data.get("tool_category", "Frezy"), edit_mode=True, item_data=item_data, item_index=selected_idx)

    def delete_selected_item(self):
        selected_idx = self.cart_table.get_selected_index()
        if selected_idx is None:
            OstrzomatPopup(self, title="Brak zaznaczenia", message="Proszę wybrać pozycję do usunięcia.", type="error")
            return

        item = self.cart_items[selected_idx]
        msg = f"Czy na pewno chcesz usunąć pozycję {selected_idx + 1}?\n({item.get('type')} Ø{item.get('diam')})"

        def execute_delete():
            self.cart_items.pop(selected_idx)
            self.cart_table.selected_idx = None
            self.refresh_cart_ui()
            self.save_cart_state()

        OstrzomatPopup(self, title="Potwierdzenie usunięcia", message=msg, type="confirm", on_confirm=execute_delete)

    def update_item_in_cart(self, idx, updated_item):
        if 0 <= idx < len(self.cart_items):
            self.cart_items[idx] = updated_item
            self.refresh_cart_ui()
            self.save_cart_state()

    def manual_save_cart(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Projekt Ostrzomat", "*.json")], initialdir="data")
        if path:
            self.save_cart_state(path=path)
            OstrzomatPopup(self, title="Zapis projektu", message="Projekt został pomyślnie zapisany na dysku.", type="success")

    def manual_load_cart(self):
        path = filedialog.askopenfilename(filetypes=[("Projekt Ostrzomat", "*.json")], initialdir="data")
        if path:
            cart_data = database.load_cart_from_file(path)
            self.cart_items = cart_data.get("items", [])
            self.current_client_id = cart_data.get("client_id")

            if self.current_client_id:
                client = clients_db.get_client_by_id(self.current_client_id)
                if client:
                    self.current_client_name = client['name']
                else:
                    self.current_client_name = cart_data.get("client_name", "Nieokreślony klient")
            else:
                self.current_client_name = cart_data.get("client_name", "Nieokreślony klient")

            self.client_btn.configure(text=f"👤 Klient: {self.current_client_name}")
            self.refresh_cart_ui()
            self.save_cart_state()
            OstrzomatPopup(self, title="Wczytanie projektu", message="Projekt został pomyślnie załadowany do koszyka.", type="success")

    def clear_cart(self):
        OstrzomatPopup(
            self,
            title="Czyszczenie koszyka",
            message="Czy na pewno chcesz bezpowrotnie wyczyścić cały koszyk?",
            type="confirm",
            on_confirm=lambda: [
                setattr(self, 'cart_items', []),
                setattr(self, 'current_client_id', None),
                setattr(self, 'current_client_name', "Nieokreślony klient"),
                self.client_btn.configure(text="👤 Klient: Nieokreślony klient"),
                self.refresh_cart_ui(),
                self.save_cart_state()
            ]
        )

    def open_price_editor(self):
        if not hasattr(self, "editor_window") or not self.editor_window.winfo_exists():
            self.editor_window = PriceEditor(self)
        else:
            self.editor_window.focus()

    def open_calc(self, category):
        ToolCalcWindow(self, category)

    def export_to_pdf(self):
        if not self.cart_items:
            OstrzomatPopup(self, title="Brak danych", message="Koszyk jest pusty!", type="error")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Plik PDF", "*.pdf")],
            initialfile=f"Wycena_Klient_{self.current_client_id or 0}.pdf"
        )
        if path:
            try:
                client_info = exporter.fetch_client_data(self.current_client_id)
                cart_data = {"items": self.cart_items}
                exporter.generate_pdf(cart_data, client_info, path)
                OstrzomatPopup(self, title="Sukces", message="Pomyślnie wygenerowano plik PDF!", type="success")
            except Exception as e:
                OstrzomatPopup(self, title="Błąd", message=f"Błąd generowania PDF:\n{e}", type="error")

    def export_to_docx(self):
        if not self.cart_items:
            OstrzomatPopup(self, title="Brak danych", message="Koszyk jest pusty!", type="error")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Dokument Word", "*.docx")],
            initialfile=f"Wycena_Klient_{self.current_client_id or 0}.docx"
        )
        if path:
            try:
                client_info = exporter.fetch_client_data(self.current_client_id)
                cart_data = {"items": self.cart_items}
                exporter.generate_docx(cart_data, client_info, path)
                OstrzomatPopup(self, title="Sukces", message="Pomyślnie wygenerowano plik MS Word!", type="success")
            except Exception as e:
                OstrzomatPopup(self, title="Błąd", message=f"Błąd generowania DOCX:\n{e}", type="error")