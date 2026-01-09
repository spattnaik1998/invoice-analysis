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
        if data.empty:
            st.info("No data available for the selected filters")
            return

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
        if data.empty:
            st.info("No data available for the selected filters")
            return

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
        Render an interactive area chart with zoom and pan capabilities.

        This chart includes built-in interactivity for data exploration:
        - Click and drag to zoom into a region
        - Shift + drag to pan across the timeline
        - Double-click to reset to original view
        - Modebar tools for additional zoom/pan/reset options

        Args:
            data (pd.DataFrame): Data to plot
            x_col (str): Column name for x-axis
            y_col (str): Column name for y-axis
            title (str): Chart title
            x_label (str): X-axis label
            y_label (str): Y-axis label
            color (str): Fill color (default: #4A90E2 - light blue)
        """
        if data.empty:
            st.info("No data available for the selected filters")
            return

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
            opacity=0.6,
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Volume: %{y:,}<extra></extra>'
        )

        fig.update_layout(
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12),
            title_font_size=16,
            xaxis=dict(
                showgrid=True,
                gridcolor='lightgray',
                title=x_label,
                rangeslider=dict(visible=False)
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='lightgray',
                title=y_label,
                rangemode='tozero'
            ),
            dragmode='zoom',
            modebar=dict(
                orientation='h',
                bgcolor='rgba(255,255,255,0.7)',
                activecolor='#4A90E2'
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def render_heatmap(
        data: pd.DataFrame,
        title: str,
        x_label: str = "Year",
        y_label: str = "Product ID",
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
        if data.empty:
            st.info("No data available for the selected filters")
            return

        fig = go.Figure(data=go.Heatmap(
            z=data.values,
            x=data.columns,
            y=data.index,
            colorscale=color_scale,
            hoverongaps=False,
            hovertemplate='Year: %{x}<br>Product: %{y}<br>Revenue: $%{z:,.2f}<extra></extra>'
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
    def render_revenue_trend_chart(
        data: pd.DataFrame,
        x_col: str = 'invoice_year',
        y_col: str = 'total_revenue',
        title: str = 'Yearly Revenue Trend',
        color: str = "#FFC000"
    ) -> None:
        """
        Render an interactive revenue trend line chart optimized for time-series data.

        This chart follows time-series visualization best practices with Power BI black/yellow theme:
        - Clear temporal progression on x-axis
        - Appropriate formatting for currency values
        - Interactive tooltips with detailed information
        - Markers to highlight individual data points
        - Responsive design
        - Power BI dark theme with yellow accent

        Args:
            data (pd.DataFrame): Data with year and revenue columns
            x_col (str): Column name for x-axis (year). Defaults to 'invoice_year'
            y_col (str): Column name for y-axis (revenue). Defaults to 'total_revenue'
            title (str): Chart title
            color (str): Line color (default: Power BI yellow #FFC000)
        """
        # Handle empty data
        if data.empty:
            st.info("No data available for the selected filters")
            return

        # Create the line chart with custom hover template
        fig = px.line(
            data,
            x=x_col,
            y=y_col,
            title=title,
            markers=True
        )

        # Update traces for Power BI style visualization
        fig.update_traces(
            line_color=color,
            line_width=4,
            marker=dict(size=12, line=dict(width=2, color='#000000')),
            hovertemplate='<b>Year: %{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>'
        )

        # Update layout for Power BI black/yellow theme
        fig.update_layout(
            hovermode='x unified',
            plot_bgcolor='#1C1C1C',
            paper_bgcolor='#000000',
            font=dict(family="Arial, sans-serif", size=12, color='#FFFFFF'),
            title_font=dict(size=20, color='#FFC000', family="Arial, sans-serif"),
            title_x=0.05,
            xaxis=dict(
                title="Year",
                title_font=dict(color='#FFC000', size=14),
                showgrid=True,
                gridcolor='#404040',
                gridwidth=1,
                dtick=1,  # Show every year
                tickmode='linear',
                tickfont=dict(color='#FFFFFF')
            ),
            yaxis=dict(
                title="Total Revenue ($)",
                title_font=dict(color='#FFC000', size=14),
                showgrid=True,
                gridcolor='#404040',
                gridwidth=1,
                tickformat='$,.0f',  # Format as currency
                rangemode='tozero',  # Start from zero for revenue
                tickfont=dict(color='#FFFFFF')
            ),
            margin=dict(l=60, r=30, t=60, b=60),
            hoverlabel=dict(
                bgcolor='#2D2D2D',
                font_size=13,
                font_family="Arial, sans-serif",
                font_color='#FFFFFF'
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def render_quantity_trend_chart(
        data: pd.DataFrame,
        x_col: str = 'invoice_year',
        y_col: str = 'total_quantity',
        title: str = 'Yearly Quantity Sold Trend',
        color: str = "#FFD740"
    ) -> None:
        """
        Render an interactive quantity sold trend line chart optimized for time-series data.

        This chart follows time-series visualization best practices with Power BI black/yellow theme.
        Distinguished from revenue chart through a lighter yellow/amber color.

        Args:
            data (pd.DataFrame): Data with year and quantity columns
            x_col (str): Column name for x-axis (year). Defaults to 'invoice_year'
            y_col (str): Column name for y-axis (quantity). Defaults to 'total_quantity'
            title (str): Chart title
            color (str): Line color (default: Light yellow #FFD740 to distinguish from revenue)
        """
        # Handle empty data
        if data.empty:
            st.info("No data available for the selected filters")
            return

        # Create the line chart with custom hover template
        fig = px.line(
            data,
            x=x_col,
            y=y_col,
            title=title,
            markers=True
        )

        # Update traces for Power BI style visualization
        fig.update_traces(
            line_color=color,
            line_width=4,
            marker=dict(size=12, line=dict(width=2, color='#000000')),
            hovertemplate='<b>Year: %{x}</b><br>Quantity: %{y:,} units<extra></extra>'
        )

        # Update layout for Power BI black/yellow theme
        fig.update_layout(
            hovermode='x unified',
            plot_bgcolor='#1C1C1C',
            paper_bgcolor='#000000',
            font=dict(family="Arial, sans-serif", size=12, color='#FFFFFF'),
            title_font=dict(size=20, color='#FFC000', family="Arial, sans-serif"),
            title_x=0.05,
            xaxis=dict(
                title="Year",
                title_font=dict(color='#FFC000', size=14),
                showgrid=True,
                gridcolor='#404040',
                gridwidth=1,
                dtick=1,  # Show every year
                tickmode='linear',
                tickfont=dict(color='#FFFFFF')
            ),
            yaxis=dict(
                title="Total Quantity Sold (units)",
                title_font=dict(color='#FFC000', size=14),
                showgrid=True,
                gridcolor='#404040',
                gridwidth=1,
                tickformat=',',  # Format with thousand separators
                rangemode='tozero',  # Start from zero for quantity
                tickfont=dict(color='#FFFFFF')
            ),
            margin=dict(l=60, r=30, t=60, b=60),
            hoverlabel=dict(
                bgcolor='#2D2D2D',
                font_size=13,
                font_family="Arial, sans-serif",
                font_color='#FFFFFF'
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def render_top_products_bar_chart(
        data: pd.DataFrame,
        title: str = "Top 10 Products by Revenue"
    ) -> dict:
        """
        Render interactive horizontal bar chart for top products with click-to-filter.

        This chart displays the top products by revenue with horizontal bars,
        allowing users to click on any bar to filter the entire dashboard to that
        specific product. The chart includes:
        - Horizontal orientation for better readability
        - Color gradient based on revenue values
        - Custom tooltips with formatted currency
        - Click event support for interactive filtering

        Args:
            data (pd.DataFrame): DataFrame with columns [product_id, total_revenue]
            title (str): Chart title (default: "Top 10 Products by Revenue")

        Returns:
            dict: Event data from st.plotly_chart for click handling, or None if data is empty
        """
        if data.empty:
            st.info("No product data available for the selected filters")
            return None

        # Sort ascending for horizontal bar display (bottom to top)
        data = data.sort_values('total_revenue', ascending=True)

        # Format product_id as string for better display
        data['product_label'] = 'Product ' + data['product_id'].astype(str)

        # Create horizontal bar chart
        fig = px.bar(
            data,
            x='total_revenue',
            y='product_label',
            orientation='h',
            color='total_revenue',
            color_continuous_scale='Teal',
            title=title,
            labels={'total_revenue': 'Total Revenue ($)', 'product_label': 'Product'},
            custom_data=['product_id']
        )

        # Update traces with custom tooltip
        fig.update_traces(
            hovertemplate='<b>%{y}</b><br>Revenue: $%{x:,.2f}<extra></extra>',
            marker=dict(line=dict(width=0))
        )

        # Update layout
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12),
            title_font_size=16,
            xaxis=dict(
                showgrid=True,
                gridcolor='lightgray',
                tickformat='$,.0f'
            ),
            yaxis=dict(showgrid=False),
            showlegend=False,
            height=400
        )

        # Render with click event support
        event = st.plotly_chart(
            fig,
            use_container_width=True,
            key="top_products_chart",
            on_select="rerun"
        )

        return event

    @staticmethod
    def render_multi_product_line_chart(
        data: pd.DataFrame,
        title: str = "Product Performance Comparison",
        y_metric: str = 'revenue'
    ) -> None:
        """
        Render multi-product line chart with interactive legend.

        Each product is shown as a separate colored line. Users can click
        legend items to toggle products on/off for comparison.

        Args:
            data (pd.DataFrame): Multi-product data with columns:
                - invoice_year: X-axis values
                - product_id: Product identifier (creates separate traces)
                - revenue (or other metric): Y-axis values
            title (str): Chart title
            y_metric (str): Column name for Y-axis metric (default: 'revenue')
        """
        if data.empty:
            st.warning("No product performance data available.")
            return

        # Count unique products for warning
        num_products = data['product_id'].nunique()

        # Show warning if many products
        if num_products > 10:
            st.warning(
                f"⚠️ Displaying {num_products} products. "
                "Chart may be cluttered. Consider filtering to fewer products for clarity."
            )

        # Create multi-trace line chart
        fig = px.line(
            data,
            x='invoice_year',
            y=y_metric,
            color='product_id',
            title=title,
            labels={
                'invoice_year': 'Year',
                y_metric: 'Revenue ($)' if y_metric == 'revenue' else y_metric.title(),
                'product_id': 'Product ID'
            },
            markers=True
        )

        # Update traces for better visibility
        fig.update_traces(
            line=dict(width=2.5),
            marker=dict(size=8, line=dict(width=1.5, color='white')),
            hovertemplate='<b>Product %{fullData.name}</b><br>Year: %{x}<br>Revenue: $%{y:,.2f}<extra></extra>'
        )

        # Update layout
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12),
            title_font_size=16,
            xaxis=dict(
                showgrid=True,
                gridcolor='lightgray',
                title='Year',
                dtick=1
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='lightgray',
                title='Revenue ($)',
                tickformat='$,.0f',
                rangemode='tozero'
            ),
            hovermode='x unified',
            legend=dict(
                title='Product ID',
                orientation='v',
                yanchor='top',
                y=1,
                xanchor='left',
                x=1.02,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='lightgray',
                borderwidth=1
            ),
            legend_itemclick='toggle',
            legend_itemdoubleclick='toggleothers'
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

    @staticmethod
    def render_button_filters(
        transformer,
        available_years: List[int],
        available_products: List[int]
    ) -> tuple:
        """
        Render Power BI-style button filters in a horizontal filter bar.

        This method creates toggle button filters for years, products, and aggregation level,
        replacing the traditional dropdown filters with a more interactive button-based interface.

        Args:
            transformer: DataTransformer instance (used to get top products)
            available_years (List[int]): List of available years
            available_products (List[int]): List of available product IDs

        Returns:
            tuple: (selected_years, selected_products, aggregation_level)
        """
        # Initialize session state for button filters
        if 'selected_years' not in st.session_state:
            st.session_state.selected_years = available_years.copy()
        if 'selected_products' not in st.session_state:
            st.session_state.selected_products = available_products.copy()
        if 'aggregation_level' not in st.session_state:
            st.session_state.aggregation_level = 'Daily'
        if 'show_all_products' not in st.session_state:
            st.session_state.show_all_products = False

        # Filter Bar Container
        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)

        # === YEAR FILTER SECTION ===
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        year_count = len(st.session_state.selected_years)
        st.markdown(
            f'<div class="filter-section-label">Year Range <span class="filter-selection-count">({year_count} selected)</span></div>',
            unsafe_allow_html=True
        )

        # Year buttons - use columns for horizontal layout
        year_cols = st.columns([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2])

        # "All Years" button
        with year_cols[0]:
            if st.button("All Years", key="year_all_btn", use_container_width=True):
                st.session_state.selected_years = available_years.copy()
                st.rerun()

        # Individual year buttons (show up to 9 years inline)
        years_to_show = available_years[:9] if len(available_years) > 9 else available_years
        for idx, year in enumerate(years_to_show):
            with year_cols[idx + 1]:
                is_selected = year in st.session_state.selected_years
                button_label = f"✓ {year}" if is_selected else str(year)

                # Apply active styling via inline style hack
                if st.button(button_label, key=f"year_{year}", use_container_width=True):
                    if is_selected:
                        # Deselect
                        if len(st.session_state.selected_years) > 1:  # Keep at least one
                            st.session_state.selected_years.remove(year)
                            st.rerun()
                    else:
                        # Select
                        st.session_state.selected_years.append(year)
                        st.rerun()

        # Clear All Years button
        with year_cols[10]:
            clear_col1, clear_col2 = st.columns([1, 1])
            with clear_col1:
                if st.button("Clear All", key="year_clear", use_container_width=True):
                    # Keep at least one year selected
                    st.session_state.selected_years = [available_years[0]]
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")

        # === PRODUCT FILTER SECTION ===
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        product_count = len(st.session_state.selected_products)
        st.markdown(
            f'<div class="filter-section-label">Products <span class="filter-selection-count">({product_count} selected)</span></div>',
            unsafe_allow_html=True
        )

        # Get top products for display
        top_products = transformer.get_top_products_for_filter(n=15)
        display_products = available_products if st.session_state.show_all_products else top_products

        # Product buttons - 5 per row
        num_cols = 5
        num_products = len(display_products)
        num_rows = (num_products + num_cols - 1) // num_cols

        for row_idx in range(num_rows):
            prod_cols = st.columns(num_cols)
            start_idx = row_idx * num_cols
            end_idx = min(start_idx + num_cols, num_products)

            for col_idx, prod_idx in enumerate(range(start_idx, end_idx)):
                product_id = display_products[prod_idx]
                with prod_cols[col_idx]:
                    is_selected = product_id in st.session_state.selected_products
                    button_label = f"✓ {product_id}" if is_selected else f"{product_id}"

                    if st.button(button_label, key=f"prod_{product_id}", use_container_width=True):
                        if is_selected:
                            # Deselect
                            if len(st.session_state.selected_products) > 1:  # Keep at least one
                                st.session_state.selected_products.remove(product_id)
                                st.rerun()
                        else:
                            # Select
                            st.session_state.selected_products.append(product_id)
                            st.rerun()

        # Action buttons row
        action_cols = st.columns([1, 1, 1, 1, 1])
        with action_cols[0]:
            if st.button("All Products", key="prod_all_btn", use_container_width=True):
                st.session_state.selected_products = available_products.copy()
                st.rerun()

        with action_cols[1]:
            if st.button("Clear All", key="prod_clear", use_container_width=True):
                # Keep at least one product
                st.session_state.selected_products = [available_products[0]]
                st.rerun()

        with action_cols[2]:
            toggle_label = "Show Top 15" if st.session_state.show_all_products else "Show All Products"
            st.markdown('<div class="toggle-visibility-btn">', unsafe_allow_html=True)
            if st.button(toggle_label, key="prod_toggle", use_container_width=True):
                st.session_state.show_all_products = not st.session_state.show_all_products
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")

        # === AGGREGATION LEVEL SECTION ===
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.markdown(
            '<div class="filter-section-label">Transaction Volume Aggregation</div>',
            unsafe_allow_html=True
        )

        agg_cols = st.columns([1, 1, 1, 7])
        agg_options = ['Daily', 'Weekly', 'Monthly']

        for idx, option in enumerate(agg_options):
            with agg_cols[idx]:
                is_selected = st.session_state.aggregation_level == option
                button_label = f"✓ {option}" if is_selected else option

                if st.button(button_label, key=f"agg_{option}", use_container_width=True):
                    st.session_state.aggregation_level = option
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)  # Close filter-bar

        return (
            st.session_state.selected_years,
            st.session_state.selected_products,
            st.session_state.aggregation_level
        )
