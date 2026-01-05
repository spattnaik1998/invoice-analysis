"""
Filtering Functions Module

This module provides reusable filtering functions for invoice data.
Designed to be used by KPIs, charts, and other data consumers.

All functions handle edge cases gracefully and return clean DataFrames.
"""

import pandas as pd
import logging
from typing import List, Optional, Union

logger = logging.getLogger(__name__)


class FilterError(Exception):
    """Custom exception for filtering errors."""
    pass


def filter_by_years(
    df: pd.DataFrame,
    years: Union[List[int], range, None],
    year_column: str = 'invoice_year'
) -> pd.DataFrame:
    """
    Filter DataFrame by specified years.

    This is a reusable filtering function designed to handle various
    edge cases gracefully. It can be used by KPIs, charts, and any
    other component that needs year-based filtering.

    Args:
        df (pd.DataFrame): Input DataFrame to filter
        years (Union[List[int], range, None]): Years to include. Can be:
            - List of years: [2020, 2021, 2022]
            - Range object: range(2020, 2023)
            - None: Returns all data (no filtering)
            - Empty list: Returns empty DataFrame with same schema
        year_column (str): Name of the year column. Defaults to 'invoice_year'

    Returns:
        pd.DataFrame: Filtered DataFrame containing only specified years

    Raises:
        FilterError: If year_column doesn't exist in DataFrame
        ValueError: If invalid year values are provided

    Examples:
        >>> # Filter by specific years
        >>> filtered = filter_by_years(df, [2020, 2021])

        >>> # Filter by year range
        >>> filtered = filter_by_years(df, range(2020, 2023))

        >>> # No filtering (return all data)
        >>> all_data = filter_by_years(df, None)

        >>> # Empty selection (return empty DataFrame)
        >>> empty = filter_by_years(df, [])
    """
    # Validate inputs
    if df is None or df.empty:
        logger.warning("filter_by_years: Input DataFrame is empty or None")
        return df if df is not None else pd.DataFrame()

    # Check if year column exists
    if year_column not in df.columns:
        error_msg = (
            f"Column '{year_column}' not found in DataFrame. "
            f"Available columns: {', '.join(df.columns)}"
        )
        logger.error(error_msg)
        raise FilterError(error_msg)

    # Handle None (no filtering)
    if years is None:
        logger.info("filter_by_years: No year filter applied (years=None)")
        return df.copy()

    # Convert range to list
    if isinstance(years, range):
        years = list(years)
        logger.debug(f"filter_by_years: Converted range to list: {years}")

    # Handle empty list (return empty DataFrame with same schema)
    if not years:
        logger.info("filter_by_years: Empty year list, returning empty DataFrame")
        return df.iloc[0:0].copy()  # Empty DataFrame with same columns

    # Validate year values
    if not all(isinstance(year, int) for year in years):
        error_msg = "All year values must be integers"
        logger.error(f"filter_by_years: {error_msg}")
        raise ValueError(error_msg)

    # Check for invalid years (negative or unrealistic)
    invalid_years = [y for y in years if y < 1900 or y > 2100]
    if invalid_years:
        logger.warning(
            f"filter_by_years: Potentially invalid years detected: {invalid_years}"
        )

    # Get available years in the dataset
    available_years = df[year_column].unique()

    # Check if any requested years exist in the data
    requested_years_set = set(years)
    available_years_set = set(available_years)
    matching_years = requested_years_set & available_years_set
    missing_years = requested_years_set - available_years_set

    if missing_years:
        logger.warning(
            f"filter_by_years: {len(missing_years)} requested years not found in data: "
            f"{sorted(missing_years)}"
        )

    if not matching_years:
        logger.warning(
            f"filter_by_years: None of the requested years exist in the dataset. "
            f"Requested: {sorted(years)}, Available: {sorted(available_years)}"
        )
        return df.iloc[0:0].copy()  # Empty DataFrame with same columns

    # Perform filtering
    filtered_df = df[df[year_column].isin(years)].copy()

    logger.info(
        f"filter_by_years: Filtered {len(df):,} -> {len(filtered_df):,} rows "
        f"({len(matching_years)} years: {sorted(matching_years)})"
    )

    return filtered_df


