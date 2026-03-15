"""Main dashboard view — assembles panels into a 2-column layout.

Left: Pro Forma financial statement (scrollable)
Right: Input Panel (scrollable, condensed)
"""

import customtkinter as ctk

from views.widgets import COLORS, FONTS
from views.input_panel import InputPanel
from views.proforma_panel import ProFormaPanel


class Dashboard(ctk.CTkFrame):
    """The main dashboard frame containing all panels.

    Layout:
        Left column: Pro Forma financial statement (scrollable)
        Right column: Input Panel (scrollable, condensed)
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_dark"], **kwargs)

        # Configure 2-column grid
        self.columnconfigure(0, weight=5, minsize=560)  # Pro Forma (2 columns)
        self.columnconfigure(1, weight=2, minsize=280)  # Inputs (tabbed)
        self.rowconfigure(0, weight=1)

        # ── Left Column — Pro Forma ─────────────────────────────────
        self.proforma_panel = ProFormaPanel(self)
        self.proforma_panel.grid(
            row=0, column=0, sticky="nsew", padx=(12, 6), pady=12
        )

        # ── Right Column — Inputs ───────────────────────────────────
        self.input_panel = InputPanel(self, width=300)
        self.input_panel.grid(
            row=0, column=1, sticky="nsew", padx=(6, 12), pady=12
        )

    def show_utility_panel(self, show: bool):
        """No-op — utility data is inline in the pro forma."""
        pass

    def refresh_from_model(self, model):
        """Update the pro forma from the model."""
        self.proforma_panel.update_from_model(model)
