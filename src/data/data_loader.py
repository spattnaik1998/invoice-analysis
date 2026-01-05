"""
Data Loader Module

This module handles loading invoice data from CSV files.
Responsible for:
- Reading CSV data
- Initial data validation
- Data type conversions
"""

import pandas as pd
import os
from typing import Optional
from pathlib import Path


class DataLoader:
    """
    Handles loading and initial validation of invoice data.

    Attributes:
        data_path (str): Path to the CSV data file
        df (pd.DataFrame): Loaded dataframe
    """

    def __init__(self, data_path: str = "data/invoices.csv"):
        """
        Initialize DataLoader with path to data file.

        Args:
            data_path (str): Path to the invoices CSV file
        """
        self.data_path = data_path
        self.df: Optional[pd.DataFrame] = None

    def load_data(self) -> pd.DataFrame:
        """
        Load invoice data from CSV file.

        Returns:
            pd.DataFrame: Raw invoice data

        Raises:
            FileNotFoundError: If CSV file doesn't exist
            pd.errors.EmptyDataError: If CSV file is empty
        """
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Data file not found at: {self.data_path}")

        try:
            # Load CSV data
            self.df = pd.read_csv(self.data_path)

            # Validate required columns
            self._validate_schema()

            # Convert date column to datetime
            self.df['invoice_date'] = pd.to_datetime(
                self.df['invoice_date'],
                format='%d/%m/%Y'
            )

            return self.df

        except pd.errors.EmptyDataError:
            raise pd.errors.EmptyDataError("CSV file is empty")
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")

    def _validate_schema(self) -> None:
        """
        Validate that all required columns exist in the dataset.

        Raises:
            ValueError: If required columns are missing
        """
        required_columns = [
            'first_name', 'last_name', 'email', 'product_id',
            'qty', 'amount', 'invoice_date', 'address',
            'city', 'stock_code', 'job'
        ]

        missing_columns = set(required_columns) - set(self.df.columns)

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {', '.join(missing_columns)}"
            )

    def get_data_info(self) -> dict:
        """
        Get basic information about the loaded dataset.

        Returns:
            dict: Dataset statistics including shape, date range, etc.
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        return {
            'total_records': len(self.df),
            'total_columns': len(self.df.columns),
            'date_range': {
                'start': self.df['invoice_date'].min(),
                'end': self.df['invoice_date'].max()
            },
            'unique_products': self.df['product_id'].nunique(),
            'unique_customers': self.df['email'].nunique(),
            'missing_values': self.df.isnull().sum().to_dict()
        }
