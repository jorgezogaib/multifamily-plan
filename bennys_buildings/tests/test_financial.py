"""Tests for the PMT financial function."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.financial import pmt


def test_pmt_standard():
    """Test PMT with standard mortgage parameters.
    Excel: =PMT(6.5%/12, 30*12, 187499.25) = -$1,185.07/mo
    """
    monthly = pmt(0.065 / 12, 30 * 12, 187499.25)
    assert abs(monthly - (-1185.07)) < 0.10, f"Expected ~-1185.07, got {monthly:.2f}"


def test_pmt_zero_rate():
    """Test PMT with 0% interest rate."""
    monthly = pmt(0, 360, 100000)
    assert abs(monthly - (-277.78)) < 0.01, f"Expected ~-277.78, got {monthly:.2f}"


def test_pmt_zero_leverage():
    """Test PMT when there's no loan."""
    monthly = pmt(0.065 / 12, 360, 0)
    assert monthly == 0.0, f"Expected 0.0, got {monthly}"


def test_pmt_annual_debt_service():
    """Test annual debt service for the workbook's test case.
    Leverage = $249,999 - $62,500 = $187,499.25 (approx)
    Excel: debt_service = PMT(6.5%/12, 360, 187499.25) * 12 ≈ -$14,221
    """
    leverage = 249999 - 249999 * 0.25  # 187499.25
    annual = pmt(0.065 / 12, 360, leverage) * 12
    assert abs(annual - (-14220.85)) < 1.0, f"Expected ~-14221, got {annual:.2f}"


if __name__ == "__main__":
    test_pmt_standard()
    test_pmt_zero_rate()
    test_pmt_zero_leverage()
    test_pmt_annual_debt_service()
    print("All PMT tests passed!")
