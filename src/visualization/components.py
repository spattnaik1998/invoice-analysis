"""
Dashboard Components Module

This module contains reusable visualization components for the dashboard.
Responsible for:
- Chart rendering functions
- KPI card components
- Filter components
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Optional


class DashboardComponents:
    """
    Reusable visualization components for the Invoice Analytics Dashboard.

    This class provides static methods for rendering various charts,
    KPI cards, and dashboard components using Streamlit and Plotly.
    """

    @staticmethod
    def render_kpi_card(
        title: str,
        value: float,
        format_string: str = "{:,.2f}",
        delta: Optional[float] = None,
        delta_color: str = "normal"
    ) -> None:
        """
        Render a KPI metric card.

        Args:
            title (str): KPI title
            value (float): KPI value
            format_string (str): Format string for value display
            delta (Optional[float]): Percentage change from previous period
            delta_color (str): Color scheme for delta ("normal", "inverse", "off")
        """
        formatted_value = format_string.format(value)

        if delta is not None:
            st.metric(
                label=title,
                value=formatted_value,
                delta=f"{delta:+.2f}%",
                delta_color=delta_color
            )
        else:
            st.metric(label=title, value=formatted_value)

    @staticmethod
    def render_line_chart(
        data: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str,
        x_label: str,
        y_label: str,
        color: str = "#1F4E78"
    ) -> None:
        """
        Render an interactive line chart.

        Args:
            data (pd.DataFrame): Data to plot
            x_col (str): Column name for x-axis
            y_col (str): Column name for y-axis
            title (str): Chart title
            x_label (str): X-axis label
            y_label (str): Y-axis label
            color (str): Line color
        """
        fig = px.line(
            data,
            x=x_col,
            y=y_col,
            title=title,
            labels={x_col: x_label, y_col: y_label},
            markers=True
        )

        fig.update_traces(
            line_color=color,
            line_width=2,
            marker=dict(size=8)
        )

        fig.update_layout(
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12),
            title_font_size=16,
            xaxis=dict(showgrid=True, gridcolor='lightgray'),
            yaxis=dict(showgrid=True, gridcolor='lightgray')
        )

        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def render_bar_chart(
        data: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str,
        x_label: str,
        y_label: str,
        orientation: str = 'h',
        color_scale: str = 'Blues'
    ) -> None:
        """
        Render an interactive bar chart.

        Args:
            data (pd.DataFrame): Data to plot
            x_col (str): Column name for x-axis
            y_col (str): Column name for y-axis
            title (str): Chart title
            x_label (str): X-axis label
            y_label (str): Y-axis label
            orientation (str): 'h' for horizontal, 'v' for vertical
            color_scale (str): Plotly color scale name
        """
        fig = px.bar(
            data,
            x=x_col if orientation == 'v' else y_col,
            y=y_col if orientation == 'v' else x_col,
            title=title,
            labels={x_col: x_label, y_col: y_label},
            orientation=orientation,
            color=y_col if orientation == 'v' else x_col,
            color_continuous_scale=color_scale
        )

        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12),
            title_font_size=16,
            xaxis=dict(showgrid=True, gridcolor='lightgray'),
            yaxis=dict(showgrid=True, gridcolor='lightgray'),
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def render_area_chart(
        data: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str,
        x_label: str,
        y_label: str,
        color: str = "#4A90E2"
    ) -> None:
        """
        Render an interactive area chart.

        Args:
            data (pd.DataFrame): Data to plot
            x_col (str): Column name for x-axis
            y_col (str): Column name for y-axis
            title (str): Chart title
            x_label (str): X-axis label
            y_label (str): Y-axis label
            color (str): Fill color
        """
        fig = px.area(
            data,
            x=x_col,
            y=y_col,
            title=title,
            labels={x_col: x_label, y_col: y_label}
        )

        fig.update_traces(
            line_color=color,
            fillcolor=color,
            opacity=0.6
        )

        fig.update_layout(
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12),
            title_font_size=16,
            xaxis=dict(showgrid=True, gridcolor='lightgray'),
            yaxis=dict(showgrid=True, gridcolor='lightgray')
        )

        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def render_heatmap(
        data: pd.DataFrame,
        title: str,
        x_label: str = "Product ID",
        y_label: str = "Year",
        color_scale: str = "Blues"
    ) -> None:
        """
        Render an interactive heatmap.

        Args:
            data (pd.DataFrame): Pivot table data
            title (str): Chart title
            x_label (str): X-axis label
            y_label (str): Y-axis label
            color_scale (str): Plotly color scale name
        """
        fig = go.Figure(data=go.Heatmap(
            z=data.values,
            x=data.columns,
            y=data.index,
            colorscale=color_scale,
            hoverongaps=False,
            hovertemplate='Product: %{x}<br>Year: %{y}<br>Revenue: $%{z:,.2f}<extra></extra>'
        ))

        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12),
            title_font_size=16
        )

        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def render_filters(
        available_years: List[int],
        available_products: List[int]
    ) -> tuple:
        """
        Render filter components in the sidebar.

        Args:
            available_years (List[int]): List of available years
            available_products (List[int]): List of available product IDs

        Returns:
            tuple: (selected_years, selected_products)
        """
        st.sidebar.header("Filters")

        # Year filter
        st.sidebar.subheader("Year Range")
        selected_years = st.sidebar.multiselect(
            "Select Years",
            options=available_years,
            default=available_years,
            help="Select one or more years to filter the data"
        )

        # Product filter
        st.sidebar.subheader("Products")
        selected_products = st.sidebar.multiselect(
            "Select Products",
            options=available_products,
            default=available_products,
            help="Select one or more product IDs to filter the data"
        )

        return selected_years, selected_products
