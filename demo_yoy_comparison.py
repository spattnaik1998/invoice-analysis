"""
Demonstration: Year-over-Year KPI Comparison

This script demonstrates the new period-over-period comparison features
added to the KPI module.
"""

import sys
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.data import DataLoader, DataTransformer
from src.utils.kpis import (
    calculate_kpis_for_year,
    calculate_kpis_with_yoy_comparison,
    get_available_years
)


def main():
    """Demonstrate YoY comparison functionality."""

    print("\n" + "="*70)
    print("YEAR-OVER-YEAR KPI COMPARISON DEMONSTRATION")
    print("="*70)

    # Load the invoice data
    print("\n[1] Loading invoice data...")
    try:
        loader = DataLoader("data/invoices.csv")
        df = loader.load_data()

        # Add derived fields (invoice_year is needed)
        transformer = DataTransformer(df)
        data = transformer.df

        print(f"    Loaded {len(data):,} invoice records")

    except FileNotFoundError:
        print("    ERROR: Invoice data file not found!")
        print("    Please ensure data/invoices.csv exists.")
        return

    # Get available years
    print("\n[2] Getting available years...")
    years = get_available_years(data)
    print(f"    Available years: {min(years)} to {max(years)}")
    print(f"    Total years: {len(years)}")

    # Calculate KPIs for most recent year
    recent_year = max(years)
    print(f"\n[3] Calculating KPIs for {recent_year}...")
    kpis_recent = calculate_kpis_for_year(data, recent_year)

    print(f"    Total Revenue: ${kpis_recent['total_revenue']:,.2f}")
    print(f"    Total Quantity: {kpis_recent['total_quantity']:,} units")
    print(f"    Avg Transaction: ${kpis_recent['avg_transaction_value']:,.2f}")
    print(f"    Transactions: {kpis_recent['num_transactions']:,}")
    print(f"    Unique Customers: {kpis_recent['unique_customers']:,}")
    print(f"    Unique Products: {kpis_recent['unique_products']:,}")

    # Year-over-year comparison for recent year
    print(f"\n[4] Year-over-Year Comparison: {recent_year} vs {recent_year-1}")
    yoy_result = calculate_kpis_with_yoy_comparison(data, recent_year)

    if yoy_result['previous'] is not None:
        print(f"\n    Current Year ({recent_year}):")
        print(f"        Revenue: ${yoy_result['current']['total_revenue']:,.2f}")
        print(f"        Transactions: {yoy_result['current']['num_transactions']:,}")

        print(f"\n    Previous Year ({recent_year-1}):")
        print(f"        Revenue: ${yoy_result['previous']['total_revenue']:,.2f}")
        print(f"        Transactions: {yoy_result['previous']['num_transactions']:,}")

        print(f"\n    Year-over-Year Changes:")
        comp = yoy_result['comparison']

        if comp['total_revenue_change'] is not None:
            sign = "UP  " if comp['total_revenue_change'] > 0 else "DOWN" if comp['total_revenue_change'] < 0 else "FLAT"
            print(f"        [{sign}] Revenue: {comp['total_revenue_change']:+.2f}%")

        if comp['total_quantity_change'] is not None:
            sign = "UP  " if comp['total_quantity_change'] > 0 else "DOWN" if comp['total_quantity_change'] < 0 else "FLAT"
            print(f"        [{sign}] Quantity: {comp['total_quantity_change']:+.2f}%")

        if comp['num_transactions_change'] is not None:
            sign = "UP  " if comp['num_transactions_change'] > 0 else "DOWN" if comp['num_transactions_change'] < 0 else "FLAT"
            print(f"        [{sign}] Transactions: {comp['num_transactions_change']:+.2f}%")

        if comp['avg_transaction_value_change'] is not None:
            sign = "UP  " if comp['avg_transaction_value_change'] > 0 else "DOWN" if comp['avg_transaction_value_change'] < 0 else "FLAT"
            print(f"        [{sign}] Avg Transaction: {comp['avg_transaction_value_change']:+.2f}%")
    else:
        print(f"    No data available for previous year ({recent_year-1})")

    # Compare multiple years
    print(f"\n[5] Comparing Last 5 Years:")
    print(f"\n    {'Year':<8} {'Revenue':<15} {'Transactions':<15} {'YoY Change':<15}")
    print(f"    {'-'*8} {'-'*15} {'-'*15} {'-'*15}")

    recent_years = sorted(years)[-5:]
    for year in recent_years:
        kpis = calculate_kpis_for_year(data, year)
        yoy = calculate_kpis_with_yoy_comparison(data, year)

        revenue_str = f"${kpis['total_revenue']:,.0f}"
        txn_str = f"{kpis['num_transactions']:,}"

        if yoy['comparison']['total_revenue_change'] is not None:
            change = yoy['comparison']['total_revenue_change']
            change_str = f"{change:+.2f}%"
        else:
            change_str = "N/A"

        print(f"    {year:<8} {revenue_str:<15} {txn_str:<15} {change_str:<15}")

    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70)
    print("\nNew Functions Available:")
    print("  - calculate_kpis_for_year(df, year)")
    print("  - calculate_kpis_with_yoy_comparison(df, current_year)")
    print("  - get_available_years(df)")
    print("\nThese functions support:")
    print("  [+] Period-over-period comparison")
    print("  [+] Percentage change calculation")
    print("  [+] Graceful handling of missing prior periods")
    print("  [+] Returns both absolute values and deltas")
    print()


if __name__ == "__main__":
    main()
