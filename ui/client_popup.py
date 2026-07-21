import customtkinter as ctk
import utils.clients_db as clients_db
from ui.style import AppStyle

class ClientSelectionModal(ctk.CTkToplevel):
    """
    Okno popup do wyboru lub szybkiego dodawania klienta.
    Dostosowane do spójnego motywu AppStyle.
    """
    def __init__(self, parent, on_client_selected_callback):
        super().__init__(parent)
        
        self.on_client_selected = on_client_selected_callback
        
        self.title("Zarządzanie / Wybór Klienta")
        self.geometry("600x550")
        self.resizable(False, False)
        
        # Okno zawsze na wierzchu i blokujące okno główne
        self.transient(parent)
        self.grab_set()
        
        self.configure(fg_color=AppStyle.COLOR_CARD_BG)
        
        self.selected_client_id = None
        
        self._build_ui()
        self._load_clients_list()

    def _build_ui(self):
        # --- NAGŁÓWEK ---
        header_frame = ctk.CTkFrame(self, fg_color=AppStyle.COLOR_HEADER_BG, corner_radius=0, height=45)
        header_frame.pack(fill="x", side="top")
        
        lbl_title = ctk.CTkLabel(
            header_frame, 
            text="👤 Wybór Klienta", 
            font=(AppStyle.FONT_FAMILY, int(AppStyle.BASE_FONT_SIZE * 1.2), "bold"), 
            text_color=AppStyle.COLOR_TEXT_DARK
        )
        lbl_title.pack(pady=10, padx=15, side="left")

        # --- ZAKŁADKI (WYBÓR / NOWY) ---
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
        self.tab_add = self.tabview.add("➕ Dodaj nowego klienta")

        self._setup_search_tab()
        self._setup_add_tab()

    def _setup_search_tab(self):
        """Zakładka wyszukiwania z listą."""
        search_frame = ctk.CTkFrame(self.tab_search, fg_color="transparent")
        search_frame.pack(fill="x", pady=(5, 10))
        
        self.entry_search = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Wpisz nazwę, NIP lub telefon...",
            font=AppStyle.get_normal_font(),
            height=35
        )
        self.entry_search.pack(fill="x", side="top")
        self.entry_search.bind("<KeyRelease>", self._on_search_change)

        # Scrollowalna lista klientów
        self.scroll_list = ctk.CTkScrollableFrame(
            self.tab_search, 
            fg_color=AppStyle.COLOR_ROW_EVEN,
            label_text="Baza Klientów",
            label_text_color=AppStyle.COLOR_TEXT_DARK,
            label_font=AppStyle.get_bold_font()
        )
        self.scroll_list.pack(fill="both", expand=True, pady=5)

    def _setup_add_tab(self):
        """Zakładka formularza tworzenia nowego klienta."""
        form_frame = ctk.CTkFrame(self.tab_add, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Pola formularza
        self.entry_name = self._create_form_field(form_frame, "Nazwa / Imię i Nazwisko *:", 0)
        self.entry_phone = self._create_form_field(form_frame, "Telefon:", 1)
        self.entry_nip = self._create_form_field(form_frame, "NIP:", 2)
        self.entry_email = self._create_form_field(form_frame, "E-mail:", 3)
        self.entry_address = self._create_form_field(form_frame, "Adres:", 4)
        self.entry_notes = self._create_form_field(form_frame, "Uwagi:", 5)

        # Przycisk Zapisz
        btn_save = ctk.CTkButton(
            form_frame,
            text="Zapisz i Wybierz",
            font=AppStyle.get_bold_font(),
            fg_color=AppStyle.COLOR_PRIMARY,
            hover_color=AppStyle.COLOR_PRIMARY_HOVER,
            text_color=AppStyle.COLOR_TEXT_LIGHT,
            height=40,
            command=self._save_new_client
        )
        btn_save.grid(row=6, column=0, columnspan=2, pady=15, sticky="ew")

    def _create_form_field(self, parent, label_text, row):
        lbl = ctk.CTkLabel(parent, text=label_text, font=AppStyle.get_normal_font(), text_color=AppStyle.COLOR_TEXT_DARK, anchor="w")
        lbl.grid(row=row, column=0, sticky="w", pady=4, padx=5)
        
        entry = ctk.CTkEntry(parent, font=AppStyle.get_normal_font(), height=30)
        entry.grid(row=row, column=1, sticky="ew", pady=4, padx=5)
        parent.grid_columnconfigure(1, weight=1)
        return entry

    def _load_clients_list(self, query=""):
        # Czyszczenie listy
        for widget in self.scroll_list.winfo_children():
            widget.destroy()

        clients = clients_db.search_clients(query) if query else clients_db.get_all_clients()

        if not clients:
            lbl_empty = ctk.CTkLabel(
                self.scroll_list, 
                text="Brak klientów w bazie.", 
                font=AppStyle.get_normal_font(), 
                text_color=AppStyle.COLOR_TEXT_MUTED
            )
            lbl_empty.pack(pady=20)
            return

        for idx, client in enumerate(clients):
            bg_col = AppStyle.COLOR_ROW_EVEN if idx % 2 == 0 else AppStyle.COLOR_ROW_ODD
            
            card = ctk.CTkFrame(self.scroll_list, fg_color=bg_col, corner_radius=6)
            card.pack(fill="x", pady=3, padx=5)

            # Podstawowe info
            sub_info = []
            if client['phone']: sub_info.append(f"Tel: {client['phone']}")
            if client['nip']: sub_info.append(f"NIP: {client['nip']}")
            info_str = " | ".join(sub_info) if sub_info else "Brak dodatkowych danych"

            info_container = ctk.CTkFrame(card, fg_color="transparent")
            info_container.pack(side="left", fill="both", expand=True, padx=10, pady=5)

            lbl_name = ctk.CTkLabel(info_container, text=client['name'], font=AppStyle.get_bold_font(), text_color=AppStyle.COLOR_TEXT_DARK, anchor="w")
            lbl_name.pack(anchor="w")

            lbl_sub = ctk.CTkLabel(info_container, text=info_str, font=(AppStyle.FONT_FAMILY, int(AppStyle.BASE_FONT_SIZE * 0.85)), text_color=AppStyle.COLOR_TEXT_MUTED, anchor="w")
            lbl_sub.pack(anchor="w")

            # Przycisk Wybierz dla danego klienta
            btn_select = ctk.CTkButton(
                card,
                text="Wybierz",
                width=80,
                height=28,
                font=AppStyle.get_bold_font(),
                fg_color=AppStyle.COLOR_SECONDARY,
                hover_color=AppStyle.COLOR_SECONDARY_HOVER,
                text_color=AppStyle.COLOR_TEXT_LIGHT,
                command=lambda c=client: self._select_client(c)
            )
            btn_select.pack(side="right", padx=10, pady=5)

    def _on_search_change(self, event):
        q = self.entry_search.get().strip()
        self._load_clients_list(q)

    def _select_client(self, client):
        """Zwraca wybranego klienta do okna głównego i zamyka popup."""
        if self.on_client_selected:
            self.on_client_selected(client)
        self.destroy()

    def _save_new_client(self):
        name = self.entry_name.get().strip()
        if not name:
            self.entry_name.configure(placeholder_text="NAZWA JEST WYMAGANA!")
            return

        phone = self.entry_phone.get().strip()
        nip = self.entry_nip.get().strip()
        email = self.entry_email.get().strip()
        address = self.entry_address.get().strip()
        notes = self.entry_notes.get().strip()

        new_id = clients_db.add_client(name, phone, nip, email, address, notes)
        new_client = clients_db.get_client_by_id(new_id)
        
        self._select_client(new_client)