"""Income and Expense panels — displays revenue and cost breakdowns."""

import customtkinter as ctk
from views.widgets import (
    SectionFrame, MetricRow, SeparatorRow, COLORS
)
from utils.formatting import format_currency, format_percent


class IncomePanel(SectionFrame):
    """Displays Potential Gross Rent, Vacancy, Loss to Lease,
    and Effective Gross Rent."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, title="INCOME", **kwargs)

        self.gross_rent = MetricRow(
            self.content, "Pot. Gross Rent",
            value_color=COLORS["accent_cyan"]
        )
        self.gross_rent.pack(fill="x", pady=2)

        self.vacancy = MetricRow(
            self.content, "Vacancy", show_rate=True,
            value_color=COLORS["negative"]
        )
        self.vacancy.pack(fill="x", pady=2)

        self.loss_to_lease = MetricRow(
            self.content, "Loss to Lease", show_rate=True,
            value_color=COLORS["negative"]
        )
        self.loss_to_lease.pack(fill="x", pady=2)

        SeparatorRow(self.content).pack(fill="x")

        self.eff_gross_rent = MetricRow(
            self.content, "Eff. Gross Rent", large=True,
            value_color=COLORS["accent_teal"]
        )
        self.eff_gross_rent.pack(fill="x", pady=2)

    def update_from_model(self, model):
        inp = model.inputs
        self.gross_rent.set_value(format_currency(model.potential_gross_rent))
        self.vacancy.set_value(format_currency(model.vacancy))
        self.vacancy.set_rate(format_percent(inp.vacancy_rate, 0))
        self.loss_to_lease.set_value(format_currency(model.loss_to_lease))
        self.loss_to_lease.set_rate(format_percent(inp.loss_to_lease_rate, 0))
        self.eff_gross_rent.set_value(
            format_currency(model.effective_gross_rent)
        )


class ExpensePanel(SectionFrame):
    """Displays all expense line items and total."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, title="EXPENSES", **kwargs)

        self.maintenance = MetricRow(
            self.content, "Maintenance", show_rate=True,
            value_color=COLORS["negative"]
        )
        self.maintenance.pack(fill="x", pady=2)

        self.management = MetricRow(
            self.content, "Management", show_rate=True,
            value_color=COLORS["negative"]
        )
        self.management.pack(fill="x", pady=2)

        self.improvements = MetricRow(
            self.content, "Annual Improvements", show_rate=True,
            value_color=COLORS["negative"]
        )
        self.improvements.pack(fill="x", pady=2)

        self.utility = MetricRow(
            self.content, "Utility Allowance",
            value_color=COLORS["negative"]
        )
        self.utility.pack(fill="x", pady=2)

        self.insurance = MetricRow(
            self.content, "Insurance", show_rate=True,
            value_color=COLORS["negative"]
        )
        self.insurance.pack(fill="x", pady=2)

        self.taxes = MetricRow(
            self.content, "Taxes", show_rate=True,
            value_color=COLORS["negative"]
        )
        self.taxes.pack(fill="x", pady=2)

        SeparatorRow(self.content).pack(fill="x")

        self.total_expenses = MetricRow(
            self.content, "Total Expenses", large=True,
            value_color=COLORS["negative"]
        )
        self.total_expenses.pack(fill="x", pady=2)

        self.expense_ratio_row = MetricRow(
            self.content, "Expense Ratio",
            value_color=COLORS["text_muted"]
        )
        self.expense_ratio_row.pack(fill="x", pady=2)

    def update_from_model(self, model):
        inp = model.inputs
        self.maintenance.set_value(format_currency(model.maintenance))
        self.maintenance.set_rate(format_percent(inp.maintenance_rate, 0))
        self.management.set_value(format_currency(model.management))
        self.management.set_rate(format_percent(inp.management_rate, 0))
        self.improvements.set_value(format_currency(model.annual_improvements))
        self.improvements.set_rate(
            format_percent(inp.annual_improvements_rate, 0)
        )
        self.utility.set_value(
            format_currency(model.utility_allowance_yearly)
        )
        self.insurance.set_value(format_currency(model.insurance))
        self.insurance.set_rate(format_percent(inp.insurance_rate, 1))
        self.taxes.set_value(format_currency(model.taxes))
        self.taxes.set_rate(format_percent(inp.tax_rate, 1))
        self.total_expenses.set_value(format_currency(model.total_expenses))
        self.expense_ratio_row.set_value(
            format_percent(model.expense_ratio, 1)
        )
