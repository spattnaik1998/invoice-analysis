"""
Helper Functions Module

This module contains utility functions used across the application.
"""

from typing import Optional


def format_currency(value: float, currency_symbol: str = "$") -> str:
    """
    Format a number as currency with thousands separator.

    Args:
        value (float): Numeric value to format
        currency_symbol (str): Currency symbol to use

    Returns:
        str: Formatted currency string (e.g., "$1,234,567.89")
    """
    return f"{currency_symbol}{value:,.2f}"


def format_number(value: int) -> str:
    """
    Format an integer with thousands separator.

    Args:
        value (int): Integer value to format

    Returns:
        str: Formatted number string (e.g., "123,456")
    """
    return f"{value:,}"


def calculate_percentage_change(
    current: float,
    previous: float
) -> Optional[float]:
    """
    Calculate percentage change between two values.

    Args:
        current (float): Current period value
        previous (float): Previous period value

    Returns:
        Optional[float]: Percentage change, or None if previous is 0
    """
    if previous == 0:
        return None

    return ((current - previous) / previous) * 100
