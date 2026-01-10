"""
LSTM Forecasting Visualization Module

This module handles LSTM model forecasting visualization with Power BI theme.

Features:
---------
- Load trained LSTM model from .h5 file
- Generate forecasts for various time horizons (days, months, years)
- Visualize historical data + LSTM forecasts
- Compare LSTM predictions with ARIMA predictions
- Power BI black and yellow theme
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from typing import Tuple, Dict, Optional
import streamlit as st
from datetime import datetime, timedelta


class LSTMForecastingComponents:
    """
    Visualization components for LSTM forecasting with Power BI theme.
    """

    # Power BI Color Scheme
    COLORS = {
        'background': '#1C1C1C',
        'grid': '#404040',
        'historical': '#FFC000',  # Power BI Yellow
        'lstm_forecast': '#FF6B9D',  # Pink for LSTM forecast
        'arima_forecast': '#4ECDC4',  # Teal for ARIMA (to compare)
        'confidence': '#FFB3D1',  # Light pink for confidence interval
        'text': '#FFFFFF'
    }

    @staticmethod
    @st.cache_resource
    def load_lstm_model(model_path: str):
        """
        Load LSTM model from .h5 file with caching.

        Args:
            model_path (str): Path to .h5 model file

        Returns:
            Loaded Keras/TensorFlow model
        """
        try:
            from tensorflow import keras
            model = keras.models.load_model(model_path)
            return model
        except Exception as e:
            st.error(f"Error loading LSTM model: {str(e)}")
            return None

    @staticmethod
    def prepare_lstm_sequences(
        series: pd.Series,
        look_back: int = 60
    ) -> Tuple[np.ndarray, np.ndarray, float, float]:
        """
        Prepare sequences for LSTM prediction with normalization.

        Args:
            series (pd.Series): Time series data
            look_back (int): Number of time steps to look back

        Returns:
            Tuple of (X_sequences, dates, min_val, max_val)
        """
        values = series.values.reshape(-1, 1)

        # Normalize the data (min-max scaling)
        min_val = values.min()
        max_val = values.max()
        normalized_values = (values - min_val) / (max_val - min_val)

        # Create sequences
        X = []
        for i in range(len(normalized_values) - look_back):
            X.append(normalized_values[i:i + look_back])

        X = np.array(X)

        return X, series.index[look_back:], min_val, max_val

    @staticmethod
    def generate_lstm_forecast(
        model,
        historical_series: pd.Series,
        steps: int,
        look_back: int = 60
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Generate LSTM forecast for specified number of steps.

        Args:
            model: Loaded LSTM model
            historical_series (pd.Series): Historical time series data
            steps (int): Number of days to forecast
            look_back (int): Number of time steps for LSTM input

        Returns:
            Tuple[pd.DataFrame, Dict]: Forecast dataframe and statistics
        """
        try:
            # Prepare the data
            values = historical_series.values.reshape(-1, 1)

            # Normalize
            min_val = values.min()
            max_val = values.max()
            normalized_values = (values - min_val) / (max_val - min_val)

            # Get the last sequence for prediction
            last_sequence = normalized_values[-look_back:].reshape(1, look_back, 1)

            # Generate predictions
            predictions = []
            current_sequence = last_sequence.copy()

            for _ in range(steps):
                # Predict next value
                pred = model.predict(current_sequence, verbose=0)
                predictions.append(pred[0, 0])

                # Update sequence for next prediction
                current_sequence = np.append(current_sequence[:, 1:, :],
                                           pred.reshape(1, 1, 1), axis=1)

            # Denormalize predictions
            predictions = np.array(predictions)
            predictions = predictions * (max_val - min_val) + min_val

            # Create forecast dates
            last_date = historical_series.index[-1]
            forecast_dates = pd.date_range(
                start=last_date + timedelta(days=1),
                periods=steps,
                freq='D'
            )

            # Create forecast dataframe
            forecast_df = pd.DataFrame({
                'date': forecast_dates,
                'forecast': predictions.flatten()
            })

            # Calculate statistics
            stats = {
                'mean_forecast': predictions.mean(),
                'total_forecast': predictions.sum(),
                'min_forecast': predictions.min(),
                'max_forecast': predictions.max(),
                'std_forecast': predictions.std()
            }

            return forecast_df, stats

        except Exception as e:
            st.error(f"Error generating LSTM forecast: {str(e)}")
            return pd.DataFrame(), {}

    @staticmethod
    def render_lstm_forecast_chart(
        historical_series: pd.Series,
        lstm_forecast_df: pd.DataFrame,
        arima_forecast_df: Optional[pd.DataFrame] = None,
        title: str = "LSTM Revenue Forecast",
        show_historical_points: int = 365
    ) -> None:
        """
        Render interactive LSTM forecast chart with optional ARIMA comparison.

        Args:
            historical_series (pd.Series): Historical daily revenue
            lstm_forecast_df (pd.DataFrame): LSTM forecast dataframe
            arima_forecast_df (pd.DataFrame): Optional ARIMA forecast for comparison
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
            line=dict(color=LSTMForecastingComponents.COLORS['historical'], width=2),
            hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                          '<b>Revenue:</b> $%{y:,.2f}<br>' +
                          '<extra></extra>'
        ))

        # Add LSTM forecast trace
        if not lstm_forecast_df.empty:
            fig.add_trace(go.Scatter(
                x=lstm_forecast_df['date'],
                y=lstm_forecast_df['forecast'],
                mode='lines+markers',
                name='LSTM Forecast',
                line=dict(color=LSTMForecastingComponents.COLORS['lstm_forecast'],
                         width=3, dash='dash'),
                marker=dict(size=6, symbol='circle'),
                hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                              '<b>LSTM Forecast:</b> $%{y:,.2f}<br>' +
                              '<extra></extra>'
            ))

        # Add ARIMA forecast trace for comparison if provided
        if arima_forecast_df is not None and not arima_forecast_df.empty:
            fig.add_trace(go.Scatter(
                x=arima_forecast_df['date'],
                y=arima_forecast_df['forecast'],
                mode='lines+markers',
                name='ARIMA Forecast (Comparison)',
                line=dict(color=LSTMForecastingComponents.COLORS['arima_forecast'],
                         width=2, dash='dot'),
                marker=dict(size=4, symbol='diamond'),
                hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                              '<b>ARIMA Forecast:</b> $%{y:,.2f}<br>' +
                              '<extra></extra>'
            ))

        # Update layout with Power BI theme
        fig.update_layout(
            title={
                'text': title,
                'font': {'size': 20, 'color': LSTMForecastingComponents.COLORS['text'],
                        'family': 'Arial Black'},
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis=dict(
                title='Date',
                gridcolor=LSTMForecastingComponents.COLORS['grid'],
                color=LSTMForecastingComponents.COLORS['text'],
                showgrid=True,
                zeroline=False
            ),
            yaxis=dict(
                title='Daily Revenue ($)',
                gridcolor=LSTMForecastingComponents.COLORS['grid'],
                color=LSTMForecastingComponents.COLORS['text'],
                showgrid=True,
                zeroline=False,
                tickformat='$,.0f'
            ),
            plot_bgcolor=LSTMForecastingComponents.COLORS['background'],
            paper_bgcolor=LSTMForecastingComponents.COLORS['background'],
            font=dict(color=LSTMForecastingComponents.COLORS['text']),
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                bgcolor='rgba(0,0,0,0.5)',
                bordercolor=LSTMForecastingComponents.COLORS['grid'],
                borderwidth=1,
                font=dict(color=LSTMForecastingComponents.COLORS['text'])
            ),
            height=500,
            margin=dict(l=60, r=40, t=80, b=60)
        )

        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def render_lstm_forecast_statistics(
        lstm_stats: Dict,
        arima_stats: Optional[Dict],
        horizon_days: int
    ) -> None:
        """
        Render LSTM forecast statistics with optional ARIMA comparison.

        Args:
            lstm_stats (Dict): LSTM forecast statistics
            arima_stats (Dict): Optional ARIMA statistics for comparison
            horizon_days (int): Number of days forecasted
        """
        st.markdown("### 📊 LSTM Forecast Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Forecast Period",
                f"{horizon_days} days"
            )

        with col2:
            lstm_total = lstm_stats.get('total_forecast', 0)
            if arima_stats:
                arima_total = arima_stats.get('total_forecast', 0)
                delta = lstm_total - arima_total
                delta_pct = (delta / arima_total * 100) if arima_total != 0 else 0
                st.metric(
                    "Total Forecasted Revenue (LSTM)",
                    f"${lstm_total:,.2f}",
                    delta=f"${delta:,.2f} vs ARIMA ({delta_pct:+.1f}%)"
                )
            else:
                st.metric(
                    "Total Forecasted Revenue (LSTM)",
                    f"${lstm_total:,.2f}"
                )

        with col3:
            lstm_mean = lstm_stats.get('mean_forecast', 0)
            if arima_stats:
                arima_mean = arima_stats.get('mean_forecast', 0)
                delta = lstm_mean - arima_mean
                delta_pct = (delta / arima_mean * 100) if arima_mean != 0 else 0
                st.metric(
                    "Avg Daily Revenue (LSTM)",
                    f"${lstm_mean:,.2f}",
                    delta=f"${delta:,.2f} vs ARIMA ({delta_pct:+.1f}%)"
                )
            else:
                st.metric(
                    "Avg Daily Revenue (LSTM)",
                    f"${lstm_mean:,.2f}"
                )

        with col4:
            st.metric(
                "Std Deviation (LSTM)",
                f"${lstm_stats.get('std_forecast', 0):,.2f}"
            )

        # Comparison section if ARIMA stats are provided
        if arima_stats:
            st.markdown("---")
            st.markdown("### 🔄 LSTM vs ARIMA Comparison")

            comp_col1, comp_col2, comp_col3 = st.columns(3)

            with comp_col1:
                lstm_total = lstm_stats.get('total_forecast', 0)
                arima_total = arima_stats.get('total_forecast', 0)
                diff = lstm_total - arima_total
                diff_pct = (diff / arima_total * 100) if arima_total != 0 else 0

                st.markdown(f"""
                **Total Revenue Difference:**
                - **LSTM:** ${lstm_total:,.2f}
                - **ARIMA:** ${arima_total:,.2f}
                - **Difference:** ${diff:,.2f} ({diff_pct:+.1f}%)
                """)

            with comp_col2:
                lstm_mean = lstm_stats.get('mean_forecast', 0)
                arima_mean = arima_stats.get('mean_forecast', 0)
                diff = lstm_mean - arima_mean
                diff_pct = (diff / arima_mean * 100) if arima_mean != 0 else 0

                st.markdown(f"""
                **Average Daily Revenue Difference:**
                - **LSTM:** ${lstm_mean:,.2f}
                - **ARIMA:** ${arima_mean:,.2f}
                - **Difference:** ${diff:,.2f} ({diff_pct:+.1f}%)
                """)

            with comp_col3:
                lstm_std = lstm_stats.get('std_forecast', 0)
                arima_std = arima_stats.get('std_forecast', 0)

                st.markdown(f"""
                **Variability Comparison:**
                - **LSTM Std Dev:** ${lstm_std:,.2f}
                - **ARIMA Std Dev:** ${arima_std:,.2f}
                - **LSTM shows {'more' if lstm_std > arima_std else 'less'} variability**
                """)

    @staticmethod
    def render_aggregated_lstm_forecast(
        forecast_df: pd.DataFrame,
        aggregation: str = 'M'
    ) -> None:
        """
        Render aggregated LSTM forecast (monthly or yearly).

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
            name=f'{period_label}ly LSTM Forecast',
            marker=dict(
                color=LSTMForecastingComponents.COLORS['lstm_forecast'],
                line=dict(color=LSTMForecastingComponents.COLORS['text'], width=1)
            ),
            hovertemplate=f'<b>{period_label}:</b> %{{x|{date_format}}}<br>' +
                          '<b>Total Revenue:</b> $%{y:,.2f}<br>' +
                          '<extra></extra>'
        ))

        # Update layout
        fig.update_layout(
            title={
                'text': f'{period_label}ly LSTM Revenue Forecast',
                'font': {'size': 18, 'color': LSTMForecastingComponents.COLORS['text']},
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis=dict(
                title=period_label,
                gridcolor=LSTMForecastingComponents.COLORS['grid'],
                color=LSTMForecastingComponents.COLORS['text']
            ),
            yaxis=dict(
                title='Total Revenue ($)',
                gridcolor=LSTMForecastingComponents.COLORS['grid'],
                color=LSTMForecastingComponents.COLORS['text'],
                tickformat='$,.0f'
            ),
            plot_bgcolor=LSTMForecastingComponents.COLORS['background'],
            paper_bgcolor=LSTMForecastingComponents.COLORS['background'],
            font=dict(color=LSTMForecastingComponents.COLORS['text']),
            height=400,
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def render_lstm_forecast_table(forecast_df: pd.DataFrame, num_rows: int = 10) -> None:
        """
        Render LSTM forecast data table.

        Args:
            forecast_df (pd.DataFrame): Forecast data
            num_rows (int): Number of rows to display
        """
        if forecast_df.empty:
            return

        st.markdown("### 📋 LSTM Forecast Data Table")

        # Format the dataframe for display
        display_df = forecast_df.copy()
        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
        display_df['forecast'] = display_df['forecast'].apply(lambda x: f"${x:,.2f}")
        display_df.columns = ['Date', 'LSTM Forecasted Revenue']

        # Show first and last rows
        st.markdown(f"**First {num_rows} Days:**")
        st.dataframe(display_df.head(num_rows), use_container_width=True, hide_index=True)

        if len(display_df) > num_rows:
            st.markdown(f"**Last {num_rows} Days:**")
            st.dataframe(display_df.tail(num_rows), use_container_width=True, hide_index=True)
