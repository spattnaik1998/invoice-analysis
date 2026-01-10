"""
Test script for forecasting module
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from src.data import DataLoader
from src.visualization import ForecastingComponents
import pandas as pd

def test_forecasting():
    """Test the forecasting functionality."""
    print("=" * 60)
    print("FORECASTING MODULE TEST")
    print("=" * 60)

    # Load model
    print("\n1. Loading ARIMA model...")
    model_path = "arima_final_model.pkl"
    model = ForecastingComponents.load_arima_model(model_path)

    if model is None:
        print("   [FAIL] Failed to load model")
        return False
    print("   [PASS] Model loaded successfully")

    # Load data
    print("\n2. Loading historical data...")
    loader = DataLoader("data/invoices.csv")
    df = loader.load_data()
    print(f"   [PASS] Loaded {len(df)} invoice records")

    # Prepare time series
    print("\n3. Preparing daily time series...")
    historical_series = ForecastingComponents.prepare_historical_data(df)
    print(f"   [PASS] Time series prepared: {len(historical_series)} days")
    print(f"   [PASS] Date range: {historical_series.index.min()} to {historical_series.index.max()}")

    # Generate forecast
    print("\n4. Generating 30-day forecast...")
    forecast_df, stats = ForecastingComponents.generate_forecast(
        model,
        steps=30,
        last_date=historical_series.index[-1]
    )

    if forecast_df.empty:
        print("   [FAIL] Failed to generate forecast")
        return False

    print(f"   [PASS] Forecast generated: {len(forecast_df)} days")
    print(f"   [PASS] Forecast date range: {forecast_df['date'].min()} to {forecast_df['date'].max()}")

    # Display statistics
    print("\n5. Forecast Statistics:")
    print(f"   - Total Forecasted Revenue: ${stats['total_forecast']:,.2f}")
    print(f"   - Average Daily Revenue: ${stats['mean_forecast']:,.2f}")
    print(f"   - Min Daily Revenue: ${stats['min_forecast']:,.2f}")
    print(f"   - Max Daily Revenue: ${stats['max_forecast']:,.2f}")
    print(f"   - Std Deviation: ${stats['std_forecast']:,.2f}")

    # Display sample forecast
    print("\n6. Sample Forecast (First 5 Days):")
    print(forecast_df.head().to_string(index=False))

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)

    return True

if __name__ == "__main__":
    try:
        success = test_forecasting()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
