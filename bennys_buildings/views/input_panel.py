"""Input panel — all user inputs organized in collapsible accordion sections.

This is the right column of the dashboard containing dropdowns for
property configuration, entry fields for financial parameters, and
the cascading State -> County behavior.
"""

import customtkinter as ctk
from typing import Optional, Callable

from views.widgets import (
    InputField, DropdownField, SearchableDropdown,
    RadioField, DisplayField, SeparatorRow,
    CollapsibleSection, COLORS, FONTS
)


class InputPanel(ctk.CTkFrame):
    """Accordion panel containing all user input fields."""

    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color="transparent",
            **kwargs,
        )

        # ── Callbacks (set by controller) ──
        self.on_state_changed: Optional[Callable] = None
        self.on_county_changed: Optional[Callable] = None
        self.on_input_changed: Optional[Callable] = None
        self.on_zip_changed: Optional[Callable] = None
        self.on_ua_toggled: Optional[Callable] = None

        # Lock width — prevent resizing when switching sections
        self.pack_propagate(False)
        self.grid_propagate(False)

        # ── Scrollable container ──
        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent_teal"],
        )
        self._scroll.pack(fill="both", expand=True)

        # ── Accordion sections ──
        self._sections: list[CollapsibleSection] = []

        self._property_section = CollapsibleSection(
            self._scroll, "Property",
            on_toggle=self._on_section_toggled,
        )
        self._property_section.pack(fill="x", pady=(0, 4))
        self._sections.append(self._property_section)

        self._financials_section = CollapsibleSection(
            self._scroll, "Financials",
            on_toggle=self._on_section_toggled,
        )
        self._financials_section.pack(fill="x", pady=4)
        self._sections.append(self._financials_section)

        self._utilities_section = CollapsibleSection(
            self._scroll, "Utilities",
            on_toggle=self._on_section_toggled,
        )
        self._utilities_section.pack(fill="x", pady=(4, 0))
        self._sections.append(self._utilities_section)

        self._build_property_section()
        self._build_financials_section()
        self._build_utility_section()

        # Start with Property expanded
        self._property_section.expand()

    # ── Accordion behaviour ──

    def _on_section_toggled(self, toggled_section, is_expanded):
        """When one section opens, close all others."""
        if is_expanded:
            for section in self._sections:
                if section is not toggled_section:
                    section.collapse()

    # ── Callbacks ──

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

    def _on_price_per_unit_changed(self):
        """When $/Unit gets a value, clear Total $."""
        if self.price_per_unit.get().strip():
            self.manual_total.set("")
        self._trigger_input_change()

    def _on_manual_total_changed(self):
        """When Total $ gets a value, clear $/Unit."""
        if self.manual_total.get().strip():
            self.price_per_unit.set("")
        self._trigger_input_change()

    def _add_group_label(self, parent, text):
        """Small section label within a group."""
        lbl = ctk.CTkLabel(
            parent, text=text,
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS["header"],
            anchor="w",
        )
        lbl.pack(fill="x", padx=14, pady=(6, 2))

    # ── Property Section ──────────────────────────────────────
    def _build_property_section(self):
        container = self._property_section.content

        self.street_address = InputField(
            container, "Address",
            placeholder="123 Main St",
            on_change=self._trigger_input_change,
        )
        self.street_address.pack(fill="x", pady=3, padx=12)

        self.state_dd = SearchableDropdown(
            container, "State", [],
            on_change=self._trigger_state_change,
        )
        self.state_dd.pack(fill="x", pady=3, padx=12)

        self.county_dd = SearchableDropdown(
            container, "County", [],
            on_change=self._trigger_county_change,
        )
        self.county_dd.pack(fill="x", pady=3, padx=12)

        self.zip_code = InputField(
            container, "Zip Code",
            placeholder="70816",
            on_change=self._trigger_zip_change,
        )
        self.zip_code.pack(fill="x", pady=3, padx=12)

        self.property_type_dd = RadioField(
            container, "Type", [],
            on_change=lambda v: self._trigger_input_change(),
            orientation="vertical",
        )
        self.property_type_dd.pack(fill="x", pady=3, padx=12)

        self.bedrooms_dd = DropdownField(
            container, "Bedrooms", [],
            on_change=lambda v: self._trigger_input_change(),
        )
        self.bedrooms_dd.pack(fill="x", pady=3, padx=12)

        self.num_units = InputField(
            container, "# Units",
            placeholder="4",
            on_change=self._trigger_input_change,
        )
        self.num_units.pack(fill="x", pady=3, padx=12)

        self.price_per_unit = InputField(
            container, "$ / Unit",
            placeholder="Leave blank if providing Total $",
            on_change=self._on_price_per_unit_changed,
        )
        self.price_per_unit.pack(fill="x", pady=3, padx=12)

        self.manual_total = InputField(
            container, "Total $ (opt)",
            placeholder="Leave blank if providing $ / Unit",
            on_change=self._on_manual_total_changed,
        )
        self.manual_total.pack(fill="x", pady=3, padx=12)

        self.rent_ready = InputField(
            container, "Rent Ready $",
            placeholder="0",
            on_change=self._trigger_input_change,
        )
        self.rent_ready.pack(fill="x", pady=3, padx=12)

    # ── Financials Section (Loan + Revenue + Expenses) ────────
    def _build_financials_section(self):
        container = self._financials_section.content

        # ── Loan Terms ──
        self._add_group_label(container, "LOAN")

        self.loan_term = InputField(
            container, "Term (yr)",
            placeholder="30",
            on_change=self._trigger_input_change,
        )
        self.loan_term.pack(fill="x", pady=2, padx=12)

        self.interest_rate = InputField(
            container, "Rate %",
            placeholder="6.5",
            on_change=self._trigger_input_change,
            suffix="%",
        )
        self.interest_rate.pack(fill="x", pady=2, padx=12)

        self._rate_hint = ctk.CTkLabel(
            container, text="",
            font=("Segoe UI", 10),
            text_color=COLORS["text_muted"],
            anchor="e",
        )
        self._rate_hint.pack(fill="x", padx=14, pady=(0, 2))

        self.down_pct = InputField(
            container, "Down %",
            placeholder="25",
            on_change=self._trigger_input_change,
            suffix="%",
        )
        self.down_pct.pack(fill="x", pady=2, padx=12)

        self.closing_pct = InputField(
            container, "Closing %",
            placeholder="2",
            on_change=self._trigger_input_change,
            suffix="%",
        )
        self.closing_pct.pack(fill="x", pady=2, padx=12)

        self.reserve_months = InputField(
            container, "Reserve (mo)",
            placeholder="6",
            on_change=self._trigger_input_change,
        )
        self.reserve_months.pack(fill="x", pady=2, padx=12)

        # ── Revenue ──
        self._add_group_label(container, "REVENUE")

        self.fmr_rent_display = DisplayField(
            container, "FMR Rent",
            value_color=COLORS["accent_cyan"],
        )
        self.fmr_rent_display.pack(fill="x", pady=2, padx=12)

        self.manual_rent = InputField(
            container, "Manual Rent",
            placeholder="Override FMR",
            on_change=self._trigger_input_change,
        )
        self.manual_rent.pack(fill="x", pady=2, padx=12)

        self.vacancy_rate = InputField(
            container, "Vacancy %",
            placeholder="5",
            on_change=self._trigger_input_change,
            suffix="%",
        )
        self.vacancy_rate.pack(fill="x", pady=2, padx=12)

        self.ltl_rate = InputField(
            container, "LtL %",
            placeholder="0",
            on_change=self._trigger_input_change,
            suffix="%",
        )
        self.ltl_rate.pack(fill="x", pady=2, padx=12)

        # ── Expenses ──
        self._add_group_label(container, "EXPENSES")

        self.maintenance_rate = InputField(
            container, "Maint %",
            placeholder="15",
            on_change=self._trigger_input_change,
            suffix="%",
        )
        self.maintenance_rate.pack(fill="x", pady=2, padx=12)

        self.management_rate = InputField(
            container, "Mgmt %",
            placeholder="10",
            on_change=self._trigger_input_change,
            suffix="%",
        )
        self.management_rate.pack(fill="x", pady=2, padx=12)

        self.improvements_rate = InputField(
            container, "Improve %",
            placeholder="15",
            on_change=self._trigger_input_change,
            suffix="%",
        )
        self.improvements_rate.pack(fill="x", pady=2, padx=12)

        self.insurance_rate = InputField(
            container, "Insurance %",
            placeholder="1.5",
            on_change=self._trigger_input_change,
            suffix="%",
        )
        self.insurance_rate.pack(fill="x", pady=2, padx=12)

        self.tax_rate = InputField(
            container, "Tax %",
            placeholder="1.0",
            on_change=self._trigger_input_change,
            suffix="%",
        )
        self.tax_rate.pack(fill="x", pady=2, padx=12)

    # ── Utilities Section ─────────────────────────────────────
    def _build_utility_section(self):
        container = self._utilities_section.content

        self.use_utility_dd = RadioField(
            container, "Use UA?", ["Yes", "No"],
            default="No",
            on_change=self._on_ua_toggled,
        )
        self.use_utility_dd.pack(fill="x", pady=3, padx=12)

        # Container for utility detail fields — hidden when UA is No
        self._ua_fields_frame = ctk.CTkFrame(
            container, fg_color="transparent"
        )

        self.has_gas_dd = DropdownField(
            self._ua_fields_frame, "Has Gas?", ["Yes", "No"],
            on_change=lambda v: self._trigger_input_change(),
        )
        self.has_gas_dd.pack(fill="x", pady=3, padx=12)

        self.heating_dd = DropdownField(
            self._ua_fields_frame, "Heating", [],
            on_change=lambda v: self._trigger_input_change(),
        )
        self.heating_dd.pack(fill="x", pady=3, padx=12)

        self.cooking_dd = DropdownField(
            self._ua_fields_frame, "Cooking", [],
            on_change=lambda v: self._trigger_input_change(),
        )
        self.cooking_dd.pack(fill="x", pady=3, padx=12)

        self.water_heating_dd = DropdownField(
            self._ua_fields_frame, "Water Htg", [],
            on_change=lambda v: self._trigger_input_change(),
        )
        self.water_heating_dd.pack(fill="x", pady=3, padx=12)

        # Start hidden (default is No)

    def _on_ua_toggled(self, value: str):
        """Show/hide utility detail fields based on Use UA toggle."""
        if value == "Yes":
            self._ua_fields_frame.pack(fill="x", after=self.use_utility_dd)
        else:
            self._ua_fields_frame.pack_forget()
        self._trigger_input_change()
        if hasattr(self, 'on_ua_toggled') and self.on_ua_toggled:
            self.on_ua_toggled(value)

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
            self.fmr_rent_display.set_value("\u2014")

    def set_rate_hint(self, rate: Optional[float]):
        """Show current market mortgage rate as a hint."""
        if rate and rate > 0:
            self._rate_hint.configure(text=f"Current avg: {rate:.2f}%")
        else:
            self._rate_hint.configure(text="")

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
            "street_address": self.street_address.get(),
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
        self.street_address.set(inputs.street_address)
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
        # Sync UA field visibility
        self._on_ua_toggled(inputs.use_utility_allowance)
