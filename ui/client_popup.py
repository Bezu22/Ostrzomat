import customtkinter as ctk
import utils.clients_db as clients_db
from ui.style import AppStyle

class ClientSelectionModal(ctk.CTkToplevel):
    """
    Kompaktowe okno wyboru i edycji klienta, zoptymalizowane pod kątem płynności.
    """
    def __init__(self, parent, on_client_selected_callback, initial_cache=None):
        super().__init__(parent)

        self.parent = parent
        self.on_client_selected = on_client_selected_callback
        self.initial_cache = initial_cache or []

        self.title("Zarządzanie / Wybór Klienta")
        self.geometry("600x550")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.configure(fg_color=AppStyle.COLOR_CARD_BG)
        self.editing_client_id = None

        self._build_ui()

        # OPTYMALIZACJA: Dajemy systemowi 10ms na wyrysowanie tła okna,
        # zanim zaczniemy generować widżety na liście (eliminacja białego błysku)
        self.after(10, self._initial_render)

    def _build_ui(self):
        # Nagłówek
        header_frame = ctk.CTkFrame(self, fg_color=AppStyle.COLOR_HEADER_BG, corner_radius=0, height=45)
        header_frame.pack(fill="x", side="top")

        lbl_title = ctk.CTkLabel(
            header_frame,
            text="👤 Zarządzanie Klientami",
            font=AppStyle.get_title_font(),
            text_color=AppStyle.COLOR_TEXT_LIGHT
        )
        lbl_title.pack(pady=10, padx=15, side="left")

        # Zakładki
        self.tabview = ctk.CTkTabview(
            self,
            segmented_button_selected_color=AppStyle.COLOR_PRIMARY,
            segmented_button_selected_hover_color=AppStyle.COLOR_PRIMARY_HOVER,
            segmented_button_unselected_color=AppStyle.COLOR_MUTED,
            segmented_button_unselected_hover_color=AppStyle.COLOR_MUTED_HOVER,
            text_color=AppStyle.COLOR_TEXT_LIGHT
        )
        self.tabview.pack(fill="both", expand=True, padx=15, pady=10)

        self.tab_search = self.tabview.add("🔍 Wybierz z listy")
        # Zmieniono nazwę zakładki z Dodaj/Edytuj na Dodaj
        self.tab_form = self.tabview.add("➕ Dodaj")

        self._setup_search_tab()
        self._setup_form_tab()

    def _setup_search_tab(self):
        search_frame = ctk.CTkFrame(self.tab_search, fg_color="transparent")
        search_frame.pack(fill="x", pady=(2, 6))

        self.entry_search = ctk.CTkEntry(
            search_frame,
            placeholder_text="Szukaj po nazwie, NIP lub telefonie...",
            height=34,
            **AppStyle.get_entry_style()
        )
        self.entry_search.pack(fill="x", side="top")
        self.entry_search.bind("<KeyRelease>", self._on_search_change)

        self.scroll_list = ctk.CTkScrollableFrame(
            self.tab_search,
            fg_color=AppStyle.COLOR_BG_DARK,
            label_text="Baza Klientów",
            label_text_color=AppStyle.COLOR_TEXT_LIGHT,
            label_font=AppStyle.get_bold_font()
        )
        self.scroll_list.pack(fill="both", expand=True, pady=2)

    def _setup_form_tab(self):
        form_frame = ctk.CTkFrame(self.tab_form, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.entry_name = self._create_form_field(form_frame, "Nazwa / Firma *:", 0)
        self.entry_phone = self._create_form_field(form_frame, "Telefon:", 1)
        self.entry_nip = self._create_form_field(form_frame, "NIP:", 2)
        self.entry_email = self._create_form_field(form_frame, "E-mail:", 3)
        self.entry_address = self._create_form_field(form_frame, "Adres:", 4)
        self.entry_notes = self._create_form_field(form_frame, "Uwagi:", 5)

        # Zmieniono tekst przycisku
        self.btn_save_form = ctk.CTkButton(
            form_frame,
            text="ZAPISZ",
            font=AppStyle.get_bold_font(),
            fg_color=AppStyle.COLOR_PRIMARY,
            hover_color=AppStyle.COLOR_PRIMARY_HOVER,
            text_color=AppStyle.COLOR_TEXT_LIGHT,
            height=38,
            command=self._save_form_client
        )
        self.btn_save_form.grid(row=6, column=0, columnspan=2, pady=15, sticky="ew")

    def _create_form_field(self, parent, label_text, row):
        lbl = ctk.CTkLabel(parent, text=label_text, font=AppStyle.get_normal_font(), text_color=AppStyle.COLOR_TEXT_LIGHT, anchor="w")
        lbl.grid(row=row, column=0, sticky="w", pady=3, padx=5)

        entry = ctk.CTkEntry(parent, height=30, **AppStyle.get_entry_style())
        entry.grid(row=row, column=1, sticky="ew", pady=3, padx=5)
        parent.grid_columnconfigure(1, weight=1)
        return entry

    def _initial_render(self):
        """Pierwsze wyrenderowanie danych z pamięci podręcznej RAM."""
        if self.initial_cache:
            self._render_cards(self.initial_cache)
        else:
            self._load_clients_list()

    def _load_clients_list(self, query=""):
        clients = clients_db.search_clients(query) if query else clients_db.get_all_clients()
        self._render_cards(clients)

    def _render_cards(self, clients):
        """Generuje niezwykle zwarty układ wierszy na liście klientów."""
        for widget in self.scroll_list.winfo_children():
            widget.destroy()

        if not clients:
            lbl_empty = ctk.CTkLabel(
                self.scroll_list, 
                text="Brak klientów w bazie.", 
                font=AppStyle.get_normal_font(), 
                text_color=AppStyle.COLOR_TEXT_MUTED
            )
            lbl_empty.pack(pady=15)
            return

        for idx, client in enumerate(clients):
            base_bg = AppStyle.COLOR_ROW_EVEN if idx % 2 == 0 else AppStyle.COLOR_ROW_ODD

            # 1. Kompaktowa ramka wiersza (wysokość tylko 30px)
            card = ctk.CTkFrame(self.scroll_list, fg_color=base_bg, corner_radius=4, height=30)
            card.pack(fill="x", pady=1, padx=2)

            # 2. Kontener na informacje (układ poziomy)
            info_container = ctk.CTkFrame(card, fg_color="transparent")
            info_container.pack(side="left", fill="both", expand=True, padx=6, pady=1)

            # Główna nazwa klienta
            lbl_name = ctk.CTkLabel(
                info_container, 
                text=client['name'], 
                font=AppStyle.get_bold_font(), 
                text_color=AppStyle.COLOR_TEXT_LIGHT, 
                anchor="w"
            )
            lbl_name.pack(side="left", padx=(0, 8))

            # Dane kontaktowe (tel / NIP) umieszczone tuż obok nazwy w tej samej linii
            sub_info = []
            if client['phone']: sub_info.append(f"Tel: {client['phone']}")
            if client['nip']: sub_info.append(f"NIP: {client['nip']}")
            info_str = f"({ ' | '.join(sub_info) })" if sub_info else ""

            if info_str:
                lbl_sub = ctk.CTkLabel(
                    info_container, 
                    text=info_str, 
                    font=AppStyle.get_small_font(), 
                    text_color=AppStyle.COLOR_TEXT_MUTED, 
                    anchor="w"
                )
                lbl_sub.pack(side="left")

            # 3. Odchudzone przyciski akcji po prawej stronie
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(side="right", padx=4, pady=1)

            # Przycisk edycji (mniejszy i bardziej zwarty)
            btn_edit = ctk.CTkButton(
                btn_frame,
                text="✏️",
                width=24,
                height=22,
                font=AppStyle.get_small_font(),
                fg_color=AppStyle.COLOR_MUTED,
                hover_color=AppStyle.COLOR_MUTED_HOVER,
                command=lambda c=client: self._open_edit_mode(c)
            )
            btn_edit.pack(side="left", padx=1)

            # Zmniejszony przycisk wyboru
            btn_select = ctk.CTkButton(
                btn_frame,
                text="Wybierz",
                width=55,
                height=22,
                font=AppStyle.get_small_font(),
                fg_color=AppStyle.COLOR_SECONDARY,
                hover_color=AppStyle.COLOR_SECONDARY_HOVER,
                text_color=AppStyle.COLOR_TEXT_LIGHT,
                command=lambda c=client: self._select_client(c)
            )
            btn_select.pack(side="left", padx=1)

    def _open_edit_mode(self, client):
        self.editing_client_id = client['id']

        self.entry_name.delete(0, 'end')
        self.entry_name.insert(0, client.get('name', '') or '')

        self.entry_phone.delete(0, 'end')
        self.entry_phone.insert(0, client.get('phone', '') or '')

        self.entry_nip.delete(0, 'end')
        self.entry_nip.insert(0, client.get('nip', '') or '')

        self.entry_email.delete(0, 'end')
        self.entry_email.insert(0, client.get('email', '') or '')

        self.entry_address.delete(0, 'end')
        self.entry_address.insert(0, client.get('address', '') or '')

        self.entry_notes.delete(0, 'end')
        self.entry_notes.insert(0, client.get('notes', '') or '')

        # Zmiana tekstu przycisku i nazwy zakładki przy edycji
        self.btn_save_form.configure(text="ZAPISZ ZMIANY")
        self.tabview.set("➕ Dodaj")

    def _on_search_change(self, event):
        q = self.entry_search.get().strip()
        self._load_clients_list(q)

    def _select_client(self, client):
        if self.on_client_selected:
            self.on_client_selected(client)
        self.destroy()

    def _reset_form(self):
        """Czyści formularz po pomyślnym zapisie klienta i resetuje stan edycji."""
        self.editing_client_id = None
        self.entry_name.delete(0, 'end')
        self.entry_phone.delete(0, 'end')
        self.entry_nip.delete(0, 'end')
        self.entry_email.delete(0, 'end')
        self.entry_address.delete(0, 'end')
        self.entry_notes.delete(0, 'end')
        self.btn_save_form.configure(text="ZAPISZ")

    def _save_form_client(self):
        name = self.entry_name.get().strip()
        if not name:
            self.entry_name.configure(placeholder_text="NAZWA JEST WYMAGANA!")
            return

        phone = self.entry_phone.get().strip()
        nip = self.entry_nip.get().strip()
        email = self.entry_email.get().strip()
        address = self.entry_address.get().strip()
        notes = self.entry_notes.get().strip()

        if self.editing_client_id:
            clients_db.update_client(self.editing_client_id, name, phone, nip, email, address, notes)
        else:
            clients_db.add_client(name, phone, nip, email, address, notes)

        # Odświeżamy wątek tła w oknie głównym po zapisie
        if hasattr(self.parent, 'preload_clients_in_background'):
            self.parent.preload_clients_in_background()

        # Zamiast wybierać klienta i zamykać okno: 
        # 1. Czyścimy formularz
        self._reset_form()
        
        # 2. Odświeżamy listę klientów
        self.entry_search.delete(0, 'end')
        self._load_clients_list()
        
        # 3. Wracamy na zakładkę z listą
        self.tabview.set("🔍 Wybierz z listy")