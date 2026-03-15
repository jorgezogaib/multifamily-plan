"""Pro Forma panel — professional financial statement layout.

Consolidates all output panels (Purchase, Income, Expenses, Returns)
into a single scrollable view formatted like a standard real estate
investment proforma / operating statement.
"""

import customtkinter as ctk
from views.widgets import COLORS, FONTS
from utils.formatting import format_currency, format_percent, format_ratio


class ProFormaPanel(ctk.CTkScrollableFrame):
    """Scrollable pro forma financial statement."""

    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent_teal"],
            **kwargs,
        )

        self._rows: dict[str, ctk.CTkLabel] = {}
        self._build_layout()

    def _build_layout(self):
        """Build the entire pro forma statement layout."""
        # Title
        self._add_title("INVESTMENT PRO FORMA")

        # ── Investment Summary ──
        self._add_section_header("INVESTMENT SUMMARY")
        self._add_line("total_price", "Acquisition Price")
        self._add_detail("price_detail", "")
        self._add_line("property_info", "Property")
        self._add_line("location", "Location")

        # ── Capital Requirements ──
        self._add_section_header("CAPITAL REQUIREMENTS")
        self._add_line("down_payment", "Down Payment")
        self._add_line("closing_costs", "Closing Costs")
        self._add_line("reserve_account", "Reserve Account")
        self._add_line("rent_ready", "Cost to Rent Ready")
        self._add_single_separator()
        self._add_total_line("total_capital", "Total Capital Required")

        # ── Financing ──
        self._add_section_header("FINANCING")
        self._add_line("loan_amount", "Loan Amount")
        self._add_line("loan_terms", "Term / Rate")
        self._add_line("debt_service", "Annual Debt Service")
        self._add_detail("monthly_ds", "")

        # ── Operating Statement ──
        self._add_section_header("OPERATING STATEMENT")

        # Revenue
        self._add_subsection("Revenue")
        self._add_line("pgr", "Potential Gross Rent")
        self._add_line("vacancy", "Less: Vacancy")
        self._add_line("ltl", "Less: Loss to Lease")
        self._add_single_separator()
        self._add_subtotal_line("egr", "Effective Gross Revenue")

        self._add_spacer()

        # Expenses
        self._add_subsection("Operating Expenses")
        self._add_line("maintenance", "Maintenance")
        self._add_line("management", "Management")
        self._add_line("improvements", "Annual Improvements")
        self._add_line("utility_allowance", "Utility Allowance")
        self._add_line("insurance", "Insurance")
        self._add_line("taxes", "Property Tax")
        self._add_single_separator()
        self._add_subtotal_line("total_expenses", "Total Operating Expenses")
        self._add_detail("expense_ratio", "")

        self._add_spacer()

        # NOI
        self._add_double_separator()
        self._add_total_line("noi", "NET OPERATING INCOME")

        # ── Cash Flow ──
        self._add_section_header("CASH FLOW ANALYSIS")
        self._add_line("cf_noi", "Net Operating Income")
        self._add_line("cf_ds", "Less: Debt Service")
        self._add_single_separator()
        self._add_total_line("annual_cf", "Annual Cash Flow")
        self._add_line("monthly_cf", "Monthly Cash Flow")

        # ── Investment Metrics ──
        self._add_section_header("INVESTMENT METRICS")
        self._add_metric_line("cap_rate", "Cap Rate")
        self._add_metric_line("coc", "Cash on Cash Return")
        self._add_metric_line("dscr", "DSCR")
        self._add_metric_line("cf_margin", "Cash Flow Margin")

        # Bottom padding
        self._add_spacer()

    # ── Layout helper methods ──

    def _add_title(self, text: str):
        lbl = ctk.CTkLabel(
            self, text=text,
            font=FONTS["title"],
            text_color=COLORS["accent_cyan"],
            anchor="center",
        )
        lbl.pack(fill="x", pady=(8, 4))
        sep = ctk.CTkFrame(self, height=2, fg_color=COLORS["accent_cyan"])
        sep.pack(fill="x", padx=16, pady=(0, 8))

    def _add_section_header(self, text: str):
        frame = ctk.CTkFrame(self, fg_color="transparent", height=30)
        frame.pack(fill="x", padx=16, pady=(12, 2))
        frame.pack_propagate(False)
        lbl = ctk.CTkLabel(
            frame, text=text,
            font=FONTS["subheader"],
            text_color=COLORS["header"],
            anchor="w",
        )
        lbl.pack(side="left", fill="x", expand=True)
        sep = ctk.CTkFrame(self, height=1, fg_color=COLORS["header"])
        sep.pack(fill="x", padx=16, pady=(0, 4))

    def _add_subsection(self, text: str):
        lbl = ctk.CTkLabel(
            self, text=text,
            font=("Segoe UI", 11, "bold"),
            text_color=COLORS["text_muted"],
            anchor="w",
        )
        lbl.pack(fill="x", padx=24, pady=(4, 2))

    def _add_line(self, key: str, label: str):
        row = ctk.CTkFrame(self, fg_color="transparent", height=24)
        row.pack(fill="x", padx=24, pady=1)
        row.pack_propagate(False)

        lbl = ctk.CTkLabel(
            row, text=label,
            font=FONTS["label"],
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        lbl.pack(side="left", fill="x", expand=True)

        rate_lbl = ctk.CTkLabel(
            row, text="",
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
            anchor="e",
            width=60,
        )
        rate_lbl.pack(side="right", padx=(4, 0))
        self._rows[f"{key}_rate"] = rate_lbl

        val_lbl = ctk.CTkLabel(
            row, text="$0",
            font=("Segoe UI Semibold", 12),
            text_color=COLORS["text_primary"],
            anchor="e",
            width=110,
        )
        val_lbl.pack(side="right")
        self._rows[key] = val_lbl

    def _add_detail(self, key: str, text: str):
        """A small detail/note line below a main line."""
        lbl = ctk.CTkLabel(
            self, text=text,
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
            anchor="e",
        )
        lbl.pack(fill="x", padx=24, pady=(0, 2))
        self._rows[key] = lbl

    def _add_subtotal_line(self, key: str, label: str):
        row = ctk.CTkFrame(self, fg_color="transparent", height=26)
        row.pack(fill="x", padx=24, pady=1)
        row.pack_propagate(False)

        lbl = ctk.CTkLabel(
            row, text=label,
            font=FONTS["subheader"],
            text_color=COLORS["text_primary"],
            anchor="w",
        )
        lbl.pack(side="left", fill="x", expand=True)

        val_lbl = ctk.CTkLabel(
            row, text="$0",
            font=("Segoe UI Semibold", 13),
            text_color=COLORS["accent_teal"],
            anchor="e",
            width=110,
        )
        val_lbl.pack(side="right")
        self._rows[key] = val_lbl

    def _add_total_line(self, key: str, label: str):
        row = ctk.CTkFrame(self, fg_color="transparent", height=30)
        row.pack(fill="x", padx=20, pady=2)
        row.pack_propagate(False)

        lbl = ctk.CTkLabel(
            row, text=label,
            font=FONTS["header"],
            text_color=COLORS["text_primary"],
            anchor="w",
        )
        lbl.pack(side="left", fill="x", expand=True)

        val_lbl = ctk.CTkLabel(
            row, text="$0",
            font=FONTS["value_large"],
            text_color=COLORS["accent_orange"],
            anchor="e",
            width=120,
        )
        val_lbl.pack(side="right")
        self._rows[key] = val_lbl

    def _add_metric_line(self, key: str, label: str):
        row = ctk.CTkFrame(self, fg_color="transparent", height=28)
        row.pack(fill="x", padx=24, pady=2)
        row.pack_propagate(False)

        lbl = ctk.CTkLabel(
            row, text=label,
            font=FONTS["label"],
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        lbl.pack(side="left", fill="x", expand=True)

        val_lbl = ctk.CTkLabel(
            row, text="0.00%",
            font=FONTS["value_large"],
            text_color=COLORS["accent_orange"],
            anchor="e",
            width=120,
        )
        val_lbl.pack(side="right")
        self._rows[key] = val_lbl

    def _add_single_separator(self):
        sep = ctk.CTkFrame(self, height=1, fg_color=COLORS["separator"])
        sep.pack(fill="x", padx=24, pady=3)

    def _add_double_separator(self):
        sep1 = ctk.CTkFrame(self, height=1, fg_color=COLORS["separator"])
        sep1.pack(fill="x", padx=24, pady=(3, 2))
        sep2 = ctk.CTkFrame(self, height=1, fg_color=COLORS["separator"])
        sep2.pack(fill="x", padx=24, pady=(0, 3))

    def _add_spacer(self):
        spacer = ctk.CTkFrame(self, fg_color="transparent", height=8)
        spacer.pack(fill="x")

    # ── Value setters ──

    def _set(self, key: str, text: str, color: str = None):
        if key in self._rows:
            self._rows[key].configure(text=text)
            if color:
                self._rows[key].configure(text_color=color)

    def _set_rate(self, key: str, text: str):
        rate_key = f"{key}_rate"
        if rate_key in self._rows:
            self._rows[rate_key].configure(text=text)

    def update_from_model(self, model):
        """Refresh the entire pro forma from the model."""
        inp = model.inputs

        # ── Investment Summary ──
        self._set("total_price", format_currency(model.total_price),
                  COLORS["accent_cyan"])
        self._set_rate("total_price", "")

        units = inp.num_units
        ppu = model.total_price / units if units else 0
        self._set("price_detail",
                  f"{units} units @ {format_currency(ppu)}/unit")

        self._set("property_info", inp.property_type,
                  COLORS["text_primary"])
        self._set_rate("property_info", inp.num_bedrooms)

        location = ""
        if inp.county:
            location = inp.county
        if inp.state:
            location = f"{location}, {inp.state}" if location else inp.state
        self._set("location", location or "—", COLORS["text_primary"])
        self._set_rate("location", "")

        # ── Capital Requirements ──
        self._set("down_payment", format_currency(model.down_payment))
        self._set_rate("down_payment", format_percent(inp.down_payment_rate, 0))

        self._set("closing_costs", format_currency(model.closing_costs))
        self._set_rate("closing_costs", format_percent(inp.closing_cost_rate, 0))

        self._set("reserve_account", format_currency(model.reserve_account))
        self._set_rate("reserve_account", f"{inp.reserve_months} mo")

        self._set("rent_ready", format_currency(inp.cost_to_rent_ready))
        self._set_rate("rent_ready", "")

        self._set("total_capital",
                  format_currency(model.total_capital_required),
                  COLORS["accent_orange"])

        # ── Financing ──
        self._set("loan_amount", format_currency(model.total_leverage),
                  COLORS["text_primary"])
        self._set_rate("loan_amount", "")

        self._set("loan_terms",
                  f"{inp.loan_term} yr @ {format_percent(inp.interest_rate, 1)}",
                  COLORS["text_primary"])
        self._set_rate("loan_terms", "")

        self._set("debt_service", format_currency(model.debt_service),
                  COLORS["negative"])
        self._set_rate("debt_service", "")

        monthly_ds = model.debt_service / 12 if model.debt_service else 0
        self._set("monthly_ds",
                  f"{format_currency(monthly_ds, show_decimals=True)}/mo")

        # ── Operating Statement — Revenue ──
        self._set("pgr", format_currency(model.potential_gross_rent),
                  COLORS["accent_cyan"])
        self._set_rate("pgr", "")

        self._set("vacancy", format_currency(model.vacancy),
                  COLORS["negative"])
        self._set_rate("vacancy", format_percent(inp.vacancy_rate, 0))

        self._set("ltl", format_currency(model.loss_to_lease),
                  COLORS["negative"])
        self._set_rate("ltl", format_percent(inp.loss_to_lease_rate, 0))

        self._set("egr", format_currency(model.effective_gross_rent),
                  COLORS["accent_teal"])

        # ── Operating Statement — Expenses ──
        self._set("maintenance", format_currency(model.maintenance),
                  COLORS["negative"])
        self._set_rate("maintenance", format_percent(inp.maintenance_rate, 0))

        self._set("management", format_currency(model.management),
                  COLORS["negative"])
        self._set_rate("management", format_percent(inp.management_rate, 0))

        self._set("improvements",
                  format_currency(model.annual_improvements),
                  COLORS["negative"])
        self._set_rate("improvements",
                       format_percent(inp.annual_improvements_rate, 0))

        self._set("utility_allowance",
                  format_currency(model.utility_allowance_yearly),
                  COLORS["negative"])
        self._set_rate("utility_allowance", "")

        self._set("insurance", format_currency(model.insurance),
                  COLORS["negative"])
        self._set_rate("insurance", format_percent(inp.insurance_rate, 1))

        self._set("taxes", format_currency(model.taxes),
                  COLORS["negative"])
        self._set_rate("taxes", format_percent(inp.tax_rate, 1))

        self._set("total_expenses",
                  format_currency(model.total_expenses),
                  COLORS["negative"])

        self._set("expense_ratio",
                  f"Expense Ratio: {format_percent(model.expense_ratio, 1)}")

        # ── NOI ──
        self._set("noi", format_currency(model.noi), COLORS["accent_teal"])

        # ── Cash Flow ──
        self._set("cf_noi", format_currency(model.noi),
                  COLORS["accent_teal"])
        self._set_rate("cf_noi", "")

        self._set("cf_ds", format_currency(model.debt_service),
                  COLORS["negative"])
        self._set_rate("cf_ds", "")

        cf_color = (COLORS["positive"] if model.annual_cashflow >= 0
                    else COLORS["negative"])
        self._set("annual_cf",
                  format_currency(model.annual_cashflow), cf_color)

        self._set("monthly_cf",
                  format_currency(model.monthly_cashflow, show_decimals=True),
                  cf_color)
        self._set_rate("monthly_cf", "")

        # ── Investment Metrics ──
        self._set("cap_rate", format_percent(model.cap_rate, 2))

        coc = model.cash_on_cash
        if coc >= 0.10:
            coc_color = COLORS["positive"]
        elif coc >= 0.06:
            coc_color = COLORS["accent_orange"]
        else:
            coc_color = COLORS["negative"]
        self._set("coc", format_percent(coc, 2), coc_color)

        dscr = model.dscr
        if dscr >= 1.25:
            dscr_color = COLORS["positive"]
        elif dscr >= 1.0:
            dscr_color = COLORS["warning"]
        else:
            dscr_color = COLORS["negative"]
        self._set("dscr", f"{format_ratio(dscr)}x", dscr_color)

        self._set("cf_margin", format_percent(model.cashflow_margin, 2))
