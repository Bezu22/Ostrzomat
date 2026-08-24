import customtkinter as ctk
from ui.style import AppStyle

class CartFooter(ctk.CTkFrame):
    def __init__(self, parent, on_save, on_load, on_clear, on_edit, on_delete, on_export_pdf=None, on_export_docx=None):
        super().__init__(parent, fg_color=AppStyle.COLOR_HEADER_BG, height=90, corner_radius=8)
        
        self.on_save = on_save
        self.on_load = on_load
        self.on_clear = on_clear
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_export_pdf = on_export_pdf
        self.on_export_docx = on_export_docx

        self._build_ui()

    def _build_ui(self):
        # ----------------------------------------------------------------------
        # LEWA STRONA: PRZYCISKI W KOLUMNACH (Bez zmian)
        # ----------------------------------------------------------------------
        left_container = ctk.CTkFrame(self, fg_color="transparent")
        left_container.pack(side="left", padx=15, pady=4, fill="y")

        # Kolumna 1: Edytuj / Usuń
        col1 = ctk.CTkFrame(left_container, fg_color="transparent")
        col1.pack(side="left", padx=(0, 10), fill="y")

        self.btn_edit = ctk.CTkButton(
            col1, text="✏️ EDYTUJ", width=100, height=40,
            font=AppStyle.get_bold_font(), fg_color=AppStyle.COLOR_SECONDARY,
            hover_color=AppStyle.COLOR_SECONDARY_HOVER, command=self.on_edit
        )
        self.btn_edit.pack(side="top", pady=(15, 3))

        self.btn_delete = ctk.CTkButton(
            col1, text="🗑️ USUŃ", width=100, height=40,
            font=AppStyle.get_bold_font(), fg_color=AppStyle.COLOR_DANGER,
            hover_color=AppStyle.COLOR_DANGER_HOVER, command=self.on_delete
        )
        self.btn_delete.pack(side="top")

        # Kolumna 2: Zapisz / Wczytaj z nowymi kolorami
        col2 = ctk.CTkFrame(left_container, fg_color="transparent")
        col2.pack(side="left", padx=(0, 10), fill="y")

        btn_save = ctk.CTkButton(
            col2, text="💾 ZAPISZ", width=100, height=40,
            font=AppStyle.get_bold_font(),
            fg_color=AppStyle.COLOR_SAVE,
            hover_color=AppStyle.COLOR_SAVE_HOVER,
            command=self.on_save
        )
        btn_save.pack(side="top", pady=(15, 4))

        btn_load = ctk.CTkButton(
            col2, text="📂 WCZYTAJ", width=100, height=40,
            font=AppStyle.get_bold_font(),
            fg_color=AppStyle.COLOR_LOAD,
            hover_color=AppStyle.COLOR_LOAD_HOVER,
            command=self.on_load
        )
        btn_load.pack(side="top")

        # Kolumna 3: Wyczyść z nowym kolorem
        col3 = ctk.CTkFrame(left_container, fg_color="transparent")
        col3.pack(side="left", fill="y")

        btn_clear = ctk.CTkButton(
            col3, text="🧹 WYCZYŚĆ", width=100, height=64,
            font=AppStyle.get_bold_font(),
            fg_color=AppStyle.COLOR_CLEAR,
            hover_color=AppStyle.COLOR_CLEAR_HOVER,
            command=self.on_clear
        )
        btn_clear.pack(side="top", pady=(15, 0))

        # ----------------------------------------------------------------------
        # PRAWA STRONA: szczegółowe podsumowanie oraz kwota końcowa
        # ----------------------------------------------------------------------
        right_container = ctk.CTkFrame(self, fg_color="transparent")
        right_container.pack(side="right", padx=15, pady=2, fill="y")

        # Podsumowanie ma osobną hierarchię: główne wartości oraz szczegóły usług.
        breakdown_frame = ctk.CTkFrame(
            right_container, fg_color=AppStyle.COLOR_CARD_BG,
            border_width=1, border_color=AppStyle.COLOR_MUTED, corner_radius=6
        )
        breakdown_frame.pack(side="left", padx=(0, 16), pady=1, fill="y")

        heading = ctk.CTkLabel(
            breakdown_frame, text="PODSUMOWANIE", anchor="w",
            font=AppStyle.get_footer_label_font(), text_color=AppStyle.COLOR_TEXT_MUTED
        )
        heading.pack(fill="x", padx=8, pady=(2, 0))

        metrics_frame = ctk.CTkFrame(breakdown_frame, fg_color="transparent")
        metrics_frame.pack(fill="x", padx=8)
        self.breakdown_labels = {}
        for key, label_text, value_text in (
            ("qty", "SZTUK", "0"),
            ("tool", "OSTRZENIE", "0.00 zł"),
            ("coat", "POWLEKANIE", "0.00 zł"),
            ("extra", "USŁUGI", "0.00 zł"),
        ):
            metric = ctk.CTkFrame(metrics_frame, fg_color="transparent")
            metric.pack(side="left", padx=(0, 12))
            ctk.CTkLabel(
                metric, text=label_text, anchor="w", font=AppStyle.get_footer_label_font(),
                text_color=AppStyle.COLOR_TEXT_MUTED
            ).pack(anchor="w")
            value_label = ctk.CTkLabel(
                metric, text=value_text, anchor="w", font=AppStyle.get_footer_value_font(),
                text_color=AppStyle.COLOR_TEXT_DARK
            )
            value_label.pack(anchor="w")
            self.breakdown_labels[key] = value_label

        services_frame = ctk.CTkFrame(breakdown_frame, fg_color="transparent")
        services_frame.pack(fill="x", padx=8, pady=(0, 2))
        self.service_labels = {}
        for key, label_text in (
            ("ciecie", "Cięcie"),
            ("opuszczenie", "Zaniżenie"),
            ("polerowanie", "Polerowanie"),
        ):
            label = ctk.CTkLabel(
                services_frame, text=f"{label_text}: 0.00 zł", anchor="w",
                font=AppStyle.get_footer_service_font(), text_color=AppStyle.COLOR_TEXT_MUTED
            )
            label.pack(side="left", padx=(0, 10))
            self.service_labels[key] = label

        total_frame = ctk.CTkFrame(right_container, fg_color="transparent")
        total_frame.pack(side="left", padx=(0, 15), fill="y")

        bottom_row = ctk.CTkFrame(total_frame, fg_color="transparent")
        bottom_row.pack(expand=True)

        # 1. Etykieta "RAZEM:"
        lbl_title = ctk.CTkLabel(
            bottom_row, text="RAZEM: ",
            font=AppStyle.get_summary_total_font(), text_color=AppStyle.COLOR_SUCCESS
        )
        lbl_title.pack(side="left")

        # 2. Kwota w tej samej linii
        self.lbl_total = ctk.CTkLabel(
            bottom_row, text="0.00 zł",
            font=AppStyle.get_summary_total_font(), text_color=AppStyle.COLOR_SUCCESS
        )
        self.lbl_total.pack(side="left")

        # Sekcja przycisków generowania w kolumnie (po prawej stronie kwoty)
        gen_buttons_frame = ctk.CTkFrame(right_container, fg_color="transparent")
        gen_buttons_frame.pack(side="right", fill="y")

        if self.on_export_pdf:
            btn_pdf = ctk.CTkButton(
                gen_buttons_frame, text="📄 Generuj PDF", width=130, height=45,
                font=AppStyle.get_bold_font(), fg_color=AppStyle.COLOR_SECONDARY,
                hover_color=AppStyle.COLOR_SECONDARY_HOVER, command=self.on_export_pdf
            )
            btn_pdf.pack(side="top", pady=(15, 3))

        if self.on_export_docx:
            btn_docx = ctk.CTkButton(
                gen_buttons_frame, text="📝 Generuj DOCX", width=130, height=45,
                font=AppStyle.get_bold_font(), fg_color=AppStyle.COLOR_SECONDARY,
                hover_color=AppStyle.COLOR_SECONDARY_HOVER, command=self.on_export_docx
            )
            btn_docx.pack(side="top")

    def update_total(self, total_val: float, breakdown=None):
        """Aktualizuje kwotę końcową i jej rozbicie na składniki."""
        self.lbl_total.configure(text=f"{total_val:.2f} zł")
        if breakdown is None:
            return
        self.breakdown_labels["qty"].configure(text=str(breakdown["qty"]))
        self.breakdown_labels["tool"].configure(text=f"{breakdown['tool']:.2f} zł")
        self.breakdown_labels["coat"].configure(text=f"{breakdown['coat']:.2f} zł")
        self.breakdown_labels["extra"].configure(text=f"{breakdown['extra']:.2f} zł")
        self.service_labels["ciecie"].configure(text=f"Cięcie: {breakdown['ciecie']:.2f} zł")
        self.service_labels["opuszczenie"].configure(text=f"Zaniżenie: {breakdown['opuszczenie']:.2f} zł")
        self.service_labels["polerowanie"].configure(text=f"Polerowanie: {breakdown['polerowanie']:.2f} zł")