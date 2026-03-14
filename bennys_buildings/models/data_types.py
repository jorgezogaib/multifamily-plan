"""Data types for Benny's Buildings application."""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class State:
    """A US state/territory from HUD API."""
    name: str
    code: str           # 2-letter code (e.g., "MS")
    number: str         # FIPS number
    category: str = "State"


@dataclass
class County:
    """A county within a state from HUD API."""
    state_code: str
    fips_code: str
    county_name: str
    town_name: str = ""
    category: str = ""


@dataclass
class FMRData:
    """Fair Market Rent data from HUD API."""
    efficiency: float = 0.0
    one_bedroom: float = 0.0
    two_bedroom: float = 0.0
    three_bedroom: float = 0.0
    four_bedroom: float = 0.0
    year: int = 0

    def get_rent_by_key(self, fmr_key: str) -> float:
        """Look up rent by the FMR key name (e.g., 'Two-Bedroom')."""
        mapping = {
            "Efficiency": self.efficiency,
            "One-Bedroom": self.one_bedroom,
            "Two-Bedroom": self.two_bedroom,
            "Three-Bedroom": self.three_bedroom,
            "Four-Bedroom": self.four_bedroom,
        }
        return mapping.get(fmr_key, 0.0)


@dataclass
class ZipInfo:
    """Zip code information from RapidAPI."""
    zip_code: str = ""
    city: str = ""
    state: str = ""
    county: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    area_code: str = ""
    time_zone: str = ""


@dataclass
class UtilityAllowanceEntry:
    """A single row from the utility allowance lookup table."""
    property_type: str
    utility_service: str
    amounts: dict[str, int] = field(default_factory=dict)
    # amounts keys: "0_br", "1_br", ... "9_br"

    def get_amount(self, bedroom_key: str) -> int:
        """Get the allowance amount for a given bedroom count.

        Args:
            bedroom_key: e.g., "2_br" for 2 bedrooms
        """
        return self.amounts.get(bedroom_key, 0)


@dataclass
class DealInputs:
    """All user inputs for a property deal analysis."""
    # Property
    state: str = ""
    county: str = ""
    property_type: str = "Duplex/Townhouse/(5 Units)"
    num_bedrooms: str = "2 BR"
    num_units: int = 4
    price_per_unit: float = 0.0
    manual_total_price: Optional[float] = None
    zip_code: str = ""

    # Rates
    insurance_rate: float = 0.015
    tax_rate: float = 0.01

    # Loan
    loan_term: int = 30
    interest_rate: float = 0.065
    down_payment_rate: float = 0.25
    closing_cost_rate: float = 0.02
    reserve_months: int = 6
    cost_to_rent_ready: float = 0.0

    # Rent
    manual_rent: Optional[float] = None
    vacancy_rate: float = 0.05
    loss_to_lease_rate: float = 0.0

    # Expense rates
    maintenance_rate: float = 0.15
    management_rate: float = 0.10
    annual_improvements_rate: float = 0.15

    # Utilities
    has_gas: str = "No"
    heating: str = "Heating - Electric"
    cooking: str = "Cooking - Electric"
    water_heating: str = "Water Heating - Electric"
    use_utility_allowance: str = "No"


@dataclass
class DealData:
    """A saved deal (property analysis)."""
    name: str
    created: str = ""
    modified: str = ""
    inputs: DealInputs = field(default_factory=DealInputs)

    def __post_init__(self):
        now = datetime.now().isoformat(timespec="seconds")
        if not self.created:
            self.created = now
        if not self.modified:
            self.modified = now
