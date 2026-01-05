"""
Test Script for CSV Ingestion Module

This script tests the robust CSV ingestion functionality with various scenarios.
Run this to verify the data loader is working correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.data import DataLoader, DataValidationError


def test_successful_ingestion():
    """Test successful data loading with valid CSV."""
    print("\n" + "="*70)
    print("TEST 1: Successful Ingestion with Valid Data")
    print("="*70)

    try:
        loader = DataLoader("data/invoices.csv")
        df = loader.load_data()

        print(f"\n[PASS] Data loaded successfully!")
        print(f"[PASS] DataFrame shape: {df.shape}")
        print(f"[PASS] Columns: {list(df.columns)}")

        # Display info
        info = loader.get_data_info()
        print(f"\n[INFO] Total Records: {info['total_records']:,}")
        print(f"[INFO] Unique Products: {info['unique_products']}")
        print(f"[INFO] Unique Customers: {info['unique_customers']}")
        print(f"[INFO] Total Revenue: ${info['total_revenue']:,.2f}")
        print(f"[INFO] Date Range: {info['date_range']['days']} days")

        return True

    except Exception as e:
        print(f"\n[FAIL] Test failed: {str(e)}")
        return False


def test_missing_file():
    """Test error handling for missing file."""
    print("\n" + "="*70)
    print("TEST 2: Missing File Error Handling")
    print("="*70)

    try:
        loader = DataLoader("data/nonexistent.csv")
        df = loader.load_data()
        print("\n[FAIL] Test failed: Should have raised FileNotFoundError")
        return False

    except FileNotFoundError as e:
        print(f"\n[PASS] Correctly caught FileNotFoundError")
        print(f"[INFO] Error message: {str(e)[:100]}...")
        return True

    except Exception as e:
        print(f"\n[FAIL] Unexpected error: {str(e)}")
        return False


def test_data_info_before_loading():
    """Test error when calling get_data_info before loading."""
    print("\n" + "="*70)
    print("TEST 3: get_data_info Before Loading Data")
    print("="*70)

    try:
        loader = DataLoader("data/invoices.csv")
        info = loader.get_data_info()  # Should fail
        print("\n[FAIL] Test failed: Should have raised ValueError")
        return False

    except ValueError as e:
        print(f"\n[PASS] Correctly caught ValueError")
        print(f"[INFO] Error message: {str(e)}")
        return True

    except Exception as e:
        print(f"\n[FAIL] Unexpected error: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "#"*70)
    print("# CSV INGESTION MODULE - TEST SUITE")
    print("#"*70)

    results = []

    # Run tests
    results.append(("Successful Ingestion", test_successful_ingestion()))
    results.append(("Missing File Handling", test_missing_file()))
    results.append(("Data Info Before Load", test_data_info_before_loading()))

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