def filter_by_products(
    df: pd.DataFrame,
    product_ids: Union[List[int], None],
    product_column: str = 'product_id'
) -> pd.DataFrame:
    """
    Filter DataFrame by specified product IDs.

    Reusable filtering function with graceful edge case handling.

    Args:
        df (pd.DataFrame): Input DataFrame to filter
        product_ids (Union[List[int], None]): Product IDs to include
            - List of IDs: [100, 101, 102]
            - None: Returns all data (no filtering)
            - Empty list: Returns empty DataFrame with same schema
        product_column (str): Name of product ID column. Defaults to 'product_id'

    Returns:
        pd.DataFrame: Filtered DataFrame containing only specified products

    Raises:
        FilterError: If product_column doesn't exist in DataFrame
        ValueError: If invalid product ID values are provided
    """
    # Validate inputs
    if df is None or df.empty:
        logger.warning("filter_by_products: Input DataFrame is empty or None")
        return df if df is not None else pd.DataFrame()

    # Check if product column exists
    if product_column not in df.columns:
        error_msg = (
            f"Column '{product_column}' not found in DataFrame. "
            f"Available columns: {', '.join(df.columns)}"
        )
        logger.error(error_msg)
        raise FilterError(error_msg)

    # Handle None (no filtering)
    if product_ids is None:
        logger.info("filter_by_products: No product filter applied (product_ids=None)")
        return df.copy()

    # Handle empty list
    if not product_ids:
        logger.info("filter_by_products: Empty product list, returning empty DataFrame")
        return df.iloc[0:0].copy()

    # Validate product ID values
    if not all(isinstance(pid, int) for pid in product_ids):
        error_msg = "All product IDs must be integers"
        logger.error(f"filter_by_products: {error_msg}")
        raise ValueError(error_msg)

    # Get available products
    available_products = df[product_column].unique()
    requested_products_set = set(product_ids)
    available_products_set = set(available_products)
    matching_products = requested_products_set & available_products_set
    missing_products = requested_products_set - available_products_set

    if missing_products:
        logger.warning(
            f"filter_by_products: {len(missing_products)} requested products not found: "
            f"{sorted(missing_products)}"
        )

    if not matching_products:
        logger.warning(
            f"filter_by_products: None of the requested products exist in the dataset"
        )
        return df.iloc[0:0].copy()

    # Perform filtering
    filtered_df = df[df[product_column].isin(product_ids)].copy()

    logger.info(
        f"filter_by_products: Filtered {len(df):,} -> {len(filtered_df):,} rows "
        f"({len(matching_products)} products)"
    )

    return filtered_df


def filter_by_date_range(
    df: pd.DataFrame,
    start_date: Optional[pd.Timestamp] = None,
    end_date: Optional[pd.Timestamp] = None,
    date_column: str = 'invoice_date'
) -> pd.DataFrame:
    """
    Filter DataFrame by date range.

    Reusable filtering function for date-based filtering.

    Args:
        df (pd.DataFrame): Input DataFrame to filter
        start_date (Optional[pd.Timestamp]): Start date (inclusive)
            - None: No lower bound
        end_date (Optional[pd.Timestamp]): End date (inclusive)
            - None: No upper bound
        date_column (str): Name of date column. Defaults to 'invoice_date'

    Returns:
        pd.DataFrame: Filtered DataFrame within date range

    Raises:
        FilterError: If date_column doesn't exist in DataFrame
        ValueError: If start_date > end_date
    """
    # Validate inputs
    if df is None or df.empty:
        logger.warning("filter_by_date_range: Input DataFrame is empty or None")
        return df if df is not None else pd.DataFrame()

    # Check if date column exists
    if date_column not in df.columns:
        error_msg = (
            f"Column '{date_column}' not found in DataFrame. "
            f"Available columns: {', '.join(df.columns)}"
        )
        logger.error(error_msg)
        raise FilterError(error_msg)

    # Handle no filtering
    if start_date is None and end_date is None:
        logger.info("filter_by_date_range: No date filter applied")
        return df.copy()

    # Validate date range
    if start_date is not None and end_date is not None:
        if start_date > end_date:
            error_msg = f"start_date ({start_date}) cannot be after end_date ({end_date})"
            logger.error(f"filter_by_date_range: {error_msg}")
            raise ValueError(error_msg)

    # Build filter condition
    filtered_df = df.copy()

    if start_date is not None:
        filtered_df = filtered_df[filtered_df[date_column] >= start_date]

    if end_date is not None:
        filtered_df = filtered_df[filtered_df[date_column] <= end_date]

    logger.info(
        f"filter_by_date_range: Filtered {len(df):,} -> {len(filtered_df):,} rows "
        f"(from {start_date} to {end_date})"
    )

    return filtered_df


def apply_combined_filters(
    df: pd.DataFrame,
    years: Union[List[int], range, None] = None,
    product_ids: Union[List[int], None] = None,
    start_date: Optional[pd.Timestamp] = None,
    end_date: Optional[pd.Timestamp] = None
) -> pd.DataFrame:
    """
    Apply multiple filters in sequence.

    Convenience function that applies year, product, and date filters
    in a single call. Filters are applied in order: years -> products -> dates.

    Args:
        df (pd.DataFrame): Input DataFrame to filter
        years (Union[List[int], range, None]): Years to include
        product_ids (Union[List[int], None]): Product IDs to include
        start_date (Optional[pd.Timestamp]): Start date (inclusive)
        end_date (Optional[pd.Timestamp]): End date (inclusive)

    Returns:
        pd.DataFrame: Filtered DataFrame with all filters applied

    Examples:
        >>> # Apply multiple filters
        >>> filtered = apply_combined_filters(
        ...     df,
        ...     years=[2020, 2021],
        ...     product_ids=[100, 101, 102]
        ... )

        >>> # Apply only year filter
        >>> filtered = apply_combined_filters(df, years=range(2020, 2023))
    """
    result = df.copy()

    # Apply year filter
    if years is not None:
        result = filter_by_years(result, years)

    # Apply product filter
    if product_ids is not None:
        result = filter_by_products(result, product_ids)

    # Apply date range filter
    if start_date is not None or end_date is not None:
        result = filter_by_date_range(result, start_date, end_date)

    logger.info(
        f"apply_combined_filters: Total filtering {len(df):,} -> {len(result):,} rows"
    )

    return result
