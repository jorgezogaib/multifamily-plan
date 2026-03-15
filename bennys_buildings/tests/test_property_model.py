"""Tests for the PropertyModel — verifies all formulas against known Excel values.

Test case uses the current workbook state:
    State: Mississippi, County: Forrest County
    Property Type: Duplex/Townhouse (<5 Units)
    4 units @ $62,499.75/unit
    6.5% interest, 30yr, 25% down, 2% closing, 6 months reserve
    2 BR, FMR Rent: $1,047
    Vacancy: 5%, LtL: 0%
    Maintenance: 15%, Management: 10%, Improvements: 15%
    Insurance: 1.5%, Tax: 1.0%
    Utility Allowance: Off
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.property_model import PropertyModel
from models.data_types import DealInputs, FMRData


def get_test_model() -> PropertyModel:
    """Create a PropertyModel with the Excel workbook's test values."""
    data_dir = Path(__file__).parent.parent / "data"
    model = PropertyModel(data_dir)

    # Set FMR data (from HUD API)
    model.fmr_data = FMRData(
        efficiency=766,
        one_bedroom=888,
        two_bedroom=1047,
        three_bedroom=1348,
        four_bedroom=1386,
        year=2026,
    )

    # Set inputs matching the workbook
    model._inputs = DealInputs(
        state="Mississippi",
        county="Forrest County",
        property_type="Duplex/Townhouse (<5 Units)",
        num_bedrooms="2 BR",
        num_units=4,
        price_per_unit=62499.75,
        manual_total_price=None,
        zip_code="70816",
        insurance_rate=0.015,
        tax_rate=0.01,
        loan_term=30,
        interest_rate=0.065,
        down_payment_rate=0.25,
        closing_cost_rate=0.02,
        reserve_months=6,
        cost_to_rent_ready=0,
        manual_rent=None,
        vacancy_rate=0.05,
        loss_to_lease_rate=0.0,
        maintenance_rate=0.15,
        management_rate=0.10,
        annual_improvements_rate=0.15,
        has_gas="No",
        heating="Heating - Electric",
        cooking="Cooking - Electric",
        water_heating="Water Heating - Electric",
        use_utility_allowance="No",
    )

    model.state_code = "MS"
    model.recalculate()
    return model


def test_total_price():
    model = get_test_model()
    assert abs(model.total_price - 249999) < 1, \
        f"Total Price: expected ~249999, got {model.total_price:.2f}"


def test_closing_costs():
    model = get_test_model()
    expected = 249999 * 0.02  # $5,000
    assert abs(model.closing_costs - expected) < 1, \
        f"Closing Costs: expected ~{expected:.0f}, got {model.closing_costs:.2f}"


def test_down_payment():
    model = get_test_model()
    expected = 249999 * 0.25  # $62,500
    assert abs(model.down_payment - expected) < 1, \
        f"Down Payment: expected ~{expected:.0f}, got {model.down_payment:.2f}"


def test_total_leverage():
    model = get_test_model()
    expected = 249999 - 249999 * 0.25  # $187,499
    assert abs(model.total_leverage - expected) < 1, \
        f"Total Leverage: expected ~{expected:.0f}, got {model.total_leverage:.2f}"


def test_potential_gross_rent():
    model = get_test_model()
    expected = 1047 * 12 * 4  # $50,256
    assert abs(model.potential_gross_rent - expected) < 1, \
        f"PGR: expected {expected}, got {model.potential_gross_rent:.2f}"


def test_effective_gross_rent():
    model = get_test_model()
    pgr = 1047 * 12 * 4
    expected = pgr + (-pgr * 0.05) + 0  # PGR - vacancy - 0 LtL
    assert abs(model.effective_gross_rent - expected) < 1, \
        f"EGR: expected ~{expected:.0f}, got {model.effective_gross_rent:.2f}"


def test_insurance():
    model = get_test_model()
    expected = 249999 * -0.015  # -$3,750
    assert abs(model.insurance - expected) < 1, \
        f"Insurance: expected ~{expected:.0f}, got {model.insurance:.2f}"


def test_taxes():
    model = get_test_model()
    expected = 249999 * -0.01  # -$2,500
    assert abs(model.taxes - expected) < 1, \
        f"Taxes: expected ~{expected:.0f}, got {model.taxes:.2f}"


