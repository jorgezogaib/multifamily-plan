"""Returns panel — displays key financial performance metrics."""

import customtkinter as ctk
from views.widgets import (
    SectionFrame, MetricRow, SeparatorRow, COLORS
)
from utils.formatting import format_currency, format_percent, format_ratio


class ReturnsPanel(SectionFrame):
    """Displays NOI, Debt Service, Cashflow, and key ratios."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, title="RETURNS", **kwargs)

        self.noi = MetricRow(
            self.content, "Net Operating Income", large=True,
            value_color=COLORS["accent_teal"]
        )
        self.noi.pack(fill="x", pady=2)

        self.debt_service = MetricRow(
            self.content, "Debt Service",
            value_color=COLORS["negative"]
        )
        self.debt_service.pack(fill="x", pady=2)

        SeparatorRow(self.content).pack(fill="x")

        self.annual_cashflow = MetricRow(
            self.content, "Annual Cashflow", large=True,
            value_color=COLORS["positive"]
        )
        self.annual_cashflow.pack(fill="x", pady=2)

        self.monthly_cashflow = MetricRow(
            self.content, "Monthly Cashflow",
            value_color=COLORS["positive"]
        )
        self.monthly_cashflow.pack(fill="x", pady=2)

        SeparatorRow(self.content).pack(fill="x")

        # Ratios
        self.cashflow_margin = MetricRow(
            self.content, "Cashflow Margin",
            value_color=COLORS["accent_orange"]
        )
        self.cashflow_margin.pack(fill="x", pady=2)

        self.cash_on_cash = MetricRow(
            self.content, "Cash on Cash", large=True,
            value_color=COLORS["accent_orange"]
        )
        self.cash_on_cash.pack(fill="x", pady=2)

        self.cap_rate = MetricRow(
            self.content, "Cap Rate",
            value_color=COLORS["accent_orange"]
        )
        self.cap_rate.pack(fill="x", pady=2)

        self.dscr = MetricRow(
            self.content, "DSCR",
            value_color=COLORS["accent_orange"]
        )
        self.dscr.pack(fill="x", pady=2)

    def update_from_model(self, model):
        self.noi.set_value(format_currency(model.noi))

        self.debt_service.set_value(format_currency(model.debt_service))

        # Cashflow — color based on positive/negative
        cf_color = COLORS["positive"] if model.annual_cashflow >= 0 else COLORS["negative"]
        self.annual_cashflow.set_value(
            format_currency(model.annual_cashflow), color=cf_color
        )
        self.monthly_cashflow.set_value(
            format_currency(model.monthly_cashflow, show_decimals=True),
            color=cf_color,
        )

        # Ratios
        self.cashflow_margin.set_value(
            format_percent(model.cashflow_margin, 2)
        )

        # Cash on Cash — highlight color based on threshold
        coc = model.cash_on_cash
        if coc >= 0.10:
            coc_color = COLORS["positive"]
        elif coc >= 0.06:
            coc_color = COLORS["accent_orange"]
        else:
            coc_color = COLORS["negative"]
        self.cash_on_cash.set_value(
            format_percent(model.cash_on_cash, 2), color=coc_color
        )

        self.cap_rate.set_value(format_percent(model.cap_rate, 2))

        # DSCR — color based on threshold
        dscr_val = model.dscr
        if dscr_val >= 1.25:
            dscr_color = COLORS["positive"]
        elif dscr_val >= 1.0:
            dscr_color = COLORS["warning"]
        else:
            dscr_color = COLORS["negative"]
        self.dscr.set_value(format_ratio(model.dscr), color=dscr_color)
