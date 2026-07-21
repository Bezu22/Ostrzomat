import customtkinter as ctk
import utils.clients_db as clients_db
from ui.style import AppStyle

class ClientSelectionModal(ctk.CTkToplevel):
    """
    Okno wyboru i edycji klienta z kompaktową listą.
    """
    def __init__(self, parent, on_client_selected_callback):
        super().__init__(parent)
        
        self.on_client_selected = on_client_selected_callback
        
        self.title("Zarządzanie / Wybór Klienta")
        self.geometry("600x550")
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        
        self.configure(fg_color=AppStyle.COLOR_CARD_BG)
        self.editing_client_id = None  # None = nowy klient, liczba = edycja
        
        self._build_ui()
        self._load_clients_list()

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
        self.tab_form = self.tabview.add("➕ Dodaj / Edytuj")

        self._setup_search_tab()
        self._setup_form_tab()

    def _setup_search_tab(self):
        """Zakładka listy z kompaktowymi wierszami."""
        search_frame = ctk.CTkFrame(self.tab_search, fg_color="transparent")
        search_frame.pack(fill="x", pady=(2, 6))
        
        # POPRAWKA: Usunięto zduplikowane 'font=...' – słownik get_entry_style() sam go dostarcza
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
        """Zakładka formularza (Służy do dodawania LUB edycji)."""
        form_frame = ctk.CTkFrame(self.tab_form, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.entry_name = self._create_form_field(form_frame, "Nazwa / Firma *:", 0)
        self.entry_phone = self._create_form_field(form_frame, "Telefon:", 1)
        self.entry_nip = self._create_form_field(form_frame, "NIP:", 2)
        self.entry_email = self._create_form_field(form_frame, "E-mail:", 3)
        self.entry_address = self._create_form_field(form_frame, "Adres:", 4)
        self.entry_notes = self._create_form_field(form_frame, "Uwagi:", 5)

        self.btn_save_form = ctk.CTkButton(
            form_frame,
            text="ZAPISZ I WYBIERZ",
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
        
        # POPRAWKA: Usunięto zduplikowane 'font=...'
        entry = ctk.CTkEntry(parent, height=30, **AppStyle.get_entry_style())
        entry.grid(row=row, column=1, sticky="ew", pady=3, padx=5)
        parent.grid_columnconfigure(1, weight=1)
        return entry

    def _load_clients_list(self, query=""):
        for widget in self.scroll_list.winfo_children():
            widget.destroy()

        clients = clients_db.search_clients(query) if query else clients_db.get_all_clients()

        if not clients:
            lbl_empty = ctk.CTkLabel(self.scroll_list, text="Brak klientów w bazie.", font=AppStyle.get_normal_font(), text_color=AppStyle.COLOR_TEXT_MUTED)
            lbl_empty.pack(pady=15)
            return

        for idx, client in enumerate(clients):
            base_bg = AppStyle.COLOR_ROW_EVEN if idx % 2 == 0 else AppStyle.COLOR_ROW_ODD
            
            card = ctk.CTkFrame(self.scroll_list, fg_color=base_bg, corner_radius=6, height=38)
            card.pack(fill="x", pady=2, padx=2)

            info_container = ctk.CTkFrame(card, fg_color="transparent")
            info_container.pack(side="left", fill="both", expand=True, padx=8, pady=4)

            # Linia 1: Nazwa
            lbl_name = ctk.CTkLabel(info_container, text=client['name'], font=AppStyle.get_bold_font(), text_color=AppStyle.COLOR_TEXT_LIGHT, anchor="w")
            lbl_name.pack(anchor="w")

            # Linia 2: Tylko Tel i NIP
            sub_info = []
            if client['phone']: sub_info.append(f"Tel: {client['phone']}")
            if client['nip']: sub_info.append(f"NIP: {client['nip']}")
            info_str = " | ".join(sub_info) if sub_info else "Brak danych kontaktowych"

            lbl_sub = ctk.CTkLabel(info_container, text=info_str, font=AppStyle.get_small_font(), text_color=AppStyle.COLOR_TEXT_MUTED, anchor="w")
            lbl_sub.pack(anchor="w")

            # Przyciski po prawej stronie
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(side="right", padx=6, pady=4)

            btn_edit = ctk.CTkButton(
                btn_frame,
                text="✏️",
                width=30,
                height=28,
                font=AppStyle.get_normal_font(),
                fg_color=AppStyle.COLOR_MUTED,
                hover_color=AppStyle.COLOR_MUTED_HOVER,
                command=lambda c=client: self._open_edit_mode(c)
            )
            btn_edit.pack(side="left", padx=2)

            btn_select = ctk.CTkButton(
                btn_frame,
                text="WYBIERZ",
                width=75,
                height=28,
                font=AppStyle.get_bold_font(),
                fg_color=AppStyle.COLOR_SECONDARY,
                hover_color=AppStyle.COLOR_SECONDARY_HOVER,
                text_color=AppStyle.COLOR_TEXT_LIGHT,
                command=lambda c=client: self._select_client(c)
            )
            btn_select.pack(side="left", padx=2)

    def _open_edit_mode(self, client):
        """Wypełnia formularz danymi klienta i przełącza zakładkę."""
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

        self.btn_save_form.configure(text="ZAPISZ ZMIANY I WYBIERZ")
        self.tabview.set("➕ Dodaj / Edytuj")

    def _on_search_change(self, event):
        q = self.entry_search.get().strip()
        self._load_clients_list(q)

    def _select_client(self, client):
        if self.on_client_selected:
            self.on_client_selected(client)
        self.destroy()

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
            client = clients_db.get_client_by_id(self.editing_client_id)
        else:
            new_id = clients_db.add_client(name, phone, nip, email, address, notes)
            client = clients_db.get_client_by_id(new_id)

        self._select_client(client)