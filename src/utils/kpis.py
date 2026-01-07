"""
KPI Computation Module

This module provides reusable functions for calculating Key Performance Indicators
from invoice data. All functions accept filtered DataFrames and handle edge cases
gracefully.

KPIs:
- Total Revenue
- Total Quantity Sold
- Average Transaction Value
- Number of Transactions
"""

import pandas as pd
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class KPIError(Exception):
    """Custom exception for KPI computation errors."""
    pass


def calculate_total_revenue(
    df: pd.DataFrame,
    qty_column: str = 'qty',
    amount_column: str = 'amount',
    total_amount_column: str = 'total_amount'
) -> float:
    """
    Calculate total revenue from invoice data.

    This function computes the sum of all transaction amounts. It first tries
    to use a pre-computed total_amount column if available, otherwise calculates
    it from qty * amount.

    Args:
        df (pd.DataFrame): Input DataFrame (can be filtered)
        qty_column (str): Name of quantity column. Defaults to 'qty'
        amount_column (str): Name of unit amount column. Defaults to 'amount'
        total_amount_column (str): Name of total amount column. Defaults to 'total_amount'

    Returns:
        float: Total revenue across all transactions. Returns 0.0 for empty DataFrame.

    Raises:
        KPIError: If required columns are missing from DataFrame

    Examples:
        >>> total = calculate_total_revenue(df)
        >>> print(f"Total Revenue: ${total:,.2f}")
    """
    # Handle None or empty DataFrame
    if df is None or df.empty:
        logger.info("calculate_total_revenue: Empty DataFrame, returning 0.0")
        return 0.0

    # Try to use pre-computed total_amount column
    if total_amount_column in df.columns:
        try:
            revenue = df[total_amount_column].sum()
            logger.debug(f"calculate_total_revenue: ${revenue:,.2f} from {len(df):,} rows")
            return float(revenue)
        except Exception as e:
            logger.warning(f"Error using {total_amount_column} column: {e}")

    # Fall back to calculating from qty * amount
    if qty_column in df.columns and amount_column in df.columns:
        try:
            revenue = (df[qty_column] * df[amount_column]).sum()
            logger.debug(f"calculate_total_revenue: ${revenue:,.2f} (calculated from qty*amount)")
            return float(revenue)
        except Exception as e:
            error_msg = f"Error calculating revenue from {qty_column} * {amount_column}: {e}"
            logger.error(error_msg)
            raise KPIError(error_msg)

    # Missing required columns
    error_msg = (
        f"Cannot calculate revenue: DataFrame must contain either '{total_amount_column}' "
        f"or both '{qty_column}' and '{amount_column}'. "
        f"Available columns: {', '.join(df.columns)}"
    )
    logger.error(error_msg)
    raise KPIError(error_msg)


def calculate_total_quantity(
    df: pd.DataFrame,
    qty_column: str = 'qty'
) -> int:
    """
    Calculate total quantity sold across all transactions.

    Args:
        df (pd.DataFrame): Input DataFrame (can be filtered)
        qty_column (str): Name of quantity column. Defaults to 'qty'

    Returns:
        int: Total quantity sold. Returns 0 for empty DataFrame.

    Raises:
        KPIError: If qty column is missing from DataFrame

    Examples:
        >>> qty = calculate_total_quantity(df)
        >>> print(f"Total Quantity: {qty:,} units")
    """
    # Handle None or empty DataFrame
    if df is None or df.empty:
        logger.info("calculate_total_quantity: Empty DataFrame, returning 0")
        return 0

    # Check if column exists
    if qty_column not in df.columns:
        error_msg = (
            f"Column '{qty_column}' not found in DataFrame. "
            f"Available columns: {', '.join(df.columns)}"
        )
        logger.error(error_msg)
        raise KPIError(error_msg)

    try:
        total_qty = df[qty_column].sum()
        logger.debug(f"calculate_total_quantity: {total_qty:,} units from {len(df):,} rows")
        return int(total_qty)
    except Exception as e:
        error_msg = f"Error calculating total quantity: {e}"
        logger.error(error_msg)
        raise KPIError(error_msg)


def calculate_average_transaction_value(
    df: pd.DataFrame,
    qty_column: str = 'qty',
    amount_column: str = 'amount',
    total_amount_column: str = 'total_amount'
) -> float:
    """
    Calculate average transaction value (average revenue per transaction).

    This is computed as: Total Revenue / Number of Transactions

    Args:
        df (pd.DataFrame): Input DataFrame (can be filtered)
        qty_column (str): Name of quantity column. Defaults to 'qty'
        amount_column (str): Name of unit amount column. Defaults to 'amount'
        total_amount_column (str): Name of total amount column. Defaults to 'total_amount'

    Returns:
        float: Average transaction value. Returns 0.0 for empty DataFrame.

    Raises:
        KPIError: If required columns are missing from DataFrame

    Examples:
        >>> avg = calculate_average_transaction_value(df)
        >>> print(f"Avg Transaction: ${avg:,.2f}")
    """
    # Handle None or empty DataFrame
    if df is None or df.empty:
        logger.info("calculate_average_transaction_value: Empty DataFrame, returning 0.0")
        return 0.0

    try:
        # Calculate total revenue
        total_revenue = calculate_total_revenue(
            df,
            qty_column=qty_column,
            amount_column=amount_column,
            total_amount_column=total_amount_column
        )

        # Number of transactions
        num_transactions = len(df)

        if num_transactions == 0:
            return 0.0

        avg_value = total_revenue / num_transactions
        logger.debug(
            f"calculate_average_transaction_value: ${avg_value:,.2f} "
            f"({total_revenue:,.2f} / {num_transactions:,})"
        )
        return float(avg_value)

    except KPIError:
        raise
    except Exception as e:
        error_msg = f"Error calculating average transaction value: {e}"
        logger.error(error_msg)
        raise KPIError(error_msg)


def calculate_num_transactions(df: pd.DataFrame) -> int:
    """
    Calculate the number of transactions (row count).

    Args:
        df (pd.DataFrame): Input DataFrame (can be filtered)

    Returns:
        int: Number of transactions. Returns 0 for empty DataFrame.

    Examples:
        >>> count = calculate_num_transactions(df)
        >>> print(f"Transactions: {count:,}")
    """
    # Handle None or empty DataFrame
    if df is None or df.empty:
        logger.info("calculate_num_transactions: Empty DataFrame, returning 0")
        return 0

    count = len(df)
    logger.debug(f"calculate_num_transactions: {count:,} transactions")
    return count


def calculate_all_kpis(
    df: pd.DataFrame,
    qty_column: str = 'qty',
    amount_column: str = 'amount',
    total_amount_column: str = 'total_amount'
) -> dict:
    """
    Calculate all KPIs at once and return as a dictionary.

    This is a convenience function that computes all KPIs in a single call.
    More efficient than calling individual functions separately when you need
    all KPIs.

    Args:
        df (pd.DataFrame): Input DataFrame (can be filtered)
        qty_column (str): Name of quantity column. Defaults to 'qty'
        amount_column (str): Name of unit amount column. Defaults to 'amount'
        total_amount_column (str): Name of total amount column. Defaults to 'total_amount'

    Returns:
        dict: Dictionary containing all KPIs:
            - total_revenue (float)
            - total_quantity (int)
            - avg_transaction_value (float)
            - num_transactions (int)

    Raises:
        KPIError: If required columns are missing from DataFrame

    Examples:
        >>> kpis = calculate_all_kpis(df)
        >>> print(f"Revenue: ${kpis['total_revenue']:,.2f}")
        >>> print(f"Quantity: {kpis['total_quantity']:,}")
        >>> print(f"Avg Value: ${kpis['avg_transaction_value']:,.2f}")
        >>> print(f"Transactions: {kpis['num_transactions']:,}")
    """
    # Handle None or empty DataFrame
    if df is None or df.empty:
        logger.info("calculate_all_kpis: Empty DataFrame, returning zeros")
        return {
            'total_revenue': 0.0,
            'total_quantity': 0,
            'avg_transaction_value': 0.0,
            'num_transactions': 0
        }

    try:
        # Calculate all KPIs
        total_revenue = calculate_total_revenue(
            df,
            qty_column=qty_column,
            amount_column=amount_column,
            total_amount_column=total_amount_column
        )

        total_quantity = calculate_total_quantity(df, qty_column=qty_column)

        avg_transaction_value = calculate_average_transaction_value(
            df,
            qty_column=qty_column,
            amount_column=amount_column,
            total_amount_column=total_amount_column
        )

        num_transactions = calculate_num_transactions(df)

        kpis = {
            'total_revenue': total_revenue,
            'total_quantity': total_quantity,
            'avg_transaction_value': avg_transaction_value,
            'num_transactions': num_transactions
        }

        logger.info(
            f"calculate_all_kpis: Revenue=${kpis['total_revenue']:,.2f}, "
            f"Qty={kpis['total_quantity']:,}, "
            f"Avg=${kpis['avg_transaction_value']:,.2f}, "
            f"Count={kpis['num_transactions']:,}"
        )

        return kpis

    except KPIError:
        raise
    except Exception as e:
        error_msg = f"Error calculating KPIs: {e}"
        logger.error(error_msg)
        raise KPIError(error_msg)


def calculate_unique_customers(
    df: pd.DataFrame,
    email_column: str = 'email'
) -> int:
    """
    Calculate the number of unique customers.

    Bonus KPI: Count distinct customers based on email addresses.

    Args:
        df (pd.DataFrame): Input DataFrame (can be filtered)
        email_column (str): Name of email column. Defaults to 'email'

    Returns:
        int: Number of unique customers. Returns 0 for empty DataFrame.

    Raises:
        KPIError: If email column is missing from DataFrame

    Examples:
        >>> customers = calculate_unique_customers(df)
        >>> print(f"Unique Customers: {customers:,}")
    """
    # Handle None or empty DataFrame
    if df is None or df.empty:
        logger.info("calculate_unique_customers: Empty DataFrame, returning 0")
        return 0

    # Check if column exists
    if email_column not in df.columns:
        error_msg = (
            f"Column '{email_column}' not found in DataFrame. "
            f"Available columns: {', '.join(df.columns)}"
        )
        logger.error(error_msg)
        raise KPIError(error_msg)

    try:
        unique_count = df[email_column].nunique()
        logger.debug(f"calculate_unique_customers: {unique_count:,} unique customers")
        return int(unique_count)
    except Exception as e:
        error_msg = f"Error calculating unique customers: {e}"
        logger.error(error_msg)
        raise KPIError(error_msg)


def calculate_unique_products(
    df: pd.DataFrame,
    product_column: str = 'product_id'
) -> int:
    """
    Calculate the number of unique products.

    Bonus KPI: Count distinct products in the filtered dataset.

    Args:
        df (pd.DataFrame): Input DataFrame (can be filtered)
        product_column (str): Name of product column. Defaults to 'product_id'

    Returns:
        int: Number of unique products. Returns 0 for empty DataFrame.

    Raises:
        KPIError: If product column is missing from DataFrame

    Examples:
        >>> products = calculate_unique_products(df)
        >>> print(f"Unique Products: {products:,}")
    """
    # Handle None or empty DataFrame
    if df is None or df.empty:
        logger.info("calculate_unique_products: Empty DataFrame, returning 0")
        return 0

    # Check if column exists
    if product_column not in df.columns:
        error_msg = (
            f"Column '{product_column}' not found in DataFrame. "
            f"Available columns: {', '.join(df.columns)}"
        )
        logger.error(error_msg)
        raise KPIError(error_msg)

    try:
        unique_count = df[product_column].nunique()
        logger.debug(f"calculate_unique_products: {unique_count:,} unique products")
        return int(unique_count)
    except Exception as e:
        error_msg = f"Error calculating unique products: {e}"
        logger.error(error_msg)
        raise KPIError(error_msg)


