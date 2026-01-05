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
