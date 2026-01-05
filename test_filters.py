"""
Test Suite for Filtering Functions

This script tests the reusable filtering functions with various scenarios
and edge cases.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.utils.filters import (
    filter_by_years,
    filter_by_products,
    filter_by_date_range,
    apply_combined_filters,
    FilterError
)


def create_sample_data() -> pd.DataFrame:
    """Create sample invoice data for testing."""
    np.random.seed(42)

    dates = pd.date_range('2020-01-01', '2022-12-31', freq='D')
    n_records = 100

    data = {
        'invoice_date': np.random.choice(dates, n_records),
        'product_id': np.random.randint(100, 110, n_records),
        'qty': np.random.randint(1, 10, n_records),
        'amount': np.random.uniform(10, 100, n_records),
        'email': [f'user{i}@example.com' for i in range(n_records)]
    }

    df = pd.DataFrame(data)
    df['invoice_year'] = df['invoice_date'].dt.year
    df['total_amount'] = df['qty'] * df['amount']

    return df


def test_filter_by_years_list():
    """Test filtering with a list of years."""
    print("\n" + "="*70)
    print("TEST 1: Filter by Years (List)")
    print("="*70)

    try:
        df = create_sample_data()
        initial_count = len(df)

        # Filter by specific years
        filtered = filter_by_years(df, [2020, 2021])

        # Verify results
        unique_years = filtered['invoice_year'].unique()
        assert all(year in [2020, 2021] for year in unique_years), "Invalid years in result"
        assert len(filtered) < initial_count, "Filtering should reduce row count"

        print(f"[PASS] Initial rows: {initial_count:,}")
        print(f"[PASS] Filtered rows: {len(filtered):,}")
        print(f"[PASS] Years in result: {sorted(unique_years)}")
        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_filter_by_years_range():
    """Test filtering with a range object."""
    print("\n" + "="*70)
    print("TEST 2: Filter by Years (Range)")
    print("="*70)

    try:
        df = create_sample_data()

        # Filter using range
        filtered = filter_by_years(df, range(2020, 2022))

        # Verify results
        unique_years = filtered['invoice_year'].unique()
        assert all(year in [2020, 2021] for year in unique_years), "Invalid years in result"

        print(f"[PASS] Filtered using range(2020, 2022)")
        print(f"[PASS] Rows: {len(filtered):,}")
        print(f"[PASS] Years: {sorted(unique_years)}")
        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_filter_by_years_none():
    """Test filtering with None (no filtering)."""
    print("\n" + "="*70)
    print("TEST 3: Filter by Years (None - No Filtering)")
    print("="*70)

    try:
        df = create_sample_data()

        # Filter with None
        filtered = filter_by_years(df, None)

        # Should return all data
        assert len(filtered) == len(df), "None should return all rows"

        print(f"[PASS] None returned all {len(filtered):,} rows")
        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_filter_by_years_empty():
    """Test filtering with empty list."""
    print("\n" + "="*70)
    print("TEST 4: Filter by Years (Empty List)")
    print("="*70)

    try:
        df = create_sample_data()

        # Filter with empty list
        filtered = filter_by_years(df, [])

        # Should return empty DataFrame with same schema
        assert len(filtered) == 0, "Empty list should return 0 rows"
        assert list(filtered.columns) == list(df.columns), "Columns should match"

        print(f"[PASS] Empty list returned 0 rows")
        print(f"[PASS] Schema preserved: {len(filtered.columns)} columns")
        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_filter_by_years_nonexistent():
    """Test filtering with years that don't exist in data."""
    print("\n" + "="*70)
    print("TEST 5: Filter by Years (Non-existent Years)")
    print("="*70)

    try:
        df = create_sample_data()

        # Filter with years not in data
        filtered = filter_by_years(df, [1999, 2050])

        # Should return empty DataFrame
        assert len(filtered) == 0, "Non-existent years should return 0 rows"

        print(f"[PASS] Non-existent years returned 0 rows")
        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_filter_by_years_missing_column():
    """Test error handling for missing year column."""
    print("\n" + "="*70)
    print("TEST 6: Filter by Years (Missing Column)")
    print("="*70)

    try:
        df = create_sample_data()
        df_no_year = df.drop(columns=['invoice_year'])

        # Should raise FilterError
        try:
            filtered = filter_by_years(df_no_year, [2020])
            print("[FAIL] Should have raised FilterError")
            return False
        except FilterError as e:
            print(f"[PASS] Correctly raised FilterError")
            print(f"[INFO] Error: {str(e)[:80]}...")
            return True

    except Exception as e:
        print(f"[FAIL] Unexpected error: {str(e)}")
        return False


