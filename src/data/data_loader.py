"""
Data Loader Module

This module handles loading invoice data from CSV files.
Responsible for:
- Reading CSV data
- Initial data validation
- Data type conversions
- Logging dataset statistics
"""

import pandas as pd
import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataValidationError(Exception):
    """Custom exception for data validation errors."""
    pass


class DataLoader:
    """
    Handles loading and initial validation of invoice data.

    This class provides robust CSV ingestion with comprehensive validation,
    error handling, and logging capabilities.

    Attributes:
        data_path (str): Path to the CSV data file
        df (pd.DataFrame): Loaded and validated dataframe
    """

    # Required columns for invoice data
    REQUIRED_COLUMNS = [
        'first_name',
        'last_name',
        'email',
        'product_id',
        'qty',
        'amount',
        'invoice_date'
    ]

    # Optional columns that may be present
    OPTIONAL_COLUMNS = [
        'address',
        'city',
        'stock_code',
        'job'
    ]

    def __init__(self, data_path: str = "data/invoices.csv"):
        """
        Initialize DataLoader with path to data file.

        Args:
            data_path (str): Path to the invoices CSV file
        """
        self.data_path = data_path
        self.df: Optional[pd.DataFrame] = None
        logger.info(f"DataLoader initialized with path: {data_path}")

    def load_data(self) -> pd.DataFrame:
        """
        Load and validate invoice data from CSV file.

        This method performs the following operations:
        1. Verify file exists
        2. Load CSV data
        3. Validate schema (required columns)
        4. Validate data types
        5. Validate data quality (nulls, ranges, formats)
        6. Convert date formats
        7. Log dataset statistics

        Returns:
            pd.DataFrame: Clean, validated invoice data

        Raises:
            FileNotFoundError: If CSV file doesn't exist
            pd.errors.EmptyDataError: If CSV file is empty
            DataValidationError: If data validation fails
        """
        logger.info("=" * 60)
        logger.info("Starting CSV ingestion process")
        logger.info("=" * 60)

        # Step 1: Verify file exists
        self._verify_file_exists()

        # Step 2: Load CSV data
        self._load_csv()

        # Step 3: Validate schema
        self._validate_schema()

        # Step 4: Validate data types
        self._validate_data_types()

        # Step 5: Validate data quality
        self._validate_data_quality()

        # Step 6: Convert and validate dates
        self._convert_dates()

        # Step 7: Log dataset statistics
        self._log_dataset_stats()

        logger.info("=" * 60)
        logger.info("CSV ingestion completed successfully")
        logger.info("=" * 60)

        return self.df

    def _verify_file_exists(self) -> None:
        """
        Verify that the CSV file exists at the specified path.

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not os.path.exists(self.data_path):
            error_msg = (
                f"Data file not found at: {self.data_path}\n"
                f"Please ensure the CSV file exists at this location."
            )
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        file_size = os.path.getsize(self.data_path)
        logger.info(f"File found: {self.data_path} ({file_size:,} bytes)")

    def _load_csv(self) -> None:
        """
        Load CSV data into a pandas DataFrame.

        Raises:
            pd.errors.EmptyDataError: If CSV file is empty
            pd.errors.ParserError: If CSV parsing fails
        """
        try:
            logger.info("Reading CSV file...")
            self.df = pd.read_csv(self.data_path)

            if self.df.empty:
                raise pd.errors.EmptyDataError("CSV file contains no data rows")

            logger.info(f"CSV loaded successfully: {len(self.df):,} rows, {len(self.df.columns)} columns")

        except pd.errors.EmptyDataError as e:
            logger.error(f"Empty CSV file: {str(e)}")
            raise

        except pd.errors.ParserError as e:
            error_msg = f"CSV parsing error: {str(e)}\nPlease check the file format."
            logger.error(error_msg)
            raise pd.errors.ParserError(error_msg)

        except Exception as e:
            error_msg = f"Unexpected error loading CSV: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def _validate_schema(self) -> None:
        """
        Validate that all required columns exist in the dataset.

        Raises:
            DataValidationError: If required columns are missing
        """
        logger.info("Validating schema...")

        missing_columns = set(self.REQUIRED_COLUMNS) - set(self.df.columns)

        if missing_columns:
            error_msg = (
                f"Schema validation failed!\n"
                f"Missing required columns: {', '.join(sorted(missing_columns))}\n"
                f"Required columns: {', '.join(self.REQUIRED_COLUMNS)}\n"
                f"Found columns: {', '.join(self.df.columns)}"
            )
            logger.error(error_msg)
            raise DataValidationError(error_msg)

        logger.info(f"Schema validation passed: All {len(self.REQUIRED_COLUMNS)} required columns present")

    def _validate_data_types(self) -> None:
        """
        Validate data types for critical columns.

        Raises:
            DataValidationError: If data types are invalid
        """
        logger.info("Validating data types...")

        errors = []

        # Validate numeric columns
        for col in ['product_id', 'qty', 'amount']:
            if col in self.df.columns:
                non_numeric = pd.to_numeric(self.df[col], errors='coerce').isna().sum()
                if non_numeric > 0:
                    errors.append(
                        f"Column '{col}': {non_numeric} non-numeric values found"
                    )

        # Validate email format (basic check)
        if 'email' in self.df.columns:
            invalid_emails = ~self.df['email'].astype(str).str.contains('@', na=False)
            if invalid_emails.sum() > 0:
                errors.append(
                    f"Column 'email': {invalid_emails.sum()} invalid email addresses (missing '@')"
                )

        if errors:
            error_msg = "Data type validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            logger.error(error_msg)
            raise DataValidationError(error_msg)

        logger.info("Data type validation passed")

    def _validate_data_quality(self) -> None:
        """
        Validate data quality (missing values, ranges, business rules).

        Raises:
            DataValidationError: If critical data quality issues are found
        """
        logger.info("Validating data quality...")

        warnings = []
        errors = []

        # Check for missing values in required columns
        for col in self.REQUIRED_COLUMNS:
            null_count = self.df[col].isnull().sum()
            if null_count > 0:
                errors.append(
                    f"Column '{col}': {null_count} missing values ({null_count/len(self.df)*100:.2f}%)"
                )

        # Validate business rules
        if 'qty' in self.df.columns:
            invalid_qty = (pd.to_numeric(self.df['qty'], errors='coerce') <= 0).sum()
            if invalid_qty > 0:
                errors.append(
                    f"Column 'qty': {invalid_qty} records with quantity <= 0"
                )

        if 'amount' in self.df.columns:
            invalid_amount = (pd.to_numeric(self.df['amount'], errors='coerce') <= 0).sum()
            if invalid_amount > 0:
                errors.append(
                    f"Column 'amount': {invalid_amount} records with amount <= 0"
                )

        # Check for duplicate rows
        duplicate_count = self.df.duplicated().sum()
        if duplicate_count > 0:
            warnings.append(
                f"Found {duplicate_count} duplicate rows ({duplicate_count/len(self.df)*100:.2f}%)"
            )

        # Log warnings
        if warnings:
            logger.warning("Data quality warnings:")
            for warning in warnings:
                logger.warning(f"  - {warning}")

        # Raise errors if critical issues found
        if errors:
            error_msg = "Data quality validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            logger.error(error_msg)
            raise DataValidationError(error_msg)

        logger.info("Data quality validation passed")

    def _convert_dates(self) -> None:
        """
        Convert invoice_date to datetime format and validate date ranges.

        Raises:
            DataValidationError: If date conversion fails
        """
        logger.info("Converting date columns...")

        try:
            # Convert to datetime with error handling
            self.df['invoice_date'] = pd.to_datetime(
                self.df['invoice_date'],
                format='%d/%m/%Y',
                errors='coerce'
            )

            # Check for failed conversions
            invalid_dates = self.df['invoice_date'].isnull().sum()
            if invalid_dates > 0:
                error_msg = (
                    f"Date conversion failed for {invalid_dates} records\n"
                    f"Expected format: DD/MM/YYYY (e.g., 31/12/2022)"
                )
                logger.error(error_msg)
                raise DataValidationError(error_msg)

            # Validate date range (future dates check)
            future_dates = (self.df['invoice_date'] > pd.Timestamp.now()).sum()
            if future_dates > 0:
                logger.warning(f"Found {future_dates} records with future dates")

            logger.info("Date conversion completed successfully")

        except DataValidationError:
            raise
        except Exception as e:
            error_msg = f"Date conversion error: {str(e)}"
            logger.error(error_msg)
            raise DataValidationError(error_msg)

    def _log_dataset_stats(self) -> None:
        """
        Log comprehensive dataset statistics.
        """
        logger.info("-" * 60)
        logger.info("DATASET STATISTICS")
        logger.info("-" * 60)

        # Basic stats
        logger.info(f"Total Records: {len(self.df):,}")
        logger.info(f"Total Columns: {len(self.df.columns)}")

        # Date range
        date_min = self.df['invoice_date'].min()
        date_max = self.df['invoice_date'].max()
        logger.info(f"Date Range: {date_min.strftime('%Y-%m-%d')} to {date_max.strftime('%Y-%m-%d')}")
        logger.info(f"Time Span: {(date_max - date_min).days} days")

        # Product stats
        unique_products = self.df['product_id'].nunique()
        logger.info(f"Unique Products: {unique_products}")

        # Customer stats
        unique_customers = self.df['email'].nunique()
        logger.info(f"Unique Customers: {unique_customers}")

        # Revenue stats
        total_revenue = (self.df['qty'] * self.df['amount']).sum()
        total_quantity = self.df['qty'].sum()
        logger.info(f"Total Revenue: ${total_revenue:,.2f}")
        logger.info(f"Total Quantity Sold: {total_quantity:,}")
        logger.info(f"Average Transaction: ${total_revenue/len(self.df):,.2f}")

        # Missing value summary
        total_missing = self.df.isnull().sum().sum()
        if total_missing > 0:
            logger.info(f"Total Missing Values: {total_missing}")
        else:
            logger.info("No Missing Values: Dataset is 100% complete")

        logger.info("-" * 60)

    def get_data_info(self) -> Dict[str, Any]:
        """
        Get detailed information about the loaded dataset.

        Returns:
            dict: Comprehensive dataset statistics

        Raises:
            ValueError: If data not loaded
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        return {
            'total_records': len(self.df),
            'total_columns': len(self.df.columns),
            'date_range': {
                'start': self.df['invoice_date'].min(),
                'end': self.df['invoice_date'].max(),
                'days': (self.df['invoice_date'].max() - self.df['invoice_date'].min()).days
            },
            'unique_products': self.df['product_id'].nunique(),
            'unique_customers': self.df['email'].nunique(),
            'total_revenue': (self.df['qty'] * self.df['amount']).sum(),
            'total_quantity': self.df['qty'].sum(),
            'avg_transaction_value': (self.df['qty'] * self.df['amount']).mean(),
            'missing_values': self.df.isnull().sum().to_dict(),
            'duplicate_rows': self.df.duplicated().sum()
        }
