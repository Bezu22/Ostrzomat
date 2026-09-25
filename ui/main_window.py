import customtkinter as ctk
import os
import re
from tkinter import filedialog
import database as database
import utils.clients_db as clients_db
import utils.cache_manager as cache_manager
import utils.document_exporter as exporter
from utils.price_list_excel import DEFAULT_EXCEL_PATH, import_pricelist

from ui.client_popup import ClientSelectionModal
from ui.cart_table import CartTable
from ui.cart_footer import CartFooter
from ui.calc_window import ToolCalcWindow
from ui.components import OstrzomatPopup
from ui.notes_window import NotesWindow
from ui.style import AppStyle
from logic import cart_logic


class OstrzomatApp(ctk.CTk):
    def __init__(self):
        AppStyle.apply_theme()
        super().__init__()

        self.title("Ostrzomat v0.2")
        self.configure(fg_color=AppStyle.COLOR_BG_DARK)

        # 1. Inicjalizacja bazy klientów, bazy cennika oraz centralnej pamięci RAM (cache_manager)
        clients_db.init_clients_db()
        database.init_db()
        self._price_list_startup_error = None
        if DEFAULT_EXCEL_PATH.exists():
            try:
                import_pricelist(DEFAULT_EXCEL_PATH)
            except Exception as error:
                self._price_list_startup_error = str(error)
        cache_manager.preload_all_cache()
        self._price_list_mtime = None
        self._watch_price_list()

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
        self.cart_table = CartTable(self.content_frame,
            on_notes_click=self.open_notes_editor)
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

        self.btn_special = ctk.CTkButton(
            self.sidebar_frame,
            text="➕ DODAJ SPECJALNE",
            font=AppStyle.FONT_BOLD,
            fg_color=AppStyle.COLOR_PRIMARY,
            hover_color=AppStyle.COLOR_PRIMARY_HOVER,
            text_color=AppStyle.COLOR_TEXT_LIGHT,
            command=lambda: self.open_calc("Specjalne")
        )
        self.btn_special.pack(pady=8, padx=20, fill="x")

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

        self.reload_price_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="↻ SPRAWDŹ I PRZEŁADUJ CENNIK",
            font=AppStyle.FONT_BOLD,
            fg_color=AppStyle.COLOR_SUCCESS,
            hover_color=AppStyle.COLOR_SUCCESS,
            text_color=AppStyle.COLOR_TEXT_LIGHT,
            command=self.reload_price_list
        )
        self.reload_price_btn.pack(side="bottom", fill="x", padx=20, pady=(0, 10))

        # Wczytanie początkowego stanu z pliku cart_cache.json
        self.load_initial_data()
        if self._price_list_startup_error:
            self.after(200, self._show_price_list_startup_error)

    def _show_price_list_startup_error(self):
        OstrzomatPopup(
            self, title="Błąd cennika", type="error",
            message="Nie wczytano zmian z pliku Excel.\n"
                    "Popraw wskazaną komórkę i użyj przeładowania:\n"
                    + self._price_list_startup_error
        )

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
        breakdown = {"qty": 0, "tool": 0.0, "coat": 0.0, "extra": 0.0,
                     "ciecie": 0.0, "opuszczenie": 0.0, "polerowanie": 0.0}
        for item in self.cart_items:
            def clean_val(k):
                return float(str(item.get(k, "0")).replace(' zł', '').replace(',', '.').strip())
            tool_value = clean_val("total_tool")
            coat_value = clean_val("total_coat")
            extra_value = clean_val("total_extra")
            total += tool_value + coat_value + extra_value
            breakdown["qty"] += int(item.get("qty", 0))
            breakdown["tool"] += tool_value
            breakdown["coat"] += coat_value
            breakdown["extra"] += extra_value

            service_values = cart_logic.calculate_service_breakdown(
                item.get("services_status", {}), item.get("services_qty", {}),
                item.get("diam", 0), item.get("qty", 0), item.get("opuszczenie_mult", 1)
            )
            for key in ("ciecie", "opuszczenie", "polerowanie"):
                breakdown[key] += service_values[key]

        self.cart_footer.update_total(total, breakdown)

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
        if not DEFAULT_EXCEL_PATH.exists():
            OstrzomatPopup(
                self, title="Brak cennika", type="error",
                message=f"Nie znaleziono pliku {DEFAULT_EXCEL_PATH}."
            )
            return
        try:
            os.startfile(DEFAULT_EXCEL_PATH)
        except OSError as error:
            OstrzomatPopup(
                self, title="Nie można otworzyć cennika", type="error", message=str(error)
            )

    def reload_price_list(self):
        """Waliduje Excel i podmienia cache cen tylko po poprawnym imporcie."""
        try:
            counts = import_pricelist(DEFAULT_EXCEL_PATH)
            self._price_list_mtime = DEFAULT_EXCEL_PATH.stat().st_mtime_ns
            self._after_price_list_reload(counts)
        except Exception as error:
            OstrzomatPopup(
                self, title="Błąd cennika", type="error",
                message=f"Nie wczytano zmian. Popraw plik Excel:\n{error}"
            )

    def _after_price_list_reload(self, counts):
        summary = "Cennik jest poprawny i został wczytany do bazy.\n" + ", ".join(
            f"{name}: {count}" for name, count in counts.items()
        )
        if not self.cart_items:
            OstrzomatPopup(self, title="Cennik przeładowany", type="success", message=summary)
            return

        OstrzomatPopup(
            self,
            title="Cennik przeładowany",
            type="confirm",
            message=summary + "\n\nCzy przeliczyć istniejące pozycje koszyka według nowych cen?",
            on_confirm=self.recalculate_cart_prices,
        )

    def recalculate_cart_prices(self):
        for item in self.cart_items:
            try:
                quantity = int(str(item.get("qty", 0)).strip())
                diameter_values = re.findall(r"\d+(?:[.,]\d+)?", str(item.get("diam", "")))
                diameter = max(float(value.replace(",", ".")) for value in diameter_values)
                services_qty = item.get("services_qty", {})
                heavy_wear_qty = services_qty.get("zuzycie", 0) if isinstance(services_qty, dict) else 0
                if item.get("tool_category") != "Specjalne":
                    tool_unit, tool_total = cart_logic.calculate_tool_price(
                        item.get("type", ""), item.get("z", ""), diameter, quantity,
                        heavy_wear_qty=heavy_wear_qty,
                    )
                    item["tool_unit"], item["total_tool"] = tool_unit, tool_total
                coat_unit, coat_total = cart_logic.calculate_coating_price(
                    item.get("coat_name", "Brak"), diameter, item.get("coat_len", 0), quantity
                )
                extra_unit, extra_total, _ = cart_logic.calculate_extra_services(
                    item.get("services_status", {}), services_qty, diameter, quantity,
                    opuszczenie_multiplier=item.get("opuszczenie_mult", 1),
                )
                item.update({
                    "coat_unit": coat_unit, "total_coat": coat_total,
                    "extra_unit": extra_unit, "total_extra": extra_total,
                })
            except (TypeError, ValueError):
                continue
        self.refresh_cart_ui()
        self.save_cart_state()

    def _watch_price_list(self):
        """Przeładowuje ceny po zapisaniu poprawnego pliku Excel."""
        try:
            mtime = DEFAULT_EXCEL_PATH.stat().st_mtime_ns
            if self._price_list_mtime is not None and mtime != self._price_list_mtime:
                try:
                    counts = import_pricelist(DEFAULT_EXCEL_PATH)
                    self._after_price_list_reload(counts)
                except Exception as error:
                    print(f"Błąd walidacji cennika Excel: {error}")
            self._price_list_mtime = mtime
        except FileNotFoundError:
            self._price_list_mtime = None
        self.after(1500, self._watch_price_list)

    def open_calc(self, category):
        ToolCalcWindow(self, category)

    def open_notes_editor(self, selected_idx=None):
        """Otwiera okno edycji uwag dla wyznaczonego wiersza z tabeli."""
        if selected_idx is None:
            selected_idx = self.cart_table.get_selected_index()

        if selected_idx is None or selected_idx < 0 or selected_idx >= len(self.cart_items):
            return

        current_item = self.cart_items[selected_idx]
        current_notes = current_item.get("notes", "")

        def save_notes_callback(new_text):
            self.cart_items[selected_idx]["notes"] = new_text
            self.refresh_cart_ui()
            self.save_cart_state()

        NotesWindow(self, current_notes, save_notes_callback)

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