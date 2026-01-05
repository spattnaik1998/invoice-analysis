"""
Utilities package for Invoice Analytics Dashboard.

This package contains helper functions and utilities.
"""

from .helpers import format_currency, format_number, calculate_percentage_change
from .filters import (
    filter_by_years,
    filter_by_products,
    filter_by_date_range,
    apply_combined_filters,
    FilterError
)
from .kpis import (
    calculate_total_revenue,
    calculate_total_quantity,
    calculate_average_transaction_value,
    calculate_num_transactions,
    calculate_all_kpis,
    calculate_unique_customers,
    calculate_unique_products,
    KPIError
)

__all__ = [
    # Formatting helpers
    'format_currency',
    'format_number',
    'calculate_percentage_change',
    # Filtering functions
    'filter_by_years',
    'filter_by_products',
    'filter_by_date_range',
    'apply_combined_filters',
    'FilterError',
    # KPI functions
    'calculate_total_revenue',
    'calculate_total_quantity',
    'calculate_average_transaction_value',
    'calculate_num_transactions',
    'calculate_all_kpis',
    'calculate_unique_customers',
    'calculate_unique_products',
    'KPIError'
]