def test_debt_service():
    model = get_test_model()
    # Excel gives ~-$14,221 annual
    assert abs(model.debt_service - (-14221)) < 5, \
        f"Debt Service: expected ~-14221, got {model.debt_service:.2f}"


def test_noi():
    model = get_test_model()
    # Excel gives ~$22,396
    assert abs(model.noi - 22396) < 5, \
        f"NOI: expected ~22396, got {model.noi:.2f}"


def test_annual_cashflow():
    model = get_test_model()
    # Excel gives ~$8,174
    assert abs(model.annual_cashflow - 8174) < 10, \
        f"Annual Cashflow: expected ~8174, got {model.annual_cashflow:.2f}"


def test_monthly_cashflow():
    model = get_test_model()
    # Excel gives ~$681.21
    assert abs(model.monthly_cashflow - 681.21) < 1, \
        f"Monthly CF: expected ~681.21, got {model.monthly_cashflow:.2f}"


def test_cash_on_cash():
    model = get_test_model()
    # Excel gives ~10.52%
    assert abs(model.cash_on_cash - 0.1052) < 0.005, \
        f"Cash on Cash: expected ~10.52%, got {model.cash_on_cash * 100:.2f}%"


def test_cap_rate():
    model = get_test_model()
    # Excel gives ~8.96%
    assert abs(model.cap_rate - 0.0896) < 0.005, \
        f"Cap Rate: expected ~8.96%, got {model.cap_rate * 100:.2f}%"


def test_dscr():
    model = get_test_model()
    # Excel gives ~1.57
    assert abs(model.dscr - 1.57) < 0.02, \
        f"DSCR: expected ~1.57, got {model.dscr:.2f}"


def test_cashflow_margin():
    model = get_test_model()
    # Excel gives ~17.12%
    assert abs(model.cashflow_margin - 0.1712) < 0.005, \
        f"CF Margin: expected ~17.12%, got {model.cashflow_margin * 100:.2f}%"


def test_total_expenses():
    model = get_test_model()
    # Excel gives ~-$25,347
    assert abs(model.total_expenses - (-25347)) < 10, \
        f"Total Expenses: expected ~-25347, got {model.total_expenses:.2f}"


def test_expense_ratio():
    model = get_test_model()
    # Expense ratio = |total_expenses| / EGR ≈ 53.1%
    assert abs(model.expense_ratio - 0.531) < 0.01, \
        f"Expense Ratio: expected ~53.1%, got {model.expense_ratio * 100:.1f}%"


def test_grm():
    model = get_test_model()
    # GRM = 249999 / (1047 * 12 * 4) = 249999 / 50256 ≈ 4.97
    assert abs(model.grm - 4.97) < 0.05, \
        f"GRM: expected ~4.97, got {model.grm:.2f}"


def test_breakeven_occupancy():
    model = get_test_model()
    # BEO = (|total_expenses| + |debt_service|) / PGR
    # ≈ (25347 + 14221) / 50256 ≈ 0.787
    assert abs(model.breakeven_occupancy - 0.787) < 0.02, \
        f"BEO: expected ~78.7%, got {model.breakeven_occupancy * 100:.1f}%"


def test_price_per_bedroom():
    model = get_test_model()
    # Price/BR = 249999 / (2 * 4) = 249999 / 8 ≈ 31250
    assert abs(model.price_per_bedroom - 31250) < 1, \
        f"Price/BR: expected ~31250, got {model.price_per_bedroom:.2f}"


if __name__ == "__main__":
    tests = [
        test_total_price,
        test_closing_costs,
        test_down_payment,
        test_total_leverage,
        test_potential_gross_rent,
        test_effective_gross_rent,
        test_insurance,
        test_taxes,
        test_debt_service,
        test_noi,
        test_annual_cashflow,
        test_monthly_cashflow,
        test_cash_on_cash,
        test_cap_rate,
        test_dscr,
        test_cashflow_margin,
        test_total_expenses,
        test_expense_ratio,
        test_grm,
        test_breakeven_occupancy,
        test_price_per_bedroom,
    ]

    passed = 0
    failed = 0
    for test_fn in tests:
        try:
            test_fn()
            print(f"  PASS  {test_fn.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {test_fn.__name__}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed out of {len(tests)} tests")
