"""Formatting utilities for currency, percentages, and numbers."""


def format_currency(value: float, show_decimals: bool = False) -> str:
    """Format a number as currency.

    Args:
        value: The dollar amount.
        show_decimals: If True, show 2 decimal places.

    Returns:
        Formatted string like "$1,234" or "$1,234.56".
    """
    if value is None:
        return "$0"

    negative = value < 0
    abs_val = abs(value)

    if show_decimals:
        formatted = f"${abs_val:,.2f}"
    else:
        formatted = f"${abs_val:,.0f}"

    if negative:
        return f"-{formatted}"
    return formatted


def format_currency_negative(value: float, show_decimals: bool = False) -> str:
    """Format a negative expense value (always shown with minus sign).

    Args:
        value: The expense amount (expected negative).
        show_decimals: If True, show 2 decimal places.
    """
    return format_currency(value, show_decimals)


def format_percent(value: float, decimals: int = 1) -> str:
    """Format a decimal as a percentage.

    Args:
        value: The decimal value (e.g., 0.05 for 5%).
        decimals: Number of decimal places.

    Returns:
        Formatted string like "5.0%" or "10.52%".
    """
    if value is None:
        return "0.0%"
    return f"{value * 100:.{decimals}f}%"


def format_ratio(value: float, decimals: int = 2) -> str:
    """Format a ratio value.

    Args:
        value: The ratio (e.g., 1.57 for DSCR).
        decimals: Number of decimal places.

    Returns:
        Formatted string like "1.57".
    """
    if value is None:
        return "0.00"
    return f"{value:.{decimals}f}"


def format_months(value: int) -> str:
    """Format months value with label."""
    return f"{value} mo"


def format_years(value: int) -> str:
    """Format years value with label."""
    return f"{value} yr"


def parse_float(text: str, default: float = 0.0) -> float:
    """Safely parse a string to float.

    Handles common formats: "$1,234.56", "6.5%", "1234", empty string.

    Args:
        text: The string to parse.
        default: Value to return if parsing fails.

    Returns:
        The parsed float, or default if parsing fails.
    """
    if not text or text.strip() == "":
        return default

    # Remove currency symbols and commas
    cleaned = text.strip().replace("$", "").replace(",", "").replace("%", "")

    try:
        return float(cleaned)
    except ValueError:
        return default


def parse_int(text: str, default: int = 0) -> int:
    """Safely parse a string to int.

    Args:
        text: The string to parse.
        default: Value to return if parsing fails.

    Returns:
        The parsed int, or default if parsing fails.
    """
    if not text or text.strip() == "":
        return default

    cleaned = text.strip().replace(",", "")
    try:
        return int(float(cleaned))
    except ValueError:
        return default
