"""Purchase section panel — displays purchase costs and loan details."""

import customtkinter as ctk
from views.widgets import (
    SectionFrame, MetricRow, SeparatorRow, COLORS, FONTS
)
from utils.formatting import format_currency, format_percent, format_years


class PurchasePanel(SectionFrame):
    """Displays Total Price, Closing Costs, Down Payment, Reserve,
    Rent Ready, Total Capital Required, and Loan details."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, title="PURCHASE & CAPITAL", **kwargs)

        # Purchase metrics
        self.total_price = MetricRow(
            self.content, "Total Price", large=True,
            value_color=COLORS["accent_cyan"]
        )
        self.total_price.pack(fill="x", pady=2)

        self.closing_costs = MetricRow(
            self.content, "Closing Costs", show_rate=True
        )
        self.closing_costs.pack(fill="x", pady=2)

        self.down_payment = MetricRow(
            self.content, "Down Payment", show_rate=True
        )
        self.down_payment.pack(fill="x", pady=2)

        self.reserve_account = MetricRow(
            self.content, "Reserve Account", show_rate=True
        )
        self.reserve_account.pack(fill="x", pady=2)

        self.rent_ready = MetricRow(self.content, "Cost to Rent Ready")
        self.rent_ready.pack(fill="x", pady=2)

        SeparatorRow(self.content).pack(fill="x")

        self.total_capital = MetricRow(
            self.content, "Total Capital Required", large=True,
            value_color=COLORS["accent_orange"]
        )
        self.total_capital.pack(fill="x", pady=2)

        SeparatorRow(self.content).pack(fill="x")

        # Loan details
        self.loan_term = MetricRow(self.content, "Loan Term")
        self.loan_term.pack(fill="x", pady=2)

        self.interest_rate = MetricRow(self.content, "Interest Rate")
        self.interest_rate.pack(fill="x", pady=2)

        self.total_leverage = MetricRow(
            self.content, "Total Leverage",
            value_color=COLORS["text_primary"]
        )
        self.total_leverage.pack(fill="x", pady=2)

    def update_from_model(self, model):
        """Refresh all displayed values from the property model."""
        inp = model.inputs

        self.total_price.set_value(format_currency(model.total_price))
        self.closing_costs.set_value(format_currency(model.closing_costs))
        self.closing_costs.set_rate(format_percent(inp.closing_cost_rate, 0))
        self.down_payment.set_value(format_currency(model.down_payment))
        self.down_payment.set_rate(format_percent(inp.down_payment_rate, 0))
        self.reserve_account.set_value(format_currency(model.reserve_account))
        self.reserve_account.set_rate(f"{inp.reserve_months} mo")
        self.rent_ready.set_value(format_currency(inp.cost_to_rent_ready))
        self.total_capital.set_value(
            format_currency(model.total_capital_required)
        )

        self.loan_term.set_value(format_years(inp.loan_term))
        self.interest_rate.set_value(format_percent(inp.interest_rate, 1))
        self.total_leverage.set_value(format_currency(model.total_leverage))
