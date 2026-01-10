"""
Forecasting Visualization Module

This module handles ARIMA model forecasting visualization with Power BI theme.

Features:
---------
- Load trained ARIMA model from pickle file
- Generate forecasts for various time horizons (days, months, years)
- Visualize historical data + forecasts
- Power BI black and yellow theme
"""

import pickle
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from typing import Tuple, Dict
import streamlit as st
from datetime import datetime, timedelta


class ForecastingComponents:
    """
    Visualization components for ARIMA forecasting with Power BI theme.
    """

    # Power BI Color Scheme
    COLORS = {
        'background': '#1C1C1C',
        'grid': '#404040',
        'historical': '#FFC000',  # Power BI Yellow
        'forecast': '#4ECDC4',     # Teal for forecast
        'confidence': '#95E1D3',   # Light teal for confidence interval
        'text': '#FFFFFF'
    }

    @staticmethod
    @st.cache_resource
    def load_arima_model(model_path: str):
        """
        Load ARIMA model from pickle file with caching.

        Args:
            model_path (str): Path to pickle file

        Returns:
            Fitted ARIMA model
        """
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            return model
        except Exception as e:
            st.error(f"Error loading ARIMA model: {str(e)}")
            return None

    @staticmethod
    def prepare_historical_data(df: pd.DataFrame) -> pd.Series:
        """
        Prepare daily aggregated revenue data for forecasting.

        Args:
            df (pd.DataFrame): Raw invoice data

        Returns:
            pd.Series: Time series of daily total revenue
        """
        # Ensure invoice_date is datetime
        if not pd.api.types.is_datetime64_any_dtype(df['invoice_date']):
            df = df.copy()
            df['invoice_date'] = pd.to_datetime(df['invoice_date'], format='%d/%m/%Y')

        # Calculate total_amount if not present
        if 'total_amount' not in df.columns:
            df = df.copy()
            df['total_amount'] = df['qty'] * df['amount']

        # Aggregate by date
        daily_data = df.groupby('invoice_date')['total_amount'].sum().reset_index()
        daily_data.columns = ['date', 'value']
        daily_data.set_index('date', inplace=True)

        # Create full date range with missing dates filled as 0
        full_range = pd.date_range(
            start=daily_data.index.min(),
            end=daily_data.index.max(),
            freq='D'
        )
        daily_data = daily_data.reindex(full_range, fill_value=0)

        return daily_data['value']

    @staticmethod
    def generate_forecast(
        model,
        steps: int,
        last_date: pd.Timestamp
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Generate forecast for specified number of steps.

        Args:
            model: Fitted ARIMA model
            steps (int): Number of days to forecast
            last_date (pd.Timestamp): Last date in historical data

        Returns:
            Tuple[pd.DataFrame, Dict]: Forecast dataframe and statistics
        """
        try:
            # Generate forecast
            forecast_result = model.forecast(steps=steps)

            # Create forecast dates
            forecast_dates = pd.date_range(
                start=last_date + timedelta(days=1),
                periods=steps,
                freq='D'
            )

            # Create forecast dataframe
            forecast_df = pd.DataFrame({
                'date': forecast_dates,
                'forecast': forecast_result
            })

            # Calculate statistics
            stats = {
                'mean_forecast': forecast_result.mean(),
                'total_forecast': forecast_result.sum(),
                'min_forecast': forecast_result.min(),
                'max_forecast': forecast_result.max(),
                'std_forecast': forecast_result.std()
            }

            return forecast_df, stats

        except Exception as e:
            st.error(f"Error generating forecast: {str(e)}")
            return pd.DataFrame(), {}

    @staticmethod
    def render_forecast_chart(
        historical_series: pd.Series,
        forecast_df: pd.DataFrame,
        title: str = "Revenue Forecast",
        show_historical_points: int = 365
    ) -> None:
        """
        Render interactive forecast chart with historical data.

        Args:
            historical_series (pd.Series): Historical daily revenue
            forecast_df (pd.DataFrame): Forecast dataframe with 'date' and 'forecast'
            title (str): Chart title
            show_historical_points (int): Number of historical days to show
        """
        fig = go.Figure()

        # Filter historical data to last N days for better visibility
        if len(historical_series) > show_historical_points:
            historical_series = historical_series.iloc[-show_historical_points:]

        # Add historical data trace
        fig.add_trace(go.Scatter(
            x=historical_series.index,
            y=historical_series.values,
            mode='lines',
            name='Historical Revenue',
            line=dict(color=ForecastingComponents.COLORS['historical'], width=2),
            hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                          '<b>Revenue:</b> $%{y:,.2f}<br>' +
                          '<extra></extra>'
        ))

        # Add forecast trace
        if not forecast_df.empty:
            fig.add_trace(go.Scatter(
                x=forecast_df['date'],
                y=forecast_df['forecast'],
                mode='lines+markers',
                name='Forecast',
                line=dict(color=ForecastingComponents.COLORS['forecast'], width=3, dash='dash'),
                marker=dict(size=6, symbol='diamond'),
                hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                              '<b>Forecast:</b> $%{y:,.2f}<br>' +
                              '<extra></extra>'
            ))

        # Update layout with Power BI theme
        fig.update_layout(
            title={
                'text': title,
                'font': {'size': 20, 'color': ForecastingComponents.COLORS['text'], 'family': 'Arial Black'},
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis=dict(
                title='Date',
                gridcolor=ForecastingComponents.COLORS['grid'],
                color=ForecastingComponents.COLORS['text'],
                showgrid=True,
                zeroline=False
            ),
            yaxis=dict(
                title='Daily Revenue ($)',
                gridcolor=ForecastingComponents.COLORS['grid'],
                color=ForecastingComponents.COLORS['text'],
                showgrid=True,
                zeroline=False,
                tickformat='$,.0f'
            ),
            plot_bgcolor=ForecastingComponents.COLORS['background'],
            paper_bgcolor=ForecastingComponents.COLORS['background'],
            font=dict(color=ForecastingComponents.COLORS['text']),
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                bgcolor='rgba(0,0,0,0.5)',
                bordercolor=ForecastingComponents.COLORS['grid'],
                borderwidth=1,
                font=dict(color=ForecastingComponents.COLORS['text'])
            ),
            height=500,
            margin=dict(l=60, r=40, t=80, b=60)
        )

        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def render_forecast_statistics(stats: Dict, horizon_days: int) -> None:
        """
        Render forecast statistics in KPI cards.

        Args:
            stats (Dict): Forecast statistics
            horizon_days (int): Number of days forecasted
        """
        st.markdown("### 📊 Forecast Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Forecast Period",
                f"{horizon_days} days"
            )

        with col2:
            st.metric(
                "Total Forecasted Revenue",
                f"${stats.get('total_forecast', 0):,.2f}"
            )

        with col3:
            st.metric(
                "Avg Daily Revenue",
                f"${stats.get('mean_forecast', 0):,.2f}"
            )

        with col4:
            st.metric(
                "Std Deviation",
                f"${stats.get('std_forecast', 0):,.2f}"
            )

        # Additional statistics in expandable section
        with st.expander("📈 Detailed Statistics"):
            detail_col1, detail_col2 = st.columns(2)

            with detail_col1:
                st.markdown(f"""
                **Range Statistics:**
                - **Minimum Daily Revenue:** ${stats.get('min_forecast', 0):,.2f}
                - **Maximum Daily Revenue:** ${stats.get('max_forecast', 0):,.2f}
                """)

            with detail_col2:
                st.markdown(f"""
                **Model Information:**
                - **Model Type:** ARIMA(0,0,0)
                - **Training Data:** 19,006 observations
                - **Date Range:** 1970-2022
                """)

    @staticmethod
    def render_aggregated_forecast(
        forecast_df: pd.DataFrame,
        aggregation: str = 'M'
    ) -> None:
        """
        Render aggregated forecast (monthly or yearly).

        Args:
            forecast_df (pd.DataFrame): Daily forecast data
            aggregation (str): 'M' for monthly, 'Y' for yearly
        """
        if forecast_df.empty:
            return

        # Set date as index for resampling
        df_temp = forecast_df.set_index('date')

        # Aggregate based on period
        if aggregation == 'M':
            agg_data = df_temp.resample('ME').sum()
            period_label = "Month"
            date_format = "%B %Y"
        elif aggregation == 'Y':
            agg_data = df_temp.resample('YE').sum()
            period_label = "Year"
            date_format = "%Y"
        else:
            return

        # Create bar chart
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=agg_data.index,
            y=agg_data['forecast'],
            name=f'{period_label}ly Forecast',
            marker=dict(
                color=ForecastingComponents.COLORS['forecast'],
                line=dict(color=ForecastingComponents.COLORS['text'], width=1)
            ),
            hovertemplate=f'<b>{period_label}:</b> %{{x|{date_format}}}<br>' +
                          '<b>Total Revenue:</b> $%{y:,.2f}<br>' +
                          '<extra></extra>'
        ))

        # Update layout
        fig.update_layout(
            title={
                'text': f'{period_label}ly Revenue Forecast',
                'font': {'size': 18, 'color': ForecastingComponents.COLORS['text']},
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis=dict(
                title=period_label,
                gridcolor=ForecastingComponents.COLORS['grid'],
                color=ForecastingComponents.COLORS['text']
            ),
            yaxis=dict(
                title='Total Revenue ($)',
                gridcolor=ForecastingComponents.COLORS['grid'],
                color=ForecastingComponents.COLORS['text'],
                tickformat='$,.0f'
            ),
            plot_bgcolor=ForecastingComponents.COLORS['background'],
            paper_bgcolor=ForecastingComponents.COLORS['background'],
            font=dict(color=ForecastingComponents.COLORS['text']),
            height=400,
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def render_forecast_table(forecast_df: pd.DataFrame, num_rows: int = 10) -> None:
        """
        Render forecast data table.

        Args:
            forecast_df (pd.DataFrame): Forecast data
            num_rows (int): Number of rows to display
        """
        if forecast_df.empty:
            return

        st.markdown("### 📋 Forecast Data Table")

        # Format the dataframe for display
        display_df = forecast_df.copy()
        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
        display_df['forecast'] = display_df['forecast'].apply(lambda x: f"${x:,.2f}")
        display_df.columns = ['Date', 'Forecasted Revenue']

        # Show first and last rows
        st.markdown(f"**First {num_rows} Days:**")
        st.dataframe(display_df.head(num_rows), use_container_width=True, hide_index=True)

        if len(display_df) > num_rows:
            st.markdown(f"**Last {num_rows} Days:**")
            st.dataframe(display_df.tail(num_rows), use_container_width=True, hide_index=True)
