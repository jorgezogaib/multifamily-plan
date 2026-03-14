"""Property investment model — all business logic and formulas.

This is the heart of the application. It replicates every formula from
the Excel workbook's Property sheet, maintaining the exact computation
order to handle dependencies correctly.
"""

import json
from pathlib import Path
from typing import Optional, Callable

from models.data_types import DealInputs, FMRData, UtilityAllowanceEntry
from utils.financial import pmt


class UtilityAllowanceCalculator:
    """Calculates utility allowances from state-specific lookup tables.

    Replicates the Calc sheet's INDEX/MATCH logic: some utilities always
    apply (All Other Electric, AC, Sewer, Trash, Water), others are
    conditional on user selections (Cooking, Heating, Water Heating, Gas).
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir / "utility_allowances"
        self._tables: dict[str, list[UtilityAllowanceEntry]] = {}
        self._available_states: set[str] = set()
        self._discover_available_states()

    def _discover_available_states(self):
        """Scan data directory for available state JSON files."""
        if self.data_dir.exists():
            for f in self.data_dir.glob("*.json"):
                self._available_states.add(f.stem.upper())

    @property
    def available_states(self) -> set[str]:
        return self._available_states

    def has_data_for_state(self, state_code: str) -> bool:
        """Check if utility allowance data exists for a state."""
        return state_code.upper() in self._available_states

    def _load_table(self, state_code: str) -> list[UtilityAllowanceEntry]:
        """Load and cache utility allowance table for a state."""
        key = state_code.upper()
        if key in self._tables:
            return self._tables[key]

        file_path = self.data_dir / f"{state_code.lower()}.json"
        if not file_path.exists():
            return []

        with open(file_path, "r") as f:
            raw = json.load(f)

        entries = []
        for row in raw:
            amounts = {}
            for i in range(10):
                br_key = f"{i}_br"
                amounts[br_key] = row.get(br_key, 0)

            entries.append(UtilityAllowanceEntry(
                property_type=row["property_type"],
                utility_service=row["utility_service"],
                amounts=amounts,
            ))

        self._tables[key] = entries
        return entries

    def _lookup(self, table: list[UtilityAllowanceEntry],
                property_type: str, utility_service: str,
                bedroom_key: str) -> int:
        """Look up a single utility allowance amount."""
        for entry in table:
            if (entry.property_type == property_type and
                    entry.utility_service == utility_service):
                return entry.get_amount(bedroom_key)
        return 0

    def calculate(self, state_code: str, property_type: str,
                  bedroom_key: str, heating: str, cooking: str,
                  water_heating: str, has_gas: str) -> dict[str, int]:
        """Calculate all utility allowances for given selections.

        Returns a dict mapping utility service names to monthly amounts,
        plus a 'total' key with the sum.
        """
        table = self._load_table(state_code)
        if not table:
            return {"total": 0}

        result = {}

        # Always-applied utilities
        always_on = [
            "All Other Electric",
            "Electric Air Conditioning",
            "Sewer",
            "Trash Collection",
            "Water",
        ]
        for service in always_on:
            amount = self._lookup(table, property_type, service, bedroom_key)
            result[service] = amount

        # Conditional: Cooking (Electric or Natural Gas based on selection)
        cooking_service = cooking  # e.g., "Cooking - Electric"
        result[cooking_service] = self._lookup(
            table, property_type, cooking_service, bedroom_key
        )

        # Conditional: Heating (Electric, Heat Pump, or Natural Gas)
        heating_service = heating  # e.g., "Heating - Electric"
        result[heating_service] = self._lookup(
            table, property_type, heating_service, bedroom_key
        )

        # Conditional: Water Heating
        wh_service = water_heating  # e.g., "Water Heating - Electric"
        result[wh_service] = self._lookup(
            table, property_type, wh_service, bedroom_key
        )

        # Conditional: Fixed Gas (only if has_gas == "Yes")
        if has_gas == "Yes":
            result["Fixed - Gas"] = self._lookup(
                table, property_type, "Fixed - Gas", bedroom_key
            )
        else:
            result["Fixed - Gas"] = 0

        result["total"] = sum(result.values())
        return result


class PropertyModel:
    """Investment analysis model with all 24 formulas.

    Holds all input values, computes all derived values on recalculate(),
    and notifies listeners when values change.
    """

    def __init__(self, data_dir: Path):
        self._inputs = DealInputs()
        self._fmr_data = FMRData()
        self._utility_calc = UtilityAllowanceCalculator(data_dir)
        self._state_code: str = ""  # 2-letter code for utility lookup
        self._listeners: list[Callable] = []

        # --- Computed values (outputs) ---
        # Purchase section
        self.total_price: float = 0.0
        self.closing_costs: float = 0.0
        self.down_payment: float = 0.0
        self.total_leverage: float = 0.0
        self.reserve_account: float = 0.0
        self.total_capital_required: float = 0.0

        # Income section
        self.fmr_rent: float = 0.0
        self.effective_rent: float = 0.0  # rent used (manual or FMR)
        self.potential_gross_rent: float = 0.0
        self.vacancy: float = 0.0
        self.loss_to_lease: float = 0.0
        self.effective_gross_rent: float = 0.0

        # Expense section
        self.maintenance: float = 0.0
        self.management: float = 0.0
        self.annual_improvements: float = 0.0
        self.utility_allowance_monthly: float = 0.0
        self.utility_allowance_yearly: float = 0.0
        self.utility_detail: dict[str, int] = {}
        self.insurance: float = 0.0
        self.taxes: float = 0.0
        self.total_expenses: float = 0.0
        self.expense_ratio: float = 0.0

        # Returns section
        self.noi: float = 0.0
        self.debt_service: float = 0.0
        self.annual_cashflow: float = 0.0
        self.monthly_cashflow: float = 0.0
        self.cashflow_margin: float = 0.0
        self.cash_on_cash: float = 0.0
        self.cap_rate: float = 0.0
        self.dscr: float = 0.0

    # --- Properties ---

    @property
    def inputs(self) -> DealInputs:
        return self._inputs

    @inputs.setter
    def inputs(self, value: DealInputs):
        self._inputs = value
        self.recalculate()

    @property
    def fmr_data(self) -> FMRData:
        return self._fmr_data

    @fmr_data.setter
    def fmr_data(self, value: FMRData):
        self._fmr_data = value
        self.recalculate()

    @property
    def state_code(self) -> str:
        return self._state_code

    @state_code.setter
    def state_code(self, value: str):
        self._state_code = value

    # --- Listener management ---

    def add_listener(self, callback: Callable):
        """Register a callback to be called after recalculation."""
        self._listeners.append(callback)

    def _notify_listeners(self):
        for cb in self._listeners:
            try:
                cb()
            except Exception:
                pass  # Don't let listener errors break recalculation

    # --- Bedroom key helper ---

    def _get_bedroom_key(self) -> str:
        """Convert bedroom display string (e.g., '2 BR') to lookup key ('2_br')."""
        display = self._inputs.num_bedrooms
        if display and " " in display:
            num = display.split(" ")[0]
            return f"{num}_br"
        return "2_br"

    def _get_fmr_key(self) -> str:
        """Get the FMR key for current bedroom selection."""
        # Load options mapping
        from pathlib import Path
        mapping = {
            "0 BR": "Efficiency",
            "1 BR": "One-Bedroom",
            "2 BR": "Two-Bedroom",
            "3 BR": "Three-Bedroom",
            "4 BR": "Four-Bedroom",
            "5 BR": "Five-Bedroom",
        }
        return mapping.get(self._inputs.num_bedrooms, "Two-Bedroom")

    # --- Core recalculation ---

    def recalculate(self):
        """Recompute all derived values from current inputs.

        Follows the exact computation order from the Excel workbook to
        handle dependencies correctly. This runs in microseconds so we
        recalculate everything on any input change.
        """
        inp = self._inputs

        # 1. Total Price (manual override or calculated)
        if inp.manual_total_price is not None and inp.manual_total_price > 0:
            self.total_price = inp.manual_total_price
        else:
            self.total_price = inp.price_per_unit * inp.num_units

        # 2-4. Purchase costs and leverage
        self.closing_costs = self.total_price * inp.closing_cost_rate
        self.down_payment = self.total_price * inp.down_payment_rate
        self.total_leverage = self.total_price - self.down_payment

        # 5-6. Insurance and Taxes (depend only on total_price)
        self.insurance = self.total_price * -inp.insurance_rate
        self.taxes = self.total_price * -inp.tax_rate

        # 7. Debt Service (depends on total_leverage)
        if inp.interest_rate > 0 and inp.loan_term > 0 and self.total_leverage > 0:
            monthly_payment = pmt(
                inp.interest_rate / 12,
                inp.loan_term * 12,
                self.total_leverage,
            )
            self.debt_service = monthly_payment * 12
        else:
            self.debt_service = 0.0

        # 8. Reserve Account (depends on debt_service, insurance, taxes)
        self.reserve_account = abs(
            self.debt_service + self.insurance + self.taxes
        ) * (inp.reserve_months / 12)

        # 9. Total Capital Required
        self.total_capital_required = (
            self.closing_costs
            + self.down_payment
            + self.reserve_account
            + inp.cost_to_rent_ready
        )

        # 10. Rent (manual override or FMR)
        fmr_key = self._get_fmr_key()
        self.fmr_rent = self._fmr_data.get_rent_by_key(fmr_key)

        if inp.manual_rent is not None and inp.manual_rent > 0:
            self.effective_rent = inp.manual_rent
        else:
            self.effective_rent = self.fmr_rent

        # 11-14. Income section
        self.potential_gross_rent = self.effective_rent * 12 * inp.num_units
        self.vacancy = -self.potential_gross_rent * inp.vacancy_rate
        self.loss_to_lease = -self.potential_gross_rent * inp.loss_to_lease_rate
        self.effective_gross_rent = (
            self.potential_gross_rent + self.vacancy + self.loss_to_lease
        )

        # 15. Operating expenses (based on EGR)
        self.maintenance = self.effective_gross_rent * -inp.maintenance_rate
        self.management = self.effective_gross_rent * -inp.management_rate
        self.annual_improvements = self.effective_gross_rent * -inp.annual_improvements_rate

        # 16. Utility Allowance
        bedroom_key = self._get_bedroom_key()
        if inp.use_utility_allowance == "Yes" and self._state_code:
            self.utility_detail = self._utility_calc.calculate(
                state_code=self._state_code,
                property_type=inp.property_type,
                bedroom_key=bedroom_key,
                heating=inp.heating,
                cooking=inp.cooking,
                water_heating=inp.water_heating,
                has_gas=inp.has_gas,
            )
            self.utility_allowance_monthly = self.utility_detail.get("total", 0)
            self.utility_allowance_yearly = (
                self.utility_allowance_monthly * -12 * inp.num_units
            )
        else:
            self.utility_detail = {}
            self.utility_allowance_monthly = 0
            self.utility_allowance_yearly = 0

        # 17. Total Expenses
        self.total_expenses = (
            self.maintenance
            + self.management
            + self.annual_improvements
            + self.utility_allowance_yearly
            + self.insurance
            + self.taxes
        )

        # Expense ratio
        if self.effective_gross_rent != 0:
            self.expense_ratio = -self.total_expenses / self.effective_gross_rent
        else:
            self.expense_ratio = 0.0

        # 18-24. Returns
        self.noi = self.effective_gross_rent - abs(self.total_expenses)

        self.annual_cashflow = self.noi + self.debt_service

        if self.annual_cashflow != 0:
            self.monthly_cashflow = self.annual_cashflow / 12
        else:
            self.monthly_cashflow = 0.0

        if self.effective_gross_rent != 0:
            self.cashflow_margin = self.annual_cashflow / self.effective_gross_rent
        else:
            self.cashflow_margin = 0.0

        if self.total_capital_required != 0:
            self.cash_on_cash = self.annual_cashflow / self.total_capital_required
        else:
            self.cash_on_cash = 0.0

        if self.total_price != 0:
            self.cap_rate = self.noi / self.total_price
        else:
            self.cap_rate = 0.0

        if self.debt_service != 0:
            self.dscr = self.noi / abs(self.debt_service)
        else:
            self.dscr = 0.0

        self._notify_listeners()

    # --- Utility helpers for the controller ---

    def has_utility_data(self) -> bool:
        """Check if utility allowance data is available for current state."""
        return self._utility_calc.has_data_for_state(self._state_code)

    def get_available_utility_states(self) -> set[str]:
        """Get set of state codes that have utility allowance data."""
        return self._utility_calc.available_states
