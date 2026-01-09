"""
Data Transformer Module

This module handles all data transformations and derived field calculations.
Responsible for:
- Creating derived fields (total_amount, full_name, invoice_year)
- Aggregations for visualizations
- Filtering operations
"""

import pandas as pd
import numpy as np
from typing import List, Optional


class DataTransformer:
    """
    Handles all data transformation and aggregation operations.

    This class takes raw invoice data and transforms it into
    formats suitable for visualization and analysis.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize DataTransformer with a dataframe.

        Args:
            df (pd.DataFrame): Raw invoice data with invoice_date as datetime
        """
        self.df = df.copy()
        self._add_derived_fields()

    def _add_derived_fields(self) -> None:
        """
        Add derived fields to the dataframe.

        Derived fields:
        - full_name: Concatenation of first_name and last_name
        - total_amount: qty * amount (total revenue per transaction)
        - invoice_year: Year extracted from invoice_date
        - invoice_month: Month extracted from invoice_date
        - invoice_day: Day extracted from invoice_date

        Note: Only adds fields if they don't already exist to avoid
        redundant recalculation when filtering creates new instances.
        """
        # Customer full name
        if 'full_name' not in self.df.columns:
            self.df['full_name'] = (
                self.df['first_name'] + ' ' + self.df['last_name']
            )

        # Total transaction amount
        if 'total_amount' not in self.df.columns:
            self.df['total_amount'] = self.df['qty'] * self.df['amount']

        # Date components
        if 'invoice_year' not in self.df.columns:
            self.df['invoice_year'] = self.df['invoice_date'].dt.year
        if 'invoice_month' not in self.df.columns:
            self.df['invoice_month'] = self.df['invoice_date'].dt.month
        if 'invoice_day' not in self.df.columns:
            self.df['invoice_day'] = self.df['invoice_date'].dt.day

    def filter_by_years(self, years: List[int]) -> 'DataTransformer':
        """
        Filter data by selected years.

        Args:
            years (List[int]): List of years to include

        Returns:
            DataTransformer: New instance with filtered data
        """
        filtered_df = self.df[self.df['invoice_year'].isin(years)]
        return DataTransformer(filtered_df)

    def filter_by_products(self, product_ids: List[int]) -> 'DataTransformer':
        """
        Filter data by selected product IDs.

        Args:
            product_ids (List[int]): List of product IDs to include

        Returns:
            DataTransformer: New instance with filtered data
        """
        filtered_df = self.df[self.df['product_id'].isin(product_ids)]
        return DataTransformer(filtered_df)

    def get_kpis(self) -> dict:
        """
        Calculate key performance indicators.

        Returns:
            dict: Dictionary containing all KPIs
        """
        return {
            'total_revenue': self.df['total_amount'].sum(),
            'total_quantity': self.df['qty'].sum(),
            'num_transactions': len(self.df),
            'avg_transaction_value': self.df['total_amount'].mean(),
            'unique_customers': self.df['email'].nunique(),
            'unique_products': self.df['product_id'].nunique()
        }

    def get_yearly_revenue(self) -> pd.DataFrame:
        """
        Aggregate revenue by year.

        Returns:
            pd.DataFrame: Yearly revenue with columns [invoice_year, total_revenue]
        """
        yearly = self.df.groupby('invoice_year').agg({
            'total_amount': 'sum'
        }).reset_index()
        yearly.columns = ['invoice_year', 'total_revenue']
        return yearly.sort_values('invoice_year')

    def get_yearly_quantity(self) -> pd.DataFrame:
        """
        Aggregate quantity sold by year.

        Returns:
            pd.DataFrame: Yearly quantity with columns [invoice_year, total_quantity]
        """
        yearly = self.df.groupby('invoice_year').agg({
            'qty': 'sum'
        }).reset_index()
        yearly.columns = ['invoice_year', 'total_quantity']
        return yearly.sort_values('invoice_year')

    def get_top_products(self, n: int = 10) -> pd.DataFrame:
        """
        Get top N products by revenue.

        Args:
            n (int): Number of top products to return

        Returns:
            pd.DataFrame: Top products with columns [product_id, total_revenue]
        """
        top_products = self.df.groupby('product_id').agg({
            'total_amount': 'sum'
        }).reset_index()
        top_products.columns = ['product_id', 'total_revenue']
        return top_products.nlargest(n, 'total_revenue')

    def get_top_products_for_filter(self, n: int = 15) -> List[int]:
        """
        Get top N product IDs by total revenue for filter button display.

        This method is used to limit the number of product buttons shown
        in the filter bar, displaying only the top-selling products.

        Args:
            n (int): Number of top products to return (default: 15)

        Returns:
            List[int]: Sorted list of product IDs ordered by revenue (highest first)
        """
        top = self.get_top_products(n)
        return top['product_id'].tolist()

    def get_product_year_heatmap_data(self) -> pd.DataFrame:
        """
        Get product-year revenue data for heatmap visualization.

        Returns:
            pd.DataFrame: Pivot table with products as index (Y-axis),
                         years as columns (X-axis)
        """
        heatmap_data = self.df.pivot_table(
            index='product_id',           # Y-axis: Products
            columns='invoice_year',       # X-axis: Years
            values='total_amount',        # Color: Revenue
            aggfunc='sum',
            fill_value=0
        )
        return heatmap_data

    def get_daily_transactions(self) -> pd.DataFrame:
        """
        Get daily transaction counts.

        Returns:
            pd.DataFrame: Daily transactions with columns [invoice_date, num_transactions]
        """
        daily = self.df.groupby('invoice_date').agg({
            'product_id': 'count'
        }).reset_index()
        daily.columns = ['invoice_date', 'num_transactions']
        return daily.sort_values('invoice_date')

    def get_transaction_volume(self, freq: str = 'D') -> pd.DataFrame:
        """
        Get transaction volume with continuous date range and configurable aggregation.

        This method provides time-series transaction volume data with automatic
        gap-filling for missing dates, supporting multiple aggregation levels.

        Args:
            freq (str): Resampling frequency (default: 'D')
                - 'D': Daily (every calendar day)
                - 'W': Weekly (Sunday to Saturday)
                - 'M': Monthly (end of month)

        Returns:
            pd.DataFrame: Continuous transaction volume with columns [date, volume]
                - date: Datetime index at specified frequency
                - volume: Integer count of transactions (zeros for missing dates)

        Raises:
            ValueError: If freq is not 'D', 'W', or 'M', or if data is empty
        """
        # Handle empty dataframe
        if self.df.empty:
            return pd.DataFrame(columns=['date', 'volume'])

        # Validate invoice_date column exists
        if 'invoice_date' not in self.df.columns:
            raise ValueError("invoice_date column not found in dataframe")

        # Ensure we have a datetime index
        df_temp = self.df.copy()
        df_temp = df_temp.set_index('invoice_date')

        # Count transactions per original date
        daily_counts = df_temp.resample('D').size()

        # Resample to requested frequency
        if freq == 'D':
            # Already daily, just ensure continuous range
            result = daily_counts
        elif freq == 'W':
            # Weekly aggregation (Sunday start)
            result = daily_counts.resample('W-SUN').sum()
        elif freq == 'M':
            # Monthly aggregation (end of month)
            # Use 'M' for pandas <2.0 compatibility, pandas will handle it
            try:
                result = daily_counts.resample('ME').sum()
            except ValueError:
                # Fallback for older pandas versions
                result = daily_counts.resample('M').sum()
        else:
            raise ValueError(f"Invalid frequency: {freq}. Use 'D', 'W', or 'M'.")

        # Convert to DataFrame
        result_df = result.reset_index()
        result_df.columns = ['date', 'volume']

        # Fill any remaining NaN values with 0
        result_df['volume'] = result_df['volume'].fillna(0).astype(int)

        return result_df

    def get_product_performance(self, product_id: int) -> pd.DataFrame:
        """
        Get yearly performance for a specific product.

        Args:
            product_id (int): Product ID to analyze

        Returns:
            pd.DataFrame: Product performance by year
        """
        product_data = self.df[self.df['product_id'] == product_id]

        performance = product_data.groupby('invoice_year').agg({
            'total_amount': 'sum',
            'qty': 'sum'
        }).reset_index()

        performance.columns = ['invoice_year', 'revenue', 'quantity']
        return performance.sort_values('invoice_year')

    def get_multi_product_performance(self, product_ids: List[int] = None) -> pd.DataFrame:
        """
        Get yearly revenue performance for multiple products.

        This method enables product comparison by returning revenue data
        for each product separately, suitable for multi-trace line charts.

        Args:
            product_ids (List[int], optional): List of product IDs to include.
                If None, uses all products in current filtered data.

        Returns:
            pd.DataFrame: Multi-product performance with columns:
                - invoice_year: Year
                - product_id: Product identifier
                - revenue: Total revenue for that product in that year
        """
        # Use all products in filtered data if not specified
        if product_ids is None:
            product_ids = self.df['product_id'].unique().tolist()

        # Filter to requested products only
        filtered_df = self.df[self.df['product_id'].isin(product_ids)]

        # Group by year and product
        performance = filtered_df.groupby(['invoice_year', 'product_id']).agg({
            'total_amount': 'sum'
        }).reset_index()

        performance.columns = ['invoice_year', 'product_id', 'revenue']

        return performance.sort_values(['invoice_year', 'product_id'])

    def get_available_years(self) -> List[int]:
        """
        Get list of all available years in the dataset.

        Returns:
            List[int]: Sorted list of years
        """
        return sorted(self.df['invoice_year'].unique().tolist())

    def get_available_products(self) -> List[int]:
        """
        Get list of all available product IDs in the dataset.

        Returns:
            List[int]: Sorted list of product IDs
        """
        return sorted(self.df['product_id'].unique().tolist())
