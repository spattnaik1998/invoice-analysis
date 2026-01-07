"""
Test Suite for KPI Computation Functions

This script tests all KPI calculation functions with various scenarios
and edge cases.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.utils.kpis import (
    calculate_total_revenue,
    calculate_total_quantity,
    calculate_average_transaction_value,
    calculate_num_transactions,
    calculate_all_kpis,
    calculate_unique_customers,
    calculate_unique_products,
    calculate_kpis_for_year,
    calculate_percentage_change,
    calculate_kpis_with_yoy_comparison,
    get_available_years,
    KPIError
)


def create_sample_data() -> pd.DataFrame:
    """Create sample invoice data for testing."""
    data = {
        'product_id': [100, 101, 100, 102, 101],
        'qty': [2, 1, 3, 1, 2],
        'amount': [10.0, 20.0, 10.0, 15.0, 20.0],
        'email': ['a@test.com', 'b@test.com', 'a@test.com', 'c@test.com', 'b@test.com'],
        'invoice_date': pd.date_range('2020-01-01', periods=5, freq='D')
    }

    df = pd.DataFrame(data)
    df['total_amount'] = df['qty'] * df['amount']
    df['invoice_year'] = df['invoice_date'].dt.year

    return df


def test_total_revenue():
    """Test total revenue calculation."""
    print("\n" + "="*70)
    print("TEST 1: Calculate Total Revenue")
    print("="*70)

    try:
        df = create_sample_data()

        # Expected: (2*10) + (1*20) + (3*10) + (1*15) + (2*20) = 20 + 20 + 30 + 15 + 40 = 125
        revenue = calculate_total_revenue(df)
        expected = 125.0

        assert revenue == expected, f"Expected {expected}, got {revenue}"

        print(f"[PASS] Total Revenue: ${revenue:,.2f}")
        print(f"[PASS] Expected: ${expected:,.2f}")
        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_total_quantity():
    """Test total quantity calculation."""
    print("\n" + "="*70)
    print("TEST 2: Calculate Total Quantity")
    print("="*70)

    try:
        df = create_sample_data()

        # Expected: 2 + 1 + 3 + 1 + 2 = 9
        qty = calculate_total_quantity(df)
        expected = 9

        assert qty == expected, f"Expected {expected}, got {qty}"

        print(f"[PASS] Total Quantity: {qty:,}")
        print(f"[PASS] Expected: {expected:,}")
        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_avg_transaction_value():
    """Test average transaction value calculation."""
    print("\n" + "="*70)
    print("TEST 3: Calculate Average Transaction Value")
    print("="*70)

    try:
        df = create_sample_data()

        # Expected: 125.0 / 5 = 25.0
        avg = calculate_average_transaction_value(df)
        expected = 25.0

        assert avg == expected, f"Expected {expected}, got {avg}"

        print(f"[PASS] Avg Transaction Value: ${avg:,.2f}")
        print(f"[PASS] Expected: ${expected:,.2f}")
        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_num_transactions():
    """Test number of transactions calculation."""
    print("\n" + "="*70)
    print("TEST 4: Calculate Number of Transactions")
    print("="*70)

    try:
        df = create_sample_data()

        # Expected: 5 rows
        count = calculate_num_transactions(df)
        expected = 5

        assert count == expected, f"Expected {expected}, got {count}"

        print(f"[PASS] Number of Transactions: {count:,}")
        print(f"[PASS] Expected: {expected:,}")
        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_all_kpis():
    """Test calculating all KPIs at once."""
    print("\n" + "="*70)
    print("TEST 5: Calculate All KPIs")
    print("="*70)

    try:
        df = create_sample_data()

        kpis = calculate_all_kpis(df)

        # Verify all keys exist
        required_keys = ['total_revenue', 'total_quantity', 'avg_transaction_value', 'num_transactions']
        assert all(key in kpis for key in required_keys), "Missing KPI keys"

        # Verify values
        assert kpis['total_revenue'] == 125.0, f"Revenue mismatch"
        assert kpis['total_quantity'] == 9, f"Quantity mismatch"
        assert kpis['avg_transaction_value'] == 25.0, f"Avg value mismatch"
        assert kpis['num_transactions'] == 5, f"Count mismatch"

        print(f"[PASS] All KPIs calculated successfully")
        print(f"[PASS] Total Revenue: ${kpis['total_revenue']:,.2f}")
        print(f"[PASS] Total Quantity: {kpis['total_quantity']:,}")
        print(f"[PASS] Avg Transaction: ${kpis['avg_transaction_value']:,.2f}")
        print(f"[PASS] Transactions: {kpis['num_transactions']:,}")
        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_empty_dataframe():
    """Test KPIs with empty DataFrame."""
    print("\n" + "="*70)
    print("TEST 6: KPIs with Empty DataFrame")
    print("="*70)

    try:
        df = pd.DataFrame()

        revenue = calculate_total_revenue(df)
        qty = calculate_total_quantity(df)
        avg = calculate_average_transaction_value(df)
        count = calculate_num_transactions(df)

        assert revenue == 0.0, "Empty DataFrame revenue should be 0.0"
        assert qty == 0, "Empty DataFrame quantity should be 0"
        assert avg == 0.0, "Empty DataFrame avg should be 0.0"
        assert count == 0, "Empty DataFrame count should be 0"

        print(f"[PASS] All KPIs return 0 for empty DataFrame")
        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_filtered_dataframe():
    """Test KPIs with filtered DataFrame."""
    print("\n" + "="*70)
    print("TEST 7: KPIs with Filtered DataFrame")
    print("="*70)

    try:
        df = create_sample_data()

        # Filter to only product_id 100
        filtered = df[df['product_id'] == 100]

        # Expected: 2 rows, qty=(2+3)=5, revenue=(20+30)=50, avg=25
        revenue = calculate_total_revenue(filtered)
        qty = calculate_total_quantity(filtered)
        count = calculate_num_transactions(filtered)

        assert count == 2, f"Expected 2 transactions, got {count}"
        assert qty == 5, f"Expected qty 5, got {qty}"
        assert revenue == 50.0, f"Expected revenue 50.0, got {revenue}"

        print(f"[PASS] Filtered to {count} transactions")
        print(f"[PASS] Revenue: ${revenue:,.2f}")
        print(f"[PASS] Quantity: {qty:,}")
        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_missing_column():
    """Test error handling for missing columns."""
    print("\n" + "="*70)
    print("TEST 8: Missing Column Error Handling")
    print("="*70)

    try:
        df = create_sample_data()
        df_no_qty = df.drop(columns=['qty'])

        # Should raise KPIError
        try:
            qty = calculate_total_quantity(df_no_qty)
            print("[FAIL] Should have raised KPIError")
            return False
        except KPIError as e:
            print(f"[PASS] Correctly raised KPIError")
            print(f"[INFO] Error: {str(e)[:80]}...")
            return True

    except Exception as e:
        print(f"[FAIL] Unexpected error: {str(e)}")
        return False


def test_revenue_without_total_amount():
    """Test revenue calculation without pre-computed total_amount column."""
    print("\n" + "="*70)
    print("TEST 9: Revenue Calculation (qty * amount)")
    print("="*70)

    try:
        df = create_sample_data()
        df_no_total = df.drop(columns=['total_amount'])

        # Should calculate from qty * amount
        revenue = calculate_total_revenue(df_no_total)
        expected = 125.0

        assert revenue == expected, f"Expected {expected}, got {revenue}"

        print(f"[PASS] Revenue calculated from qty * amount")
        print(f"[PASS] Revenue: ${revenue:,.2f}")
        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_unique_customers():
    """Test unique customer count."""
    print("\n" + "="*70)
    print("TEST 10: Calculate Unique Customers")
    print("="*70)

    try:
        df = create_sample_data()

        # Expected: 3 unique emails (a@test.com, b@test.com, c@test.com)
        customers = calculate_unique_customers(df)
        expected = 3

        assert customers == expected, f"Expected {expected}, got {customers}"

        print(f"[PASS] Unique Customers: {customers:,}")
        print(f"[PASS] Expected: {expected:,}")
        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_unique_products():
    """Test unique product count."""
    print("\n" + "="*70)
    print("TEST 11: Calculate Unique Products")
    print("="*70)

    try:
        df = create_sample_data()

        # Expected: 3 unique products (100, 101, 102)
        products = calculate_unique_products(df)
        expected = 3

        assert products == expected, f"Expected {expected}, got {products}"

        print(f"[PASS] Unique Products: {products:,}")
        print(f"[PASS] Expected: {expected:,}")
        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_kpis_with_real_data():
    """Test KPIs with actual invoice data if available."""
    print("\n" + "="*70)
    print("TEST 12: KPIs with Real Invoice Data")
    print("="*70)

    try:
        from src.data import DataLoader

        try:
            loader = DataLoader("data/invoices.csv")
            df = loader.load_data()

            kpis = calculate_all_kpis(df)

            # Verify reasonable values
            assert kpis['total_revenue'] > 0, "Revenue should be positive"
            assert kpis['total_quantity'] > 0, "Quantity should be positive"
            assert kpis['num_transactions'] == 10000, "Should have 10,000 transactions"

            print(f"[PASS] Real data KPIs calculated successfully")
            print(f"[INFO] Total Revenue: ${kpis['total_revenue']:,.2f}")
            print(f"[INFO] Total Quantity: {kpis['total_quantity']:,}")
            print(f"[INFO] Avg Transaction: ${kpis['avg_transaction_value']:,.2f}")
            print(f"[INFO] Transactions: {kpis['num_transactions']:,}")
            return True

        except FileNotFoundError:
            print("[SKIP] Real data file not found, skipping test")
            return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def create_multi_year_sample_data() -> pd.DataFrame:
    """Create sample invoice data with multiple years for YoY testing."""
    # 2020 data: 3 transactions
    data_2020 = {
        'product_id': [100, 101, 102],
        'qty': [2, 3, 1],
        'amount': [10.0, 20.0, 30.0],
        'email': ['a@test.com', 'b@test.com', 'c@test.com'],
        'invoice_date': pd.date_range('2020-01-01', periods=3, freq='D')
    }

    # 2021 data: 4 transactions (growth scenario)
    data_2021 = {
        'product_id': [100, 101, 102, 100],
        'qty': [3, 4, 2, 1],
        'amount': [10.0, 20.0, 30.0, 10.0],
        'email': ['a@test.com', 'b@test.com', 'c@test.com', 'd@test.com'],
        'invoice_date': pd.date_range('2021-01-01', periods=4, freq='D')
    }

    # 2022 data: 2 transactions (decline scenario)
    data_2022 = {
        'product_id': [100, 101],
        'qty': [1, 2],
        'amount': [10.0, 20.0],
        'email': ['a@test.com', 'b@test.com'],
        'invoice_date': pd.date_range('2022-01-01', periods=2, freq='D')
    }

    df_2020 = pd.DataFrame(data_2020)
    df_2021 = pd.DataFrame(data_2021)
    df_2022 = pd.DataFrame(data_2022)

    df = pd.concat([df_2020, df_2021, df_2022], ignore_index=True)
    df['total_amount'] = df['qty'] * df['amount']
    df['invoice_year'] = df['invoice_date'].dt.year

    return df


def test_get_available_years():
    """Test getting available years from data."""
    print("\n" + "="*70)
    print("TEST 13: Get Available Years")
    print("="*70)

    try:
        df = create_multi_year_sample_data()

        years = get_available_years(df)
        expected = [2020, 2021, 2022]

        assert years == expected, f"Expected {expected}, got {years}"

        print(f"[PASS] Available years: {years}")
        print(f"[PASS] Expected: {expected}")
        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_calculate_kpis_for_year():
    """Test calculating KPIs for a specific year."""
    print("\n" + "="*70)
    print("TEST 14: Calculate KPIs for Specific Year")
    print("="*70)

    try:
        df = create_multi_year_sample_data()

        # Test 2020 data
        kpis_2020 = calculate_kpis_for_year(df, 2020)

        # 2020: (2*10) + (3*20) + (1*30) = 20 + 60 + 30 = 110
        assert kpis_2020['year'] == 2020
        assert kpis_2020['total_revenue'] == 110.0
        assert kpis_2020['total_quantity'] == 6  # 2+3+1
        assert kpis_2020['num_transactions'] == 3
        assert kpis_2020['unique_customers'] == 3

        # Test 2021 data
        kpis_2021 = calculate_kpis_for_year(df, 2021)

        # 2021: (3*10) + (4*20) + (2*30) + (1*10) = 30 + 80 + 60 + 10 = 180
        assert kpis_2021['year'] == 2021
        assert kpis_2021['total_revenue'] == 180.0
        assert kpis_2021['total_quantity'] == 10  # 3+4+2+1
        assert kpis_2021['num_transactions'] == 4

        print(f"[PASS] 2020 KPIs: Revenue=${kpis_2020['total_revenue']:,.2f}, Qty={kpis_2020['total_quantity']:,}")
        print(f"[PASS] 2021 KPIs: Revenue=${kpis_2021['total_revenue']:,.2f}, Qty={kpis_2021['total_quantity']:,}")
        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_calculate_percentage_change():
    """Test percentage change calculation."""
    print("\n" + "="*70)
    print("TEST 15: Calculate Percentage Change")
    print("="*70)

    try:
        # Test increase
        change = calculate_percentage_change(120, 100)
        assert change == 20.0, f"Expected 20.0%, got {change}%"
        print(f"[PASS] 100 -> 120 = {change:+.2f}% (increase)")

        # Test decrease
        change = calculate_percentage_change(80, 100)
        assert change == -20.0, f"Expected -20.0%, got {change}%"
        print(f"[PASS] 100 -> 80 = {change:+.2f}% (decrease)")

        # Test no change
        change = calculate_percentage_change(100, 100)
        assert change == 0.0, f"Expected 0.0%, got {change}%"
        print(f"[PASS] 100 -> 100 = {change:+.2f}% (no change)")

        # Test division by zero
        change = calculate_percentage_change(100, 0)
        assert change is None, f"Expected None for division by zero, got {change}"
        print(f"[PASS] 0 -> 100 = None (division by zero handled)")

        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_yoy_comparison_with_data():
    """Test year-over-year comparison with data."""
    print("\n" + "="*70)
    print("TEST 16: Year-over-Year Comparison (With Prior Year)")
    print("="*70)

    try:
        df = create_multi_year_sample_data()

        # Compare 2021 vs 2020
        result = calculate_kpis_with_yoy_comparison(df, 2021)

        # Verify structure
        assert 'current' in result
        assert 'previous' in result
        assert 'comparison' in result

        # Verify current year (2021)
        assert result['current']['year'] == 2021
        assert result['current']['total_revenue'] == 180.0
        assert result['current']['num_transactions'] == 4

        # Verify previous year (2020)
        assert result['previous'] is not None
        assert result['previous']['year'] == 2020
        assert result['previous']['total_revenue'] == 110.0
        assert result['previous']['num_transactions'] == 3

        # Verify comparison (2021 vs 2020)
        # Revenue: (180-110)/110 * 100 = 63.64%
        revenue_change = result['comparison']['total_revenue_change']
        assert revenue_change is not None
        assert abs(revenue_change - 63.636363) < 0.01, f"Expected ~63.64%, got {revenue_change}%"

        # Transactions: (4-3)/3 * 100 = 33.33%
        txn_change = result['comparison']['num_transactions_change']
        assert txn_change is not None
        assert abs(txn_change - 33.333333) < 0.01, f"Expected ~33.33%, got {txn_change}%"

        print(f"[PASS] 2021 Revenue: ${result['current']['total_revenue']:,.2f}")
        print(f"[PASS] 2020 Revenue: ${result['previous']['total_revenue']:,.2f}")
        print(f"[PASS] YoY Revenue Change: {revenue_change:+.2f}%")
        print(f"[PASS] YoY Transaction Change: {txn_change:+.2f}%")
        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_yoy_comparison_without_prior_data():
    """Test year-over-year comparison without prior year data."""
    print("\n" + "="*70)
    print("TEST 17: Year-over-Year Comparison (No Prior Year)")
    print("="*70)

    try:
        df = create_multi_year_sample_data()

        # Compare 2020 (first year, no prior)
        result = calculate_kpis_with_yoy_comparison(df, 2020)

        # Verify current year exists
        assert result['current'] is not None
        assert result['current']['year'] == 2020
        assert result['current']['total_revenue'] == 110.0

        # Verify previous year is None
        assert result['previous'] is None

        # Verify all comparisons are None
        assert result['comparison']['total_revenue_change'] is None
        assert result['comparison']['total_quantity_change'] is None
        assert result['comparison']['avg_transaction_value_change'] is None
        assert result['comparison']['num_transactions_change'] is None

        print(f"[PASS] 2020 Revenue: ${result['current']['total_revenue']:,.2f}")
        print(f"[PASS] No prior year data, all comparisons are None")
        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_yoy_comparison_decline_scenario():
    """Test year-over-year comparison with declining metrics."""
    print("\n" + "="*70)
    print("TEST 18: Year-over-Year Comparison (Decline Scenario)")
    print("="*70)

    try:
        df = create_multi_year_sample_data()

        # Compare 2022 vs 2021 (decline)
        result = calculate_kpis_with_yoy_comparison(df, 2022)

        # 2022: (1*10) + (2*20) = 10 + 40 = 50
        # 2021: 180
        # Change: (50-180)/180 * 100 = -72.22%

        assert result['current']['year'] == 2022
        assert result['current']['total_revenue'] == 50.0
        assert result['previous']['year'] == 2021
        assert result['previous']['total_revenue'] == 180.0

        revenue_change = result['comparison']['total_revenue_change']
        assert revenue_change is not None
        assert revenue_change < 0, "Revenue should decline"
        assert abs(revenue_change - (-72.222222)) < 0.01, f"Expected ~-72.22%, got {revenue_change}%"

        print(f"[PASS] 2022 Revenue: ${result['current']['total_revenue']:,.2f}")
        print(f"[PASS] 2021 Revenue: ${result['previous']['total_revenue']:,.2f}")
        print(f"[PASS] YoY Revenue Change: {revenue_change:+.2f}% (decline)")
        return True

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "#"*70)
    print("# KPI COMPUTATION - TEST SUITE")
    print("#"*70)

    results = []

    # Run basic KPI tests
    results.append(("Total Revenue", test_total_revenue()))
    results.append(("Total Quantity", test_total_quantity()))
    results.append(("Average Transaction Value", test_avg_transaction_value()))
    results.append(("Number of Transactions", test_num_transactions()))
    results.append(("All KPIs", test_all_kpis()))
    results.append(("Empty DataFrame", test_empty_dataframe()))
    results.append(("Filtered DataFrame", test_filtered_dataframe()))
    results.append(("Missing Column", test_missing_column()))
    results.append(("Revenue (qty*amount)", test_revenue_without_total_amount()))
    results.append(("Unique Customers", test_unique_customers()))
    results.append(("Unique Products", test_unique_products()))
    results.append(("Real Data KPIs", test_kpis_with_real_data()))

    # Run period-over-period comparison tests
    results.append(("Get Available Years", test_get_available_years()))
    results.append(("KPIs for Specific Year", test_calculate_kpis_for_year()))
    results.append(("Percentage Change", test_calculate_percentage_change()))
    results.append(("YoY Comparison (Growth)", test_yoy_comparison_with_data()))
    results.append(("YoY Comparison (No Prior)", test_yoy_comparison_without_prior_data()))
    results.append(("YoY Comparison (Decline)", test_yoy_comparison_decline_scenario()))

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