def test_filter_by_products():
    """Test product filtering."""
    print("\n" + "="*70)
    print("TEST 7: Filter by Products")
    print("="*70)

    try:
        df = create_sample_data()

        # Filter by products
        filtered = filter_by_products(df, [100, 101, 102])

        # Verify results
        unique_products = filtered['product_id'].unique()
        assert all(pid in [100, 101, 102] for pid in unique_products), "Invalid products"

        print(f"[PASS] Filtered to products [100, 101, 102]")
        print(f"[PASS] Rows: {len(filtered):,}")
        print(f"[PASS] Products in result: {sorted(unique_products)}")
        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_filter_by_date_range():
    """Test date range filtering."""
    print("\n" + "="*70)
    print("TEST 8: Filter by Date Range")
    print("="*70)

    try:
        df = create_sample_data()

        # Filter by date range
        start = pd.Timestamp('2021-01-01')
        end = pd.Timestamp('2021-12-31')
        filtered = filter_by_date_range(df, start, end)

        # Verify results
        assert filtered['invoice_date'].min() >= start, "Start date violated"
        assert filtered['invoice_date'].max() <= end, "End date violated"

        print(f"[PASS] Filtered to 2021")
        print(f"[PASS] Rows: {len(filtered):,}")
        print(f"[PASS] Date range: {filtered['invoice_date'].min()} to {filtered['invoice_date'].max()}")
        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_combined_filters():
    """Test applying multiple filters together."""
    print("\n" + "="*70)
    print("TEST 9: Combined Filters")
    print("="*70)

    try:
        df = create_sample_data()
        initial_count = len(df)

        # Apply combined filters
        filtered = apply_combined_filters(
            df,
            years=[2020, 2021],
            product_ids=[100, 101]
        )

        # Verify results
        assert len(filtered) < initial_count, "Should reduce row count"
        assert all(year in [2020, 2021] for year in filtered['invoice_year'].unique()), "Year filter failed"
        assert all(pid in [100, 101] for pid in filtered['product_id'].unique()), "Product filter failed"

        print(f"[PASS] Combined filters applied successfully")
        print(f"[PASS] {initial_count:,} -> {len(filtered):,} rows")
        print(f"[PASS] Years: {sorted(filtered['invoice_year'].unique())}")
        print(f"[PASS] Products: {sorted(filtered['product_id'].unique())}")
        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_empty_dataframe():
    """Test filtering on empty DataFrame."""
    print("\n" + "="*70)
    print("TEST 10: Filter Empty DataFrame")
    print("="*70)

    try:
        df = pd.DataFrame()

        # Should handle gracefully
        filtered = filter_by_years(df, [2020])

        print(f"[PASS] Empty DataFrame handled gracefully")
        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "#"*70)
    print("# FILTERING FUNCTIONS - TEST SUITE")
    print("#"*70)

    results = []

    # Run tests
    results.append(("Filter by Years (List)", test_filter_by_years_list()))
    results.append(("Filter by Years (Range)", test_filter_by_years_range()))
    results.append(("Filter by Years (None)", test_filter_by_years_none()))
    results.append(("Filter by Years (Empty)", test_filter_by_years_empty()))
    results.append(("Filter by Years (Non-existent)", test_filter_by_years_nonexistent()))
    results.append(("Filter by Years (Missing Column)", test_filter_by_years_missing_column()))
    results.append(("Filter by Products", test_filter_by_products()))
    results.append(("Filter by Date Range", test_filter_by_date_range()))
    results.append(("Combined Filters", test_combined_filters()))
    results.append(("Empty DataFrame", test_empty_dataframe()))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n*** All tests passed! ***")
        return 0
    else:
        print(f"\n*** {total - passed} test(s) failed ***")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
