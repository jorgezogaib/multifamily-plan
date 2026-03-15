"""Main dashboard view — assembles all panels into the 3-column layout."""

import customtkinter as ctk

from views.widgets import COLORS, FONTS
from views.input_panel import InputPanel
from views.purchase_panel import PurchasePanel
from views.income_expense_panel import IncomePanel, ExpensePanel
from views.returns_panel import ReturnsPanel
from views.utility_detail_panel import UtilityDetailPanel


class Dashboard(ctk.CTkFrame):
    """The main dashboard frame containing all panels.

    Layout:
        Left column: Purchase + Income + Utility Detail
        Middle column: Returns + Expenses
        Right column: Input Panel (scrollable)
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_dark"], **kwargs)

        # Configure 3-column grid
        self.columnconfigure(0, weight=3, minsize=320)  # Left
        self.columnconfigure(1, weight=3, minsize=320)  # Middle
        self.columnconfigure(2, weight=2, minsize=300)  # Right (input)
        self.rowconfigure(0, weight=1)

        # ── Left Column ───────────────────────────────────────────
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(12, 6), pady=12)

        self.purchase_panel = PurchasePanel(left_frame)
        self.purchase_panel.pack(fill="x", pady=(0, 8))

        self.income_panel = IncomePanel(left_frame)
        self.income_panel.pack(fill="x", pady=(0, 8))

        self.utility_panel = UtilityDetailPanel(left_frame)
        # Hidden by default — shown when Use UA? = Yes
        # (pack is called by show_utility_panel)

        # ── Middle Column ─────────────────────────────────────────
        mid_frame = ctk.CTkFrame(self, fg_color="transparent")
        mid_frame.grid(row=0, column=1, sticky="nsew", padx=6, pady=12)

        self.returns_panel = ReturnsPanel(mid_frame)
        self.returns_panel.pack(fill="x", pady=(0, 8))

        self.expense_panel = ExpensePanel(mid_frame)
        self.expense_panel.pack(fill="x")

        # ── Right Column (scrollable inputs) ──────────────────────
        self.input_panel = InputPanel(self, width=300)
        self.input_panel.grid(
            row=0, column=2, sticky="nsew", padx=(6, 12), pady=12
        )

    def show_utility_panel(self, show: bool):
        """Show or hide the Utility Breakdown panel."""
        if show:
            self.utility_panel.pack(fill="x")
        else:
            self.utility_panel.pack_forget()

    def refresh_from_model(self, model):
        """Update all display panels from the model."""
        self.purchase_panel.update_from_model(model)
        self.income_panel.update_from_model(model)
        self.expense_panel.update_from_model(model)
        self.returns_panel.update_from_model(model)
        self.utility_panel.update_from_model(model)
