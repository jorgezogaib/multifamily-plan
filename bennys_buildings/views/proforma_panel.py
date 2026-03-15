"""Pro Forma panel — professional financial statement layout.

Consolidates all output panels into a single scrollable view formatted
like a standard real estate investment proforma / operating statement.

Uses a 2-column layout with auto-scaling fonts that maximize readability
based on available screen space.
"""

import customtkinter as ctk
from views.widgets import COLORS, FONTS
from utils.formatting import format_currency, format_percent, format_ratio


class ProFormaPanel(ctk.CTkScrollableFrame):
    """Scrollable pro forma financial statement with auto-scaling fonts."""

    # Known content height at base font sizes (scale 1.0).
    # Computed from the layout: right column has ~25 rows of varying height
    # totaling ~650px, plus title ~30px, padding/margins ~20px.
    _BASE_CONTENT_H = 700

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
        self._font_reg: list[tuple] = []  # (widget, family, base_size, bold)
        self._current_scale = 1.0
        self._scale_pending = False

        self._build_layout()
        # Bind to the canvas viewport — self is the inner content frame
        self._parent_canvas.bind("<Configure>", self._schedule_rescale)

    # ── Auto-scaling engine ──

    def _rf(self, w, family, size, bold=False):
        """Register a widget for font scaling."""
        self._font_reg.append((w, family, size, bold))

    def _schedule_rescale(self, event=None):
        if not self._scale_pending:
            self._scale_pending = True
            self.after(150, self._auto_scale)

    def _auto_scale(self):
        self._scale_pending = False
        h = self._parent_canvas.winfo_height()
        if h <= 100:
            return

        raw = h / self._BASE_CONTENT_H
        scale = max(0.75, min(1.5, raw))

        if abs(scale - self._current_scale) >= 0.02:
            self._current_scale = scale
            self._apply_scale(scale)

        self._toggle_scrollbar(raw >= 0.95)

    def _apply_scale(self, s):
        for w, fam, base, bold in self._font_reg:
            sz = max(9, round(base * s))
            f = (fam, sz, "bold") if bold else (fam, sz)
            try:
                w.configure(font=f)
            except Exception:
                pass

    def _toggle_scrollbar(self, hide):
        try:
            if hide:
                self._scrollbar.grid_remove()
            else:
                self._scrollbar.grid(row=1, column=1, sticky="ns")
        except Exception:
            pass

    # ── Build layout ──

    def _build_layout(self):
        """Build the entire pro forma statement layout."""
        self._add_title("INVESTMENT PRO FORMA")

        # 2-column container
        cols = ctk.CTkFrame(self, fg_color="transparent")
        cols.pack(fill="both", expand=True)
        cols.columnconfigure(0, weight=1)
        cols.columnconfigure(1, weight=1)
        cols.rowconfigure(0, weight=1)

        L = ctk.CTkFrame(cols, fg_color="transparent")
        L.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        R = ctk.CTkFrame(cols, fg_color="transparent")
        R.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        # ── Left: Deal Structure + Cash Flow ──

        self._add_section_header("INVESTMENT SUMMARY", L)
        self._add_line("total_price", "Acquisition Price", L)
        self._add_detail("price_detail", "", L)
        self._add_line("property_info", "Property", L)
        self._add_line("location", "Location", L)

        self._add_section_header("CAPITAL REQUIREMENTS", L)
        self._add_line("down_payment", "Down Payment", L)
        self._add_line("closing_costs", "Closing Costs", L)
        self._add_line("reserve_account", "Reserve Account", L)
        self._add_line("rent_ready", "Cost to Rent Ready", L)
        self._add_single_separator(L)
        self._add_total_line("total_capital", "Total Capital Required", L)

        self._add_section_header("FINANCING", L)
        self._add_line("loan_amount", "Loan Amount", L)
        self._add_line("loan_terms", "Term / Rate", L)
        self._add_line("debt_service", "Annual Debt Service", L)
        self._add_detail("monthly_ds", "", L)

        self._add_section_header("CASH FLOW ANALYSIS", L)
        self._add_line("cf_noi", "Net Operating Income", L)
        self._add_line("cf_ds", "Less: Debt Service", L)
        self._add_single_separator(L)
        self._add_total_line("annual_cf", "Annual Cash Flow", L)
        self._add_line("monthly_cf", "Monthly Cash Flow", L)

        # ── Right: Operating Statement + Metrics ──

        self._add_section_header("OPERATING STATEMENT", R)
        self._add_subsection("Revenue", R)
        self._add_line("pgr", "Potential Gross Rent", R)
        self._add_line("vacancy", "Less: Vacancy", R)
        self._add_line("ltl", "Less: Loss to Lease", R)
        self._add_single_separator(R)
        self._add_subtotal_line("egr", "Effective Gross Revenue", R)
        self._add_spacer(R)

        self._add_subsection("Operating Expenses", R)
        self._add_line("maintenance", "Maintenance", R)
        self._add_line("management", "Management", R)
        self._add_line("improvements", "Annual Improvements", R)
        self._add_line("utility_allowance", "Utility Allowance", R)
        self._add_line("insurance", "Insurance", R)
        self._add_line("taxes", "Property Tax", R)
        self._add_single_separator(R)
        self._add_subtotal_line("total_expenses", "Total Expenses", R)
        self._add_detail("expense_ratio", "", R)
        self._add_spacer(R)

        self._add_double_separator(R)
        self._add_total_line("noi", "NET OPERATING INCOME", R)

        self._add_section_header("INVESTMENT METRICS", R)
        self._add_metric_line("cap_rate", "Cap Rate", R)
        self._add_metric_line("coc", "Cash on Cash Return", R)
        self._add_metric_line("dscr", "DSCR", R)
        self._add_metric_line("cf_margin", "Cash Flow Margin", R)
        self._add_metric_line("grm", "Gross Rent Multiplier", R)
        self._add_metric_line("breakeven_occ", "Break-even Occupancy", R)
        self._add_metric_line("price_per_br", "Price / Bedroom", R)

    # ── Layout helpers — rows auto-size from content ──

    def _add_title(self, text: str):
        lbl = ctk.CTkLabel(
            self, text=text,
            font=("Segoe UI", 17, "bold"),
            text_color=COLORS["accent_cyan"],
            anchor="center",
        )
        lbl.pack(fill="x", pady=(6, 2))
        self._rf(lbl, "Segoe UI", 17, bold=True)
        sep = ctk.CTkFrame(self, height=2, fg_color=COLORS["accent_cyan"])
        sep.pack(fill="x", padx=12, pady=(0, 6))

    def _add_section_header(self, text: str, parent=None):
        p = parent if parent is not None else self
        lbl = ctk.CTkLabel(
            p, text=text,
            font=("Segoe UI", 13, "bold"),
            text_color=COLORS["header"],
            anchor="w",
        )
        lbl.pack(fill="x", padx=12, pady=(10, 0))
        self._rf(lbl, "Segoe UI", 13, bold=True)
        sep = ctk.CTkFrame(p, height=1, fg_color=COLORS["header"])
        sep.pack(fill="x", padx=12, pady=(2, 4))

    def _add_subsection(self, text: str, parent=None):
        p = parent if parent is not None else self
        lbl = ctk.CTkLabel(
            p, text=text,
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS["text_muted"],
            anchor="w",
        )
        lbl.pack(fill="x", padx=18, pady=(4, 2))
        self._rf(lbl, "Segoe UI", 12, bold=True)

    def _add_line(self, key: str, label: str, parent=None):
        p = parent if parent is not None else self
        row = ctk.CTkFrame(p, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=1)

        lbl = ctk.CTkLabel(
            row, text=label, font=("Segoe UI", 13),
            text_color=COLORS["text_secondary"], anchor="w",
        )
        lbl.pack(side="left", fill="x", expand=True)
        self._rf(lbl, "Segoe UI", 13)

        rate_lbl = ctk.CTkLabel(
            row, text="", font=("Segoe UI", 10),
            text_color=COLORS["text_muted"], anchor="e",
        )
        rate_lbl.pack(side="right", padx=(6, 0))
        self._rf(rate_lbl, "Segoe UI", 10)
        self._rows[f"{key}_rate"] = rate_lbl

        val_lbl = ctk.CTkLabel(
            row, text="$0", font=("Segoe UI Semibold", 13),
            text_color=COLORS["text_primary"], anchor="e",
        )
        val_lbl.pack(side="right", padx=(6, 0))
        self._rf(val_lbl, "Segoe UI Semibold", 13)
        self._rows[key] = val_lbl

    def _add_detail(self, key: str, text: str, parent=None):
        p = parent if parent is not None else self
        lbl = ctk.CTkLabel(
            p, text=text, font=("Segoe UI", 10),
            text_color=COLORS["text_muted"], anchor="e",
        )
        lbl.pack(fill="x", padx=18, pady=(0, 1))
        self._rf(lbl, "Segoe UI", 10)
        self._rows[key] = lbl

    def _add_subtotal_line(self, key: str, label: str, parent=None):
        p = parent if parent is not None else self
        row = ctk.CTkFrame(p, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=2)

        lbl = ctk.CTkLabel(
            row, text=label, font=("Segoe UI", 13, "bold"),
            text_color=COLORS["text_primary"], anchor="w",
        )
        lbl.pack(side="left", fill="x", expand=True)
        self._rf(lbl, "Segoe UI", 13, bold=True)

        val_lbl = ctk.CTkLabel(
            row, text="$0", font=("Segoe UI Semibold", 14),
            text_color=COLORS["accent_teal"], anchor="e",
        )
        val_lbl.pack(side="right", padx=(6, 0))
        self._rf(val_lbl, "Segoe UI Semibold", 14)
        self._rows[key] = val_lbl

    def _add_total_line(self, key: str, label: str, parent=None):
        p = parent if parent is not None else self
        row = ctk.CTkFrame(p, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=2)

        lbl = ctk.CTkLabel(
            row, text=label, font=("Segoe UI", 14, "bold"),
            text_color=COLORS["text_primary"], anchor="w",
        )
        lbl.pack(side="left", fill="x", expand=True)
        self._rf(lbl, "Segoe UI", 14, bold=True)

        val_lbl = ctk.CTkLabel(
            row, text="$0", font=("Segoe UI Semibold", 15),
            text_color=COLORS["accent_orange"], anchor="e",
        )
        val_lbl.pack(side="right", padx=(6, 0))
        self._rf(val_lbl, "Segoe UI Semibold", 15)
        self._rows[key] = val_lbl

    def _add_metric_line(self, key: str, label: str, parent=None):
        p = parent if parent is not None else self
        row = ctk.CTkFrame(p, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=1)

        lbl = ctk.CTkLabel(
            row, text=label, font=("Segoe UI", 13),
            text_color=COLORS["text_secondary"], anchor="w",
        )
        lbl.pack(side="left", fill="x", expand=True)
        self._rf(lbl, "Segoe UI", 13)

        val_lbl = ctk.CTkLabel(
            row, text="0.00%", font=("Segoe UI Semibold", 15),
            text_color=COLORS["accent_orange"], anchor="e",
        )
        val_lbl.pack(side="right", padx=(6, 0))
        self._rf(val_lbl, "Segoe UI Semibold", 15)
        self._rows[key] = val_lbl

    def _add_single_separator(self, parent=None):
        p = parent if parent is not None else self
        sep = ctk.CTkFrame(p, height=1, fg_color=COLORS["separator"])
        sep.pack(fill="x", padx=18, pady=3)

    def _add_double_separator(self, parent=None):
        p = parent if parent is not None else self
        ctk.CTkFrame(p, height=1, fg_color=COLORS["separator"]).pack(
            fill="x", padx=18, pady=(3, 1))
        ctk.CTkFrame(p, height=1, fg_color=COLORS["separator"]).pack(
            fill="x", padx=18, pady=(0, 3))

    def _add_spacer(self, parent=None):
        p = parent if parent is not None else self
        ctk.CTkFrame(p, fg_color="transparent", height=6).pack(fill="x")

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
        self._set("location", location or "\u2014", COLORS["text_primary"])
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
        noi_color = (COLORS["positive"] if model.noi >= 0
                     else COLORS["negative"])
        self._set("noi", format_currency(model.noi), noi_color)

        # ── Investment Metrics ──

        cap = model.cap_rate
        if cap >= 0.07:
            cap_color = COLORS["positive"]
        elif cap >= 0.05:
            cap_color = COLORS["accent_orange"]
        else:
            cap_color = COLORS["negative"]
        self._set("cap_rate", format_percent(cap, 2), cap_color)

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

        cfm = model.cashflow_margin
        if cfm >= 0.20:
            cfm_color = COLORS["positive"]
        elif cfm >= 0.10:
            cfm_color = COLORS["accent_orange"]
        else:
            cfm_color = COLORS["negative"]
        self._set("cf_margin", format_percent(cfm, 2), cfm_color)

        grm = model.grm
        if grm <= 0:
            grm_color = COLORS["text_muted"]
        elif grm < 8:
            grm_color = COLORS["positive"]
        elif grm <= 12:
            grm_color = COLORS["accent_orange"]
        else:
            grm_color = COLORS["negative"]
        self._set("grm", f"{format_ratio(grm)}x", grm_color)

        beo = model.breakeven_occupancy
        if beo <= 0:
            beo_color = COLORS["text_muted"]
        elif beo < 0.75:
            beo_color = COLORS["positive"]
        elif beo <= 0.85:
            beo_color = COLORS["accent_orange"]
        else:
            beo_color = COLORS["negative"]
        self._set("breakeven_occ", format_percent(beo, 1), beo_color)

        self._set("price_per_br",
                  format_currency(model.price_per_bedroom),
                  COLORS["accent_orange"])
