"""
Test script for LSTM forecasting module

This script tests the LSTM forecasting functionality to ensure it works correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.data import DataLoader, DataTransformer
from src.visualization import ForecastingComponents, LSTMForecastingComponents
from config import DATA_FILE

def test_lstm_forecasting():
    """Test LSTM forecasting module"""

    print("=" * 60)
    print("LSTM FORECASTING MODULE TEST")
    print("=" * 60)
    print()

    # Test 1: Load LSTM model
    print("1. Loading LSTM model...")
    lstm_model_path = Path(__file__).parent / "lstm_model.h5"

    if not lstm_model_path.exists():
        print(f"   [FAIL] LSTM model not found at: {lstm_model_path}")
        return False

    lstm_model = LSTMForecastingComponents.load_lstm_model(str(lstm_model_path))

    if lstm_model is None:
        print("   [FAIL] Failed to load LSTM model")
        return False

    print("   [PASS] LSTM model loaded successfully")
    print(f"   Model type: {type(lstm_model)}")
    print()

    # Test 2: Load data
    print("2. Loading historical data...")
    try:
        loader = DataLoader(str(DATA_FILE))
        df = loader.load_data()
        print(f"   [PASS] Loaded {len(df)} invoice records")
    except Exception as e:
        print(f"   [FAIL] Error loading data: {e}")
        return False
    print()

    # Test 3: Prepare time series
    print("3. Preparing daily time series...")
    try:
        historical_series = ForecastingComponents.prepare_historical_data(df)
        print(f"   [PASS] Time series prepared: {len(historical_series)} days")
        print(f"   [PASS] Date range: {historical_series.index[0]} to {historical_series.index[-1]}")
    except Exception as e:
        print(f"   [FAIL] Error preparing time series: {e}")
        return False
    print()

    # Test 4: Generate LSTM forecast
    print("4. Generating 30-day LSTM forecast...")
    try:
        forecast_df, stats = LSTMForecastingComponents.generate_lstm_forecast(
            lstm_model,
            historical_series,
            steps=30,
            look_back=60
        )

        if forecast_df.empty:
            print("   [FAIL] Forecast dataframe is empty")
            return False

        print(f"   [PASS] Forecast generated: {len(forecast_df)} days")
        print(f"   [PASS] Forecast date range: {forecast_df['date'].iloc[0]} to {forecast_df['date'].iloc[-1]}")
    except Exception as e:
        print(f"   [FAIL] Error generating forecast: {e}")
        import traceback
        traceback.print_exc()
        return False
    print()

    # Test 5: Display statistics
    print("5. LSTM Forecast Statistics:")
    print(f"   - Total Forecasted Revenue: ${stats['total_forecast']:,.2f}")
    print(f"   - Average Daily Revenue: ${stats['mean_forecast']:,.2f}")
    print(f"   - Min Daily Revenue: ${stats['min_forecast']:,.2f}")
    print(f"   - Max Daily Revenue: ${stats['max_forecast']:,.2f}")
    print(f"   - Std Deviation: ${stats['std_forecast']:,.2f}")
    print()

    # Test 6: Generate ARIMA forecast for comparison
    print("6. Generating ARIMA forecast for comparison...")
    arima_model_path = Path(__file__).parent / "arima_final_model.pkl"

    if arima_model_path.exists():
        arima_model = ForecastingComponents.load_arima_model(str(arima_model_path))
        if arima_model:
            arima_forecast_df, arima_stats = ForecastingComponents.generate_forecast(
                arima_model,
                30,
                historical_series.index[-1]
            )

            print("   [PASS] ARIMA forecast generated for comparison")
            print(f"   - ARIMA Total: ${arima_stats['total_forecast']:,.2f}")
            print(f"   - ARIMA Avg Daily: ${arima_stats['mean_forecast']:,.2f}")

            # Calculate difference
            lstm_total = stats['total_forecast']
            arima_total = arima_stats['total_forecast']
            diff = lstm_total - arima_total
            diff_pct = (diff / arima_total * 100) if arima_total != 0 else 0

            print()
            print("7. LSTM vs ARIMA Comparison:")
            print(f"   - Difference in Total Revenue: ${diff:,.2f} ({diff_pct:+.1f}%)")
            print(f"   - LSTM {'predicts higher' if diff > 0 else 'predicts lower'} revenue than ARIMA")
    else:
        print("   [SKIP] ARIMA model not found for comparison")

    print()
    print("=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_lstm_forecasting()
    sys.exit(0 if success else 1)