def calculate_kpis_for_year(
    df: pd.DataFrame,
    year: int,
    year_column: str = 'invoice_year',
    qty_column: str = 'qty',
    amount_column: str = 'amount',
    total_amount_column: str = 'total_amount',
    email_column: str = 'email',
    product_column: str = 'product_id'
) -> dict:
    """
    Calculate all KPIs for a specific year.

    Args:
        df (pd.DataFrame): Input DataFrame with year column
        year (int): The year to calculate KPIs for
        year_column (str): Name of year column. Defaults to 'invoice_year'
        qty_column (str): Name of quantity column. Defaults to 'qty'
        amount_column (str): Name of unit amount column. Defaults to 'amount'
        total_amount_column (str): Name of total amount column. Defaults to 'total_amount'
        email_column (str): Name of email column. Defaults to 'email'
        product_column (str): Name of product column. Defaults to 'product_id'

    Returns:
        dict: Dictionary containing all KPIs for the specified year:
            - year (int): The year
            - total_revenue (float)
            - total_quantity (int)
            - avg_transaction_value (float)
            - num_transactions (int)
            - unique_customers (int)
            - unique_products (int)

    Raises:
        KPIError: If year column is missing or other errors occur

    Examples:
        >>> kpis_2022 = calculate_kpis_for_year(df, 2022)
        >>> print(f"2022 Revenue: ${kpis_2022['total_revenue']:,.2f}")
    """
    # Handle None or empty DataFrame
    if df is None or df.empty:
        logger.info(f"calculate_kpis_for_year: Empty DataFrame for year {year}")
        return {
            'year': year,
            'total_revenue': 0.0,
            'total_quantity': 0,
            'avg_transaction_value': 0.0,
            'num_transactions': 0,
            'unique_customers': 0,
            'unique_products': 0
        }

    # Check if year column exists
    if year_column not in df.columns:
        error_msg = (
            f"Column '{year_column}' not found in DataFrame. "
            f"Available columns: {', '.join(df.columns)}"
        )
        logger.error(error_msg)
        raise KPIError(error_msg)

    try:
        # Filter data for the specified year
        year_df = df[df[year_column] == year].copy()

        if year_df.empty:
            logger.info(f"calculate_kpis_for_year: No data found for year {year}")
            return {
                'year': year,
                'total_revenue': 0.0,
                'total_quantity': 0,
                'avg_transaction_value': 0.0,
                'num_transactions': 0,
                'unique_customers': 0,
                'unique_products': 0
            }

        # Calculate all KPIs for this year
        kpis = {
            'year': year,
            'total_revenue': calculate_total_revenue(
                year_df, qty_column, amount_column, total_amount_column
            ),
            'total_quantity': calculate_total_quantity(year_df, qty_column),
            'avg_transaction_value': calculate_average_transaction_value(
                year_df, qty_column, amount_column, total_amount_column
            ),
            'num_transactions': calculate_num_transactions(year_df),
            'unique_customers': calculate_unique_customers(year_df, email_column),
            'unique_products': calculate_unique_products(year_df, product_column)
        }

        logger.info(
            f"calculate_kpis_for_year {year}: Revenue=${kpis['total_revenue']:,.2f}, "
            f"Transactions={kpis['num_transactions']:,}"
        )

        return kpis

    except KPIError:
        raise
    except Exception as e:
        error_msg = f"Error calculating KPIs for year {year}: {e}"
        logger.error(error_msg)
        raise KPIError(error_msg)


def calculate_percentage_change(
    current_value: float,
    previous_value: float
) -> Optional[float]:
    """
    Calculate percentage change between current and previous values.

    Args:
        current_value (float): Current period value
        previous_value (float): Previous period value

    Returns:
        Optional[float]: Percentage change, or None if previous_value is 0

    Examples:
        >>> change = calculate_percentage_change(120, 100)
        >>> print(f"Change: {change:+.2f}%")  # Output: Change: +20.00%
    """
    if previous_value == 0:
        logger.debug("calculate_percentage_change: Previous value is 0, returning None")
        return None

    pct_change = ((current_value - previous_value) / previous_value) * 100
    return float(pct_change)


