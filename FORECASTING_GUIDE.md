# Revenue Forecasting Feature Guide

## Overview

The Revenue Forecasting tab uses a trained ARIMA(0,0,0) model to predict future daily revenue based on historical transaction data. This feature provides business intelligence for budget planning, capacity planning, and strategic decision-making.

---

## Features

### 1. Interactive Forecast Controls

**Forecast Horizon Options:**
- **Next 30 Days** - Short-term revenue projections
- **Next 90 Days** - Quarterly planning horizon
- **Next 6 Months** - Medium-term forecasting (180 days)
- **Next 1 Year** - Annual revenue projections (365 days)
- **Next 2 Years** - Long-term strategic planning (730 days)
- **Custom** - User-defined forecast period (1-3650 days)

**Historical Data Display:**
- **Last 3 Months** - Recent trend context (90 days)
- **Last 6 Months** - Medium-term historical view (180 days)
- **Last 1 Year** - Annual comparison (365 days)
- **Last 2 Years** - Extended trend analysis (730 days)
- **All Data** - Complete historical dataset (1970-2022)

### 2. Forecast Visualizations

#### Main Forecast Chart
- **Historical Revenue Line**: Power BI yellow (#FFC000) - Shows actual daily revenue
- **Forecast Line**: Teal (#4ECDC4) with diamond markers - Shows predicted revenue
- **Interactive Features**:
  - Hover tooltips with exact date and revenue values
  - Zoom and pan capabilities
  - Dark theme consistent with main dashboard

#### Aggregated Forecasts
- **Monthly Aggregation**: Bar chart showing total forecasted revenue per month
- **Yearly Aggregation**: Bar chart showing total forecasted revenue per year (requires 365+ days)
- Automatically aggregates daily forecasts into higher-level summaries

### 3. Forecast Statistics Dashboard

**Key Metrics:**
- **Forecast Period**: Number of days forecasted
- **Total Forecasted Revenue**: Sum of all forecasted daily revenues
- **Avg Daily Revenue**: Mean forecasted daily revenue
- **Std Deviation**: Standard deviation of forecast (indicates variability)

**Detailed Statistics:**
- Minimum and maximum daily revenue in forecast period
- Model information and training details

### 4. Forecast Data Table

- **First 10 Days**: Shows the beginning of the forecast period
- **Last 10 Days**: Shows the end of the forecast period
- Date and forecasted revenue formatted for easy reading

---

## Model Information

### ARIMA(0,0,0) Specifications

**Model Type**: ARIMA(0,0,0) - Also known as a "white noise" or "mean" model

**Training Details:**
- **Training Period**: January 5, 1970 to January 17, 2022 (52 years)
- **Observations**: 19,006 daily data points
- **Target Variable**: Daily total revenue (sum of all transactions per day)

**Performance Metrics:**
- **AIC**: 263,077.78 (Akaike Information Criterion)
- **BIC**: 263,093.48 (Bayesian Information Criterion)
- **RMSE**: 233.14 (Root Mean Square Error)
- **MAE**: 174.32 (Mean Absolute Error)

### Model Interpretation

The ARIMA(0,0,0) model provides forecasts based on the historical mean of the time series. This means:

1. **Constant Forecast**: The model predicts a constant value for all future periods
2. **Historical Average**: Forecasts represent the average daily revenue from the training period (~$139.79/day)
3. **Baseline Estimate**: Provides a conservative baseline for revenue planning
4. **No Trend**: Does not capture increasing/decreasing trends in the data
5. **No Seasonality**: Does not account for seasonal patterns (day of week, month, etc.)

### When to Use This Model

**Suitable For:**
- Baseline revenue projections
- Conservative budget planning
- Long-term average expectations
- Comparison benchmarks for other models

**Limitations:**
- Does not capture growth trends
- Ignores seasonal variations
- May underestimate during growth periods
- May overestimate during decline periods

---

## Use Cases

### 1. Budget Planning
- **Scenario**: Annual budget preparation
- **How to Use**:
  1. Select "Next 1 Year" horizon
  2. Review "Total Forecasted Revenue" statistic
  3. Use yearly aggregation chart for monthly breakdown
  4. Compare with historical data for context

### 2. Capacity Planning
- **Scenario**: Inventory and staffing decisions
- **How to Use**:
  1. Select "Next 90 Days" for quarterly planning
  2. Review average daily revenue to estimate product demand
  3. Use monthly aggregation to plan inventory orders
  4. Monitor historical trends to validate assumptions

### 3. Strategic Planning
- **Scenario**: Multi-year business strategy
- **How to Use**:
  1. Select "Next 2 Years" horizon
  2. Use yearly aggregation for long-term projections
  3. Compare forecast with historical growth patterns
  4. Consider external factors not captured by the model

### 4. Performance Monitoring
- **Scenario**: Track actual vs. forecasted performance
- **How to Use**:
  1. Generate forecast for current period
  2. Compare actual revenue to forecast baseline
  3. Identify periods of over/under-performance
  4. Investigate reasons for significant deviations

---

## Technical Implementation

### Architecture

```
src/visualization/forecasting.py
├── ForecastingComponents (Main class)
│   ├── load_arima_model() - Load pickle model with caching
│   ├── prepare_historical_data() - Aggregate daily revenue
│   ├── generate_forecast() - Generate multi-step forecast
│   ├── render_forecast_chart() - Main time series chart
│   ├── render_forecast_statistics() - KPI cards
│   ├── render_aggregated_forecast() - Monthly/yearly charts
│   └── render_forecast_table() - Data table display
```

### Data Flow

1. **Data Loading**: Invoice CSV → DataLoader → DataTransformer
2. **Time Series Preparation**:
   - Group by invoice_date
   - Sum total_amount per day
   - Fill missing dates with 0
   - Create continuous time series
3. **Model Loading**: Load ARIMA model from pickle file (cached)
4. **Forecast Generation**:
   - Call `model.forecast(steps=N)`
   - Create date range for forecast period
   - Calculate statistics (mean, sum, std, min, max)
5. **Visualization**:
   - Historical + forecast line chart
   - Aggregated bar charts (monthly, yearly)
   - Statistics dashboard
   - Data tables

### Performance Optimizations

- **Model Caching**: `@st.cache_resource` prevents repeated model loading
- **Data Caching**: Reuses DataTransformer from main dashboard
- **Efficient Aggregation**: Pandas resampling for monthly/yearly views
- **Lazy Rendering**: Charts render only when visible

---

## Example Workflow

### Scenario: Q1 2022 Budget Planning

**Step 1: Access Forecasting Tab**
- Navigate to "Revenue Forecasting" tab

**Step 2: Configure Forecast**
- Forecast Horizon: "Next 90 Days"
- Historical Data: "Last 1 Year"

**Step 3: Review Statistics**
- Total Forecasted Revenue: ~$12,581
- Average Daily Revenue: ~$140
- Note: Based on 52-year historical average

**Step 4: Analyze Visualizations**
- Main chart shows historical volatility vs. stable forecast
- Monthly aggregation shows ~$4,194 per month
- Q1 projection: ~$12,581 total revenue

**Step 5: Download Data** (Future Enhancement)
- Export forecast table to CSV
- Share with finance team
- Import into budgeting software

**Step 6: Compare with Actuals** (Future Enhancement)
- Track actual Q1 revenue
- Calculate variance from forecast
- Identify opportunities for model improvement

---

## Future Enhancements

### Planned Features

1. **Advanced Models**:
   - SARIMA for seasonal patterns
   - Prophet for trend + seasonality
   - Multiple model comparison

2. **Confidence Intervals**:
   - Upper and lower bounds
   - Probability distributions
   - Risk assessment metrics

3. **Scenario Analysis**:
   - Best case / worst case scenarios
   - What-if analysis
   - Parameter sensitivity

4. **Export Functionality**:
   - CSV/Excel download
   - PDF reports
   - API integration

5. **Model Retraining**:
   - Update model with new data
   - Automatic retraining schedule
   - Model version tracking

6. **Custom Filters**:
   - Product-specific forecasts
   - Customer segment forecasts
   - Regional forecasts

---

## Troubleshooting

### Model Not Loading
**Issue**: Error message "ARIMA model file not found"

**Solution**:
1. Verify `arima_final_model.pkl` exists in project root
2. Check file permissions
3. Ensure statsmodels is installed: `pip install statsmodels>=0.14.0`

### Forecast Generation Failed
**Issue**: Empty forecast or error during generation

**Solution**:
1. Check historical data is loaded correctly
2. Verify date range is valid
3. Ensure forecast steps > 0
4. Check console for detailed error messages

### Visualization Issues
**Issue**: Charts not displaying or rendering incorrectly

**Solution**:
1. Verify Plotly is installed: `pip install plotly>=5.17.0`
2. Clear browser cache
3. Try different browser
4. Check streamlit version: `streamlit --version`

### Performance Issues
**Issue**: Slow forecast generation for large horizons

**Solution**:
1. Model loading is cached (should be fast after first load)
2. Reduce historical data display points
3. Consider using aggregated views (monthly/yearly)
4. For very long forecasts (1000+ days), expect 2-3 second delay

---

## API Reference

### ForecastingComponents Class Methods

#### `load_arima_model(model_path: str)`
Loads ARIMA model from pickle file with caching.

**Parameters:**
- `model_path` (str): Path to .pkl file

**Returns:**
- Fitted ARIMA model or None on error

#### `prepare_historical_data(df: pd.DataFrame) -> pd.Series`
Prepares daily aggregated revenue time series.

**Parameters:**
- `df` (pd.DataFrame): Raw invoice data

**Returns:**
- pd.Series: Daily revenue time series with date index

#### `generate_forecast(model, steps: int, last_date: pd.Timestamp) -> Tuple[pd.DataFrame, Dict]`
Generates forecast for specified number of days.

**Parameters:**
- `model`: Fitted ARIMA model
- `steps` (int): Number of days to forecast
- `last_date` (pd.Timestamp): Last historical date

**Returns:**
- Tuple[pd.DataFrame, Dict]: Forecast dataframe and statistics

#### `render_forecast_chart(...)`
Renders interactive Plotly forecast chart.

**Parameters:**
- `historical_series` (pd.Series): Historical daily revenue
- `forecast_df` (pd.DataFrame): Forecast data
- `title` (str): Chart title
- `show_historical_points` (int): Number of historical days to display

#### `render_forecast_statistics(stats: Dict, horizon_days: int)`
Displays forecast statistics in KPI cards.

#### `render_aggregated_forecast(forecast_df: pd.DataFrame, aggregation: str)`
Renders monthly ('M') or yearly ('Y') aggregated forecast bar chart.

#### `render_forecast_table(forecast_df: pd.DataFrame, num_rows: int)`
Displays forecast data in table format.

---

## Contact & Support

For questions or issues with the forecasting feature:

1. Check this documentation
2. Review the troubleshooting section
3. Examine the test script: `test_forecasting.py`
4. Review the model training notebook: `Invoice_Analysis.ipynb`

---

**Last Updated**: 2026-01-09
**Version**: 1.0.0
**Model**: ARIMA(0,0,0)
