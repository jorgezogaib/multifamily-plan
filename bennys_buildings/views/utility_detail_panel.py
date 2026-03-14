"""Utility detail panel — shows breakdown of utility allowance by service."""

import customtkinter as ctk
from views.widgets import (
    SectionFrame, MetricRow, SeparatorRow, COLORS, FONTS
)
from utils.formatting import format_currency


# Friendly display names for utility services
SERVICE_DISPLAY_NAMES = {
    "All Other Electric": "All Other Electric",
    "Cooking - Electric": "Cooking (Elec)",
    "Cooking - Natural Gas": "Cooking (Gas)",
    "Electric Air Conditioning": "Air Conditioning",
    "Fixed - Gas": "Fixed Gas",
    "Heating - Electric": "Heating (Elec)",
    "Heating - Heat Pump": "Heating (HP)",
    "Heating - Natural Gas": "Heating (Gas)",
    "Sewer": "Sewer",
    "Trash Collection": "Trash Collection",
    "Water": "Water",
    "Water Heating - Electric": "Water Heat (Elec)",
    "Water Heating - Natural Gas": "Water Heat (Gas)",
}


class UtilityDetailPanel(SectionFrame):
    """Shows per-service utility allowance breakdown.

    Only visible when Use Utility Allowance is "Yes".
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, title="UTILITY BREAKDOWN", **kwargs)

        self._rows: dict[str, MetricRow] = {}
        self._no_data_label: ctk.CTkLabel | None = None
        self._total_row: MetricRow | None = None

    def update_from_model(self, model):
        """Rebuild the utility detail display from model data."""
        # Clear existing rows
        for widget in self.content.winfo_children():
            widget.destroy()
        self._rows.clear()

        detail = model.utility_detail
        inp = model.inputs

        if inp.use_utility_allowance != "Yes":
            label = ctk.CTkLabel(
                self.content,
                text="Utility allowance disabled",
                font=FONTS["small"],
                text_color=COLORS["text_muted"],
            )
            label.pack(pady=8)
            return

        if not detail or detail.get("total", 0) == 0:
            if not model.has_utility_data():
                msg = f"No utility data for {inp.state}"
            else:
                msg = "No allowances for current selections"
            label = ctk.CTkLabel(
                self.content,
                text=msg,
                font=FONTS["small"],
                text_color=COLORS["text_muted"],
            )
            label.pack(pady=8)
            return

        # Show each non-zero service
        for service, amount in detail.items():
            if service == "total":
                continue
            if amount <= 0:
                continue

            display_name = SERVICE_DISPLAY_NAMES.get(service, service)
            row = MetricRow(
                self.content,
                display_name,
                value_color=COLORS["text_primary"],
            )
            row.set_value(f"${amount}")
            row.pack(fill="x", pady=1)
            self._rows[service] = row

        # Separator and total
        SeparatorRow(self.content).pack(fill="x")

        total = detail.get("total", 0)
        total_row = MetricRow(
            self.content, "Total / month", large=True,
            value_color=COLORS["accent_orange"],
        )
        total_row.set_value(f"${total}")
        total_row.pack(fill="x", pady=2)