def calculate_kpis_with_yoy_comparison(
    df: pd.DataFrame,
    current_year: int,
    year_column: str = 'invoice_year',
    qty_column: str = 'qty',
    amount_column: str = 'amount',
    total_amount_column: str = 'total_amount',
    email_column: str = 'email',
    product_column: str = 'product_id'
) -> dict:
    """
    Calculate KPIs with year-over-year (YoY) comparison.

    This function computes all KPIs for the current year and compares them
    with the previous year, calculating percentage changes for each metric.

    Args:
        df (pd.DataFrame): Input DataFrame with year column
        current_year (int): The current year to analyze
        year_column (str): Name of year column. Defaults to 'invoice_year'
        qty_column (str): Name of quantity column. Defaults to 'qty'
        amount_column (str): Name of unit amount column. Defaults to 'amount'
        total_amount_column (str): Name of total amount column. Defaults to 'total_amount'
        email_column (str): Name of email column. Defaults to 'email'
        product_column (str): Name of product column. Defaults to 'product_id'

    Returns:
        dict: Dictionary containing:
            - current (dict): All KPIs for current year
            - previous (dict): All KPIs for previous year (or None if unavailable)
            - comparison (dict): Percentage changes for each KPI (or None if unavailable)
                - total_revenue_change (float or None)
                - total_quantity_change (float or None)
                - avg_transaction_value_change (float or None)
                - num_transactions_change (float or None)
                - unique_customers_change (float or None)
                - unique_products_change (float or None)

    Examples:
        >>> result = calculate_kpis_with_yoy_comparison(df, 2022)
        >>> print(f"2022 Revenue: ${result['current']['total_revenue']:,.2f}")
        >>> if result['comparison']['total_revenue_change'] is not None:
        ...     print(f"YoY Change: {result['comparison']['total_revenue_change']:+.2f}%")
    """
    # Handle None or empty DataFrame
    if df is None or df.empty:
        logger.warning(f"calculate_kpis_with_yoy_comparison: Empty DataFrame")
        return {
            'current': {
                'year': current_year,
                'total_revenue': 0.0,
                'total_quantity': 0,
                'avg_transaction_value': 0.0,
                'num_transactions': 0,
                'unique_customers': 0,
                'unique_products': 0
            },
            'previous': None,
            'comparison': {
                'total_revenue_change': None,
                'total_quantity_change': None,
                'avg_transaction_value_change': None,
                'num_transactions_change': None,
                'unique_customers_change': None,
                'unique_products_change': None
            }
        }

    try:
        # Calculate KPIs for current year
        current_kpis = calculate_kpis_for_year(
            df, current_year, year_column, qty_column, amount_column,
            total_amount_column, email_column, product_column
        )

        # Calculate KPIs for previous year
        previous_year = current_year - 1
        previous_kpis = calculate_kpis_for_year(
            df, previous_year, year_column, qty_column, amount_column,
            total_amount_column, email_column, product_column
        )

        # Check if previous year has data
        has_previous_data = previous_kpis['num_transactions'] > 0

        if not has_previous_data:
            logger.info(
                f"calculate_kpis_with_yoy_comparison: No data for previous year {previous_year}"
            )
            return {
                'current': current_kpis,
                'previous': None,
                'comparison': {
                    'total_revenue_change': None,
                    'total_quantity_change': None,
                    'avg_transaction_value_change': None,
                    'num_transactions_change': None,
                    'unique_customers_change': None,
                    'unique_products_change': None
                }
            }

        # Calculate percentage changes
        comparison = {
            'total_revenue_change': calculate_percentage_change(
                current_kpis['total_revenue'],
                previous_kpis['total_revenue']
            ),
            'total_quantity_change': calculate_percentage_change(
                current_kpis['total_quantity'],
                previous_kpis['total_quantity']
            ),
            'avg_transaction_value_change': calculate_percentage_change(
                current_kpis['avg_transaction_value'],
                previous_kpis['avg_transaction_value']
            ),
            'num_transactions_change': calculate_percentage_change(
                current_kpis['num_transactions'],
                previous_kpis['num_transactions']
            ),
            'unique_customers_change': calculate_percentage_change(
                current_kpis['unique_customers'],
                previous_kpis['unique_customers']
            ),
            'unique_products_change': calculate_percentage_change(
                current_kpis['unique_products'],
                previous_kpis['unique_products']
            )
        }

        logger.info(
            f"calculate_kpis_with_yoy_comparison: {current_year} vs {previous_year} - "
            f"Revenue change: {comparison['total_revenue_change']:+.2f}% "
            if comparison['total_revenue_change'] is not None else "N/A"
        )

        return {
            'current': current_kpis,
            'previous': previous_kpis,
            'comparison': comparison
        }

    except KPIError:
        raise
    except Exception as e:
        error_msg = f"Error calculating YoY comparison for year {current_year}: {e}"
        logger.error(error_msg)
        raise KPIError(error_msg)


def get_available_years(
    df: pd.DataFrame,
    year_column: str = 'invoice_year'
) -> list:
    """
    Get sorted list of available years in the dataset.

    Args:
        df (pd.DataFrame): Input DataFrame with year column
        year_column (str): Name of year column. Defaults to 'invoice_year'

    Returns:
        list: Sorted list of years (ascending order). Empty list if no data.

    Raises:
        KPIError: If year column is missing from DataFrame

    Examples:
        >>> years = get_available_years(df)
        >>> print(f"Available years: {years}")  # [1970, 1971, ..., 2022]
    """
    # Handle None or empty DataFrame
    if df is None or df.empty:
        logger.info("get_available_years: Empty DataFrame, returning empty list")
        return []

    # Check if year column exists
    if year_column not in df.columns:
        error_msg = (
            f"Column '{year_column}' not found in DataFrame. "
            f"Available columns: {', '.join(df.columns)}"
        )
        logger.error(error_msg)
        raise KPIError(error_msg)

    try:
        years = sorted(df[year_column].unique().tolist())
        logger.debug(f"get_available_years: Found {len(years)} years")
        return years
    except Exception as e:
        error_msg = f"Error getting available years: {e}"
        logger.error(error_msg)
        raise KPIError(error_msg)
