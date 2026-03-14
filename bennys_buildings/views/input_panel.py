"""Input panel — all user inputs organized in logical groups.

This is the right column of the dashboard containing dropdowns for
property configuration, entry fields for financial parameters, and
the cascading State -> County behavior.
"""

import customtkinter as ctk
from typing import Optional, Callable

from views.widgets import (
    SectionFrame, InputField, DropdownField, DisplayField,
    SeparatorRow, COLORS, FONTS
)


class InputPanel(ctk.CTkScrollableFrame):
    """Scrollable panel containing all user input fields."""

    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent_teal"],
            **kwargs,
        )

        # ── Callbacks (set by controller) ──
        self.on_state_changed: Optional[Callable] = None
        self.on_county_changed: Optional[Callable] = None
        self.on_input_changed: Optional[Callable] = None
        self.on_zip_changed: Optional[Callable] = None

        self._build_property_section()
        self._build_rates_section()
        self._build_loan_section()
        self._build_rent_section()
        self._build_utility_section()

    def _trigger_input_change(self, *args):
        """Called when any input field changes."""
        if self.on_input_changed:
            self.on_input_changed()

    def _trigger_state_change(self, value):
        if self.on_state_changed:
            self.on_state_changed(value)

    def _trigger_county_change(self, value):
        if self.on_county_changed:
            self.on_county_changed(value)

    def _trigger_zip_change(self):
        if self.on_zip_changed:
            self.on_zip_changed()

    # ── Property Section ───────────────────────────────────────────
    def _build_property_section(self):
        section = SectionFrame(self, title="PROPERTY")
        section.pack(fill="x", pady=(0, 8))

        self.state_dd = DropdownField(
            section.content, "State", [],
            on_change=self._trigger_state_change,
        )
        self.state_dd.pack(fill="x", pady=3)

        self.county_dd = DropdownField(
            section.content, "County", [],
            on_change=self._trigger_county_change,
        )
        self.county_dd.pack(fill="x", pady=3)

        self.property_type_dd = DropdownField(
            section.content, "Type", [],
            on_change=lambda v: self._trigger_input_change(),
        )
        self.property_type_dd.pack(fill="x", pady=3)

        self.bedrooms_dd = DropdownField(
            section.content, "Bedrooms", [],
            on_change=lambda v: self._trigger_input_change(),
        )
        self.bedrooms_dd.pack(fill="x", pady=3)

        self.num_units = InputField(
            section.content, "# Units",
            placeholder="4",
            on_change=self._trigger_input_change,
        )
        self.num_units.pack(fill="x", pady=3)

        self.price_per_unit = InputField(
            section.content, "$ / Unit",
            placeholder="62,500",
            on_change=self._trigger_input_change,
        )
        self.price_per_unit.pack(fill="x", pady=3)

        self.manual_total = InputField(
            section.content, "Total $ (opt)",
            placeholder="Leave blank to calculate",
            on_change=self._trigger_input_change,
        )
        self.manual_total.pack(fill="x", pady=3)

        self.zip_code = InputField(
            section.content, "Zip Code",
            placeholder="70816",
            on_change=self._trigger_zip_change,
        )
        self.zip_code.pack(fill="x", pady=3)

    # ── Rates Section ──────────────────────────────────────────────
    def _build_rates_section(self):
        section = SectionFrame(self, title="RATES")
        section.pack(fill="x", pady=(0, 8))

        self.insurance_rate = InputField(
            section.content, "Insurance %",
            placeholder="1.5",
            on_change=self._trigger_input_change,
            suffix="%",
        )
        self.insurance_rate.pack(fill="x", pady=3)

        self.tax_rate = InputField(
            section.content, "Tax %",
            placeholder="1.0",
            on_change=self._trigger_input_change,
            suffix="%",
        )
        self.tax_rate.pack(fill="x", pady=3)

    # ── Loan Section ───────────────────────────────────────────────
    def _build_loan_section(self):
        section = SectionFrame(self, title="LOAN")
        section.pack(fill="x", pady=(0, 8))

        self.loan_term = InputField(
            section.content, "Term (yr)",
            placeholder="30",
            on_change=self._trigger_input_change,
        )
        self.loan_term.pack(fill="x", pady=3)

        self.interest_rate = InputField(
            section.content, "Rate %",
            placeholder="6.5",
            on_change=self._trigger_input_change,
            suffix="%",
        )
        self.interest_rate.pack(fill="x", pady=3)

        self.down_pct = InputField(
            section.content, "Down %",
            placeholder="25",
            on_change=self._trigger_input_change,
            suffix="%",
        )
        self.down_pct.pack(fill="x", pady=3)

        self.closing_pct = InputField(
            section.content, "Closing %",
            placeholder="2",
            on_change=self._trigger_input_change,
            suffix="%",
        )
        self.closing_pct.pack(fill="x", pady=3)

        self.reserve_months = InputField(
            section.content, "Reserve (mo)",
            placeholder="6",
            on_change=self._trigger_input_change,
        )
        self.reserve_months.pack(fill="x", pady=3)

        self.rent_ready = InputField(
            section.content, "Rent Ready $",
            placeholder="0",
            on_change=self._trigger_input_change,
        )
        self.rent_ready.pack(fill="x", pady=3)

    # ── Rent Section ───────────────────────────────────────────────
    def _build_rent_section(self):
        section = SectionFrame(self, title="RENT")
        section.pack(fill="x", pady=(0, 8))

        self.fmr_rent_display = DisplayField(
            section.content, "FMR Rent",
            value_color=COLORS["accent_cyan"],
        )
        self.fmr_rent_display.pack(fill="x", pady=3)

        self.manual_rent = InputField(
            section.content, "Manual Rent",
            placeholder="Override FMR",
            on_change=self._trigger_input_change,
        )
        self.manual_rent.pack(fill="x", pady=3)

        self.vacancy_rate = InputField(
            section.content, "Vacancy %",
            placeholder="5",
            on_change=self._trigger_input_change,
            suffix="%",
        )
        self.vacancy_rate.pack(fill="x", pady=3)

        self.ltl_rate = InputField(
            section.content, "LtL %",
            placeholder="0",
            on_change=self._trigger_input_change,
            suffix="%",
        )
        self.ltl_rate.pack(fill="x", pady=3)

        SeparatorRow(section.content).pack(fill="x")

        # Expense rates in this section for space efficiency
        expense_label = ctk.CTkLabel(
            section.content,
            text="Expense Rates",
            font=FONTS["small"],
            text_color=COLORS["header"],
        )
        expense_label.pack(anchor="w", pady=(4, 2))

        self.maintenance_rate = InputField(
            section.content, "Maint %",
            placeholder="15",
            on_change=self._trigger_input_change,
            suffix="%",
        )
        self.maintenance_rate.pack(fill="x", pady=3)

        self.management_rate = InputField(
            section.content, "Mgmt %",
            placeholder="10",
            on_change=self._trigger_input_change,
            suffix="%",
        )
        self.management_rate.pack(fill="x", pady=3)

        self.improvements_rate = InputField(
            section.content, "Improve %",
            placeholder="15",
            on_change=self._trigger_input_change,
            suffix="%",
        )
        self.improvements_rate.pack(fill="x", pady=3)

    # ── Utility Section ────────────────────────────────────────────
    def _build_utility_section(self):
        section = SectionFrame(self, title="UTILITIES")
        section.pack(fill="x", pady=(0, 8))

        self.has_gas_dd = DropdownField(
            section.content, "Has Gas?", ["Yes", "No"],
            on_change=lambda v: self._trigger_input_change(),
        )
        self.has_gas_dd.pack(fill="x", pady=3)

        self.heating_dd = DropdownField(
            section.content, "Heating", [],
            on_change=lambda v: self._trigger_input_change(),
        )
        self.heating_dd.pack(fill="x", pady=3)

        self.cooking_dd = DropdownField(
            section.content, "Cooking", [],
            on_change=lambda v: self._trigger_input_change(),
        )
        self.cooking_dd.pack(fill="x", pady=3)

        self.water_heating_dd = DropdownField(
            section.content, "Water Htg", [],
            on_change=lambda v: self._trigger_input_change(),
        )
        self.water_heating_dd.pack(fill="x", pady=3)

        self.use_utility_dd = DropdownField(
            section.content, "Use UA?", ["Yes", "No"],
            on_change=lambda v: self._trigger_input_change(),
        )
        self.use_utility_dd.pack(fill="x", pady=3)

    # ── Bulk set/get methods ───────────────────────────────────────

    def populate_dropdowns(self, options: dict):
        """Set dropdown values from options.json data."""
        if "cooking_types" in options:
            self.cooking_dd.update_values(options["cooking_types"])
        if "heating_types" in options:
            self.heating_dd.update_values(options["heating_types"])
        if "water_heating_types" in options:
            self.water_heating_dd.update_values(options["water_heating_types"])
        if "property_types" in options:
            self.property_type_dd.update_values(options["property_types"])
        if "bedroom_options" in options:
            displays = [b["display"] for b in options["bedroom_options"]]
            self.bedrooms_dd.update_values(displays)

    def set_state_values(self, state_names: list[str]):
        """Update the state dropdown options."""
        self.state_dd.update_values(state_names)

    def set_county_values(self, county_names: list[str]):
        """Update the county dropdown options."""
        self.county_dd.update_values(county_names)

    def set_fmr_rent(self, rent: float, year: int = 0):
        """Update the FMR rent display."""
        if rent > 0:
            text = f"${rent:,.0f}/mo"
            if year:
                text += f" ({year})"
            self.fmr_rent_display.set_value(text)
        else:
            self.fmr_rent_display.set_value("—")

    def get_all_inputs(self) -> dict:
        """Collect all current input values as a dict."""
        return {
            "state": self.state_dd.get(),
            "county": self.county_dd.get(),
            "property_type": self.property_type_dd.get(),
            "num_bedrooms": self.bedrooms_dd.get(),
            "num_units": self.num_units.get(),
            "price_per_unit": self.price_per_unit.get(),
            "manual_total_price": self.manual_total.get(),
            "zip_code": self.zip_code.get(),
            "insurance_rate": self.insurance_rate.get(),
            "tax_rate": self.tax_rate.get(),
            "loan_term": self.loan_term.get(),
            "interest_rate": self.interest_rate.get(),
            "down_payment_rate": self.down_pct.get(),
            "closing_cost_rate": self.closing_pct.get(),
            "reserve_months": self.reserve_months.get(),
            "cost_to_rent_ready": self.rent_ready.get(),
            "manual_rent": self.manual_rent.get(),
            "vacancy_rate": self.vacancy_rate.get(),
            "loss_to_lease_rate": self.ltl_rate.get(),
            "maintenance_rate": self.maintenance_rate.get(),
            "management_rate": self.management_rate.get(),
            "annual_improvements_rate": self.improvements_rate.get(),
            "has_gas": self.has_gas_dd.get(),
            "heating": self.heating_dd.get(),
            "cooking": self.cooking_dd.get(),
            "water_heating": self.water_heating_dd.get(),
            "use_utility_allowance": self.use_utility_dd.get(),
        }

    def set_all_inputs(self, inputs: 'DealInputs'):
        """Populate all fields from a DealInputs object."""
        self.state_dd.set(inputs.state)
        self.county_dd.set(inputs.county)
        self.property_type_dd.set(inputs.property_type)
        self.bedrooms_dd.set(inputs.num_bedrooms)
        self.num_units.set(str(inputs.num_units))
        self.price_per_unit.set(
            f"{inputs.price_per_unit:g}" if inputs.price_per_unit else ""
        )
        self.manual_total.set(
            f"{inputs.manual_total_price:g}"
            if inputs.manual_total_price else ""
        )
        self.zip_code.set(inputs.zip_code)
        self.insurance_rate.set(f"{inputs.insurance_rate * 100:g}")
        self.tax_rate.set(f"{inputs.tax_rate * 100:g}")
        self.loan_term.set(str(inputs.loan_term))
        self.interest_rate.set(f"{inputs.interest_rate * 100:g}")
        self.down_pct.set(f"{inputs.down_payment_rate * 100:g}")
        self.closing_pct.set(f"{inputs.closing_cost_rate * 100:g}")
        self.reserve_months.set(str(inputs.reserve_months))
        self.rent_ready.set(
            f"{inputs.cost_to_rent_ready:g}"
            if inputs.cost_to_rent_ready else ""
        )
        self.manual_rent.set(
            f"{inputs.manual_rent:g}" if inputs.manual_rent else ""
        )
        self.vacancy_rate.set(f"{inputs.vacancy_rate * 100:g}")
        self.ltl_rate.set(f"{inputs.loss_to_lease_rate * 100:g}")
        self.maintenance_rate.set(f"{inputs.maintenance_rate * 100:g}")
        self.management_rate.set(f"{inputs.management_rate * 100:g}")
        self.improvements_rate.set(
            f"{inputs.annual_improvements_rate * 100:g}"
        )
        self.has_gas_dd.set(inputs.has_gas)
        self.heating_dd.set(inputs.heating)
        self.cooking_dd.set(inputs.cooking)
        self.water_heating_dd.set(inputs.water_heating)
        self.use_utility_dd.set(inputs.use_utility_allowance)
