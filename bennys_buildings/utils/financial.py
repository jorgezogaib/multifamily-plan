"""Financial calculation utilities."""


def pmt(rate_per_period: float, num_periods: int, present_value: float) -> float:
    """Calculate periodic payment amount, matching Excel's PMT function.

    Args:
        rate_per_period: Interest rate per period (e.g., annual_rate / 12).
        num_periods: Total number of payment periods.
        present_value: Loan principal (present value).

    Returns:
        The payment amount per period (negative, representing cash outflow).
    """
    if rate_per_period == 0:
        if num_periods == 0:
            return 0.0
        return -present_value / num_periods

    factor = (1 + rate_per_period) ** num_periods
    return -present_value * (rate_per_period * factor) / (factor - 1)
