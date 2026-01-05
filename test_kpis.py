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


def main():
    """Run all tests."""
    print("\n" + "#"*70)
    print("# KPI COMPUTATION - TEST SUITE")
    print("#"*70)

    results = []

    # Run tests
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
