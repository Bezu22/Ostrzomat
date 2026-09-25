import os
import re
from tkinter import filedialog
import customtkinter as ctk

import database
import utils.document_exporter as exporter
from ui.components import OstrzomatPopup
from ui.style import AppStyle


class ExportReportModal(ctk.CTkToplevel):
    """
    Okno modalne konfiguracji i generowania raportu wyceny.
    
    Pozwala użytkownikowi:
    - Wybrać format raportu (PDF lub MS Word DOCX)
    - Wskazać/nadać numer wyceny (z automatycznym podpowiadaniem kolejnego numeru)
    - Zdecydować o zawartości (dane klienta, logo/nagłówek firmowy, podsumowanie)
    - Wybrać lokalizację zapisu pliku i zapisać raport na dysku
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.title("Generowanie Raportu / Wyceny")
        width, height = 480, 500
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.grab_set()

        # Pobranie sugerowanego kolejnego numeru raportu
        settings = database.get_user_settings()
        default_number = str(settings.get("next_report_number", 115))

        self.configure(fg_color=AppStyle.COLOR_MAIN_BG)

        # Kontener główny z marginesami
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=20)

        # 1. Tytuł okna
        lbl_title = ctk.CTkLabel(
            container,
            text="📄 GENEROWANIE RAPORTU",
            font=AppStyle.get_title_font(),
            text_color=AppStyle.COLOR_TEXT_DARK
        )
        lbl_title.pack(anchor="w", pady=(0, 15))

        # 2. Numer raportu
        lbl_num = ctk.CTkLabel(
            container,
            text="Numer raportu / wyceny:",
            font=AppStyle.get_bold_font(),
            text_color=AppStyle.COLOR_TEXT_DARK
        )
        lbl_num.pack(anchor="w", pady=(0, 3))

        self.entry_number = ctk.CTkEntry(container, width=430, **AppStyle.get_entry_style())
        self.entry_number.insert(0, default_number)
        self.entry_number.pack(anchor="w", pady=(0, 15))

        # 3. Format dokumentu (PDF / DOCX)
        lbl_fmt = ctk.CTkLabel(
            container,
            text="Format pliku:",
            font=AppStyle.get_bold_font(),
            text_color=AppStyle.COLOR_TEXT_DARK
        )
        lbl_fmt.pack(anchor="w", pady=(0, 3))

        self.format_var = ctk.StringVar(value="PDF (*.pdf)")
        self.fmt_segmented = ctk.CTkSegmentedButton(
            container,
            values=["PDF (*.pdf)", "Word (*.docx)"],
            variable=self.format_var,
            selected_color=AppStyle.COLOR_PRIMARY,
            selected_hover_color=AppStyle.COLOR_PRIMARY_HOVER,
            unselected_color=AppStyle.COLOR_BG_LIGHT,
            unselected_hover_color=AppStyle.COLOR_MUTED,
            font=AppStyle.get_bold_font(),
            width=430,
            height=36
        )
        self.fmt_segmented.pack(anchor="w", pady=(0, 15))

        # 4. Sekcja opcji zawartości dokumentu
        lbl_opts = ctk.CTkLabel(
            container,
            text="Elementy zawarte na raporcie:",
            font=AppStyle.get_bold_font(),
            text_color=AppStyle.COLOR_TEXT_DARK
        )
        lbl_opts.pack(anchor="w", pady=(0, 5))

        opts_frame = ctk.CTkFrame(
            container,
            fg_color=AppStyle.COLOR_CARD_BG,
            border_width=1,
            border_color=AppStyle.COLOR_MUTED,
            corner_radius=6
        )
        opts_frame.pack(fill="x", pady=(0, 20), padx=0)

        self.var_client = ctk.BooleanVar(value=True)
        self.var_logo = ctk.BooleanVar(value=True)
        self.var_summary = ctk.BooleanVar(value=True)

        cb_client = ctk.CTkCheckBox(
            opts_frame,
            text="Dane odbiorcy / klienta",
            variable=self.var_client,
            font=AppStyle.get_normal_font(),
            fg_color=AppStyle.COLOR_PRIMARY,
            hover_color=AppStyle.COLOR_PRIMARY_HOVER,
            text_color=AppStyle.COLOR_TEXT_DARK
        )
        cb_client.pack(anchor="w", padx=12, pady=(10, 5))

        cb_logo = ctk.CTkCheckBox(
            opts_frame,
            text="Nagłówek firmowy / logo",
            variable=self.var_logo,
            font=AppStyle.get_normal_font(),
            fg_color=AppStyle.COLOR_PRIMARY,
            hover_color=AppStyle.COLOR_PRIMARY_HOVER,
            text_color=AppStyle.COLOR_TEXT_DARK
        )
        cb_logo.pack(anchor="w", padx=12, pady=5)

        cb_summary = ctk.CTkCheckBox(
            opts_frame,
            text="Tabela podsumowania kosztów",
            variable=self.var_summary,
            font=AppStyle.get_normal_font(),
            fg_color=AppStyle.COLOR_PRIMARY,
            hover_color=AppStyle.COLOR_PRIMARY_HOVER,
            text_color=AppStyle.COLOR_TEXT_DARK
        )
        cb_summary.pack(anchor="w", padx=12, pady=(5, 10))

        # 5. Przyciski akcji na dole
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", side="bottom")

        self.btn_generate = ctk.CTkButton(
            btn_frame,
            text="💾 ZAPISZ RAPORT",
            width=230,
            height=40,
            font=AppStyle.get_bold_font(),
            fg_color=AppStyle.COLOR_SAVE,
            hover_color=AppStyle.COLOR_SAVE_HOVER,
            command=self._execute_export
        )
        self.btn_generate.pack(side="left", padx=(0, 10), expand=True, fill="x")

        self.btn_cancel = ctk.CTkButton(
            btn_frame,
            text="ANULUJ",
            width=140,
            height=40,
            font=AppStyle.get_bold_font(),
            fg_color=AppStyle.COLOR_MUTED,
            hover_color=AppStyle.COLOR_MUTED_HOVER,
            command=self.destroy
        )
        self.btn_cancel.pack(side="right", expand=True, fill="x")

    def _execute_export(self):
        """Przeprowadza proces wyboru ścieżki i generowania raportu."""
        if not getattr(self.parent, "cart_items", None):
            OstrzomatPopup(self, title="Brak danych", message="Koszyk jest pusty!", type="error")
            return

        report_num = self.entry_number.get().strip()
        is_pdf = "pdf" in self.format_var.get().lower()

        ext = ".pdf" if is_pdf else ".docx"
        filter_desc = "Plik PDF" if is_pdf else "Dokument Word"

        # Pobranie i oczyszczenie nazwy klienta do nazwy pliku
        raw_client = getattr(self.parent, "current_client_name", "") or "Klient"
        clean_client = re.sub(r'[\\/*?:"<>|]', '', str(raw_client)).strip()
        clean_client = re.sub(r'\s+', '_', clean_client)
        if not clean_client or clean_client.lower() in ["nieokreslony_klient", "nieokreślony_klient", "nieokreslony", "nieokreślony"]:
            clean_client = "Klient"

        report_suffix = f"_{report_num}" if report_num else ""
        default_filename = f"Wycena_{clean_client}{report_suffix}{ext}"

        # Wyłączamy topmost na czas okna eksploratora, aby nie chował się pod spodem
        self.attributes("-topmost", False)
        try:
            save_path = filedialog.asksaveasfilename(
                parent=self,
                defaultextension=ext,
                filetypes=[(filter_desc, f"*{ext}")],
                initialfile=default_filename
            )
        finally:
            if self.winfo_exists():
                self.attributes("-topmost", True)

        if not save_path:
            return

        try:
            client_id = getattr(self.parent, "current_client_id", None)
            client_info = exporter.fetch_client_data(client_id)
            cart_data = {"items": self.parent.cart_items}

            include_client = self.var_client.get()
            include_logo = self.var_logo.get()
            include_summary = self.var_summary.get()

            if is_pdf:
                exporter.generate_pdf(
                    cart_data=cart_data,
                    client_info=client_info,
                    output_pdf_path=save_path,
                    report_number=report_num,
                    include_client=include_client,
                    include_summary=include_summary,
                    include_logo=include_logo
                )
            else:
                exporter.generate_docx(
                    cart_data=cart_data,
                    client_info=client_info,
                    output_docx_path=save_path,
                    report_number=report_num,
                    include_client=include_client,
                    include_summary=include_summary,
                    include_logo=include_logo
                )

            # Inkrementacja numeru dla kolejnego raportu, jeśli wpisano liczbę
            if report_num.isdigit():
                next_num = int(report_num) + 1
                database.save_user_settings({"next_report_number": next_num})

            self.destroy()
            OstrzomatPopup(
                self.parent,
                title="Sukces",
                message=f"Pomyślnie wygenerowano raport:\n{os.path.basename(save_path)}",
                type="success"
            )

        except Exception as e:
            OstrzomatPopup(
                self,
                title="Błąd generowania",
                message=f"Wystąpił błąd podczas tworzenia pliku:\n{e}",
                type="error"
            )
