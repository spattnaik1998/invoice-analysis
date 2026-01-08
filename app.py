"""
Invoice Analytics Dashboard - Main Application

This is the main Streamlit application file that orchestrates the dashboard.

Technology Stack Justification:
------------------------------
Streamlit was chosen for this project because:

1. **Python-Native**: Seamlessly integrates with pandas for data transformation,
   leveraging the existing invoice_analysis.py exploration work.

2. **Rapid Development**: Built-in widgets, state management, and caching enable
   fast iteration when building features one at a time.

3. **Performance**: @st.cache_data decorator provides automatic optimization,
   meeting the PRD requirement of <3s initial load and <500ms filter updates.

4. **Interactive by Default**: All Plotly visualizations are interactive
   out-of-the-box with zoom, pan, and hover capabilities.

5. **Professional Quality**: Widely used in industry for data analytics dashboards,
   making it portfolio-worthy for recruiters and hiring managers.

6. **Easy Deployment**: Simple deployment to Streamlit Cloud, Docker, or
   cloud platforms without complex backend setup.

7. **Meets All PRD Requirements**: Handles multi-select filters, real-time KPI
   updates, and complex visualizations efficiently.

Architecture:
-------------
The application follows a clean three-layer architecture:

Layer 1 - Data Loading (src/data/data_loader.py):
    - Reads CSV files
    - Validates schema
    - Converts data types

Layer 2 - Data Transformation (src/data/data_transformer.py):
    - Creates derived fields
    - Handles filtering logic
    - Performs aggregations for visualizations

Layer 3 - Visualization (src/visualization/components.py + app.py):
    - Renders interactive charts using Plotly
    - Displays KPI cards
    - Manages user interface and filters
"""

import streamlit as st
from pathlib import Path
import sys

# Add src to Python path for imports
sys.path.append(str(Path(__file__).parent))

from src.data import DataLoader, DataTransformer
from src.visualization import DashboardComponents
from src.utils import format_currency, format_number
from config import APP_TITLE, APP_ICON, APP_LAYOUT, DATA_FILE


# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=APP_LAYOUT,
    initial_sidebar_state="expanded"
)


@st.cache_data(ttl=3600)
def load_and_prepare_data():
    """
    Load and prepare data with caching for performance.

    Returns:
        DataTransformer: Transformer instance with loaded data
    """
    loader = DataLoader(str(DATA_FILE))
    df = loader.load_data()
    transformer = DataTransformer(df)
    return transformer


def initialize_session_state():
    """
    Initialize session state for filter management.

    Session state variables:
    - selected_products_override: Override sidebar product filter (used for chart clicks)
    - filter_source: Track if filter came from 'sidebar' or 'chart_click'
    """
    if 'selected_products_override' not in st.session_state:
        st.session_state.selected_products_override = None
    if 'filter_source' not in st.session_state:
        st.session_state.filter_source = 'sidebar'


def main():
    """
    Main application function.
    """
    # Initialize session state for filter management
    initialize_session_state()

    # Header
    st.title(f"{APP_ICON} {APP_TITLE}")
    st.markdown(
        """
        Transform invoice data into actionable business intelligence.
        Use the filters in the sidebar to explore sales patterns, product performance, and revenue trends.
        """
    )

    # Load data
    try:
        with st.spinner("Loading invoice data..."):
            transformer = load_and_prepare_data()

        # Get available filter options
        available_years = transformer.get_available_years()
        available_products = transformer.get_available_products()

        # Render filters in sidebar
        selected_years, selected_products = DashboardComponents.render_filters(
            available_years,
            available_products
        )

        # Apply session state overrides from chart clicks
        if st.session_state.selected_products_override is not None:
            selected_products = st.session_state.selected_products_override

            # Show clear filter button
            if st.sidebar.button("🔄 Clear Product Filter", use_container_width=True):
                st.session_state.selected_products_override = None
                st.session_state.filter_source = 'sidebar'
                st.rerun()

        # Transaction Volume Aggregation Selector
        st.sidebar.markdown("---")
        st.sidebar.subheader("Transaction Volume")

        aggregation_level = st.sidebar.selectbox(
            "Aggregation Level",
            options=['Daily', 'Weekly', 'Monthly'],
            index=0,  # Default to Daily
            help="Select the time granularity for transaction volume analysis"
        )

        # Map display names to pandas frequency codes
        aggregation_map = {
            'Daily': 'D',
            'Weekly': 'W',
            'Monthly': 'M'
        }
        freq_code = aggregation_map[aggregation_level]

        # Validate filter selections
        if not selected_years:
            st.warning("Please select at least one year from the filters.")
            return

        if not selected_products:
            st.warning("Please select at least one product from the filters.")
            return

        # Apply filters
        filtered_transformer = transformer.filter_by_years(
            selected_years
        ).filter_by_products(selected_products)

        # Display data info in sidebar
        st.sidebar.markdown("---")
        st.sidebar.subheader("Dataset Info")
        kpis = filtered_transformer.get_kpis()
        st.sidebar.info(
            f"**Filtered Records:** {format_number(kpis['num_transactions'])}\n\n"
            f"**Unique Customers:** {format_number(kpis['unique_customers'])}\n\n"
            f"**Unique Products:** {format_number(kpis['unique_products'])}"
        )

        # KPI Section
        st.header("Key Performance Indicators")
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

        with kpi_col1:
            DashboardComponents.render_kpi_card(
                title="Total Revenue",
                value=kpis['total_revenue'],
                format_string="${:,.2f}"
            )

        with kpi_col2:
            DashboardComponents.render_kpi_card(
                title="Total Quantity Sold",
                value=kpis['total_quantity'],
                format_string="{:,.0f}"
            )

        with kpi_col3:
            DashboardComponents.render_kpi_card(
                title="Avg Transaction Value",
                value=kpis['avg_transaction_value'],
                format_string="${:,.2f}"
            )

        with kpi_col4:
            DashboardComponents.render_kpi_card(
                title="Number of Transactions",
                value=kpis['num_transactions'],
                format_string="{:,.0f}"
            )

        st.markdown("---")

        # Visualizations Section
        st.header("Visualizations")

        # Yearly Revenue Trend Chart
        st.subheader("📈 Yearly Revenue Trend")
        yearly_revenue_data = filtered_transformer.get_yearly_revenue()

        if not yearly_revenue_data.empty:
            DashboardComponents.render_revenue_trend_chart(
                data=yearly_revenue_data,
                x_col='invoice_year',
                y_col='total_revenue',
                title='Revenue Trend Over Time'
            )
        else:
            st.warning("No revenue data available for the selected filters.")

        st.markdown("---")

        # Yearly Quantity Sold Trend Chart
        st.subheader("📊 Yearly Quantity Sold Trend")
        yearly_quantity_data = filtered_transformer.get_yearly_quantity()

        if not yearly_quantity_data.empty:
            DashboardComponents.render_quantity_trend_chart(
                data=yearly_quantity_data,
                x_col='invoice_year',
                y_col='total_quantity',
                title='Quantity Sold Trend Over Time'
            )
        else:
            st.warning("No quantity data available for the selected filters.")

        st.markdown("---")

        # Top 10 Products by Revenue with Click-to-Filter
        st.subheader("🏆 Top 10 Products by Revenue")

        # User guidance
        st.info("💡 Click on any bar to filter the entire dashboard to that product. Use the sidebar button to clear the filter.")

        top_products_data = filtered_transformer.get_top_products(n=10)

        if not top_products_data.empty:
            event = DashboardComponents.render_top_products_bar_chart(
                data=top_products_data,
                title='Top 10 Products by Total Revenue'
            )

            # Handle click event
            if event and event.get('selection') and event['selection'].get('points'):
                points = event['selection']['points']
                if len(points) > 0:
                    try:
                        clicked_product_id = int(points[0]['customdata'][0])

                        # Update session state to filter by clicked product
                        st.session_state.selected_products_override = [clicked_product_id]
                        st.session_state.filter_source = 'chart_click'
                        st.rerun()
                    except (KeyError, IndexError, ValueError) as e:
                        st.error(f"Error processing click event: {e}")
        else:
            st.warning("No product data available for the selected filters.")

        st.markdown("---")

        # Product vs Year Revenue Heatmap
        st.subheader("🔥 Product Performance Heatmap")

        # User guidance
        st.info("💡 Explore revenue patterns across all products and years. Darker colors indicate higher revenue.")

        heatmap_data = filtered_transformer.get_product_year_heatmap_data()

        if not heatmap_data.empty:
            DashboardComponents.render_heatmap(
                data=heatmap_data,
                title='Revenue by Product and Year',
                x_label='Year',
                y_label='Product ID',
                color_scale='Blues'
            )
        else:
            st.warning("No heatmap data available for the selected filters.")

        st.markdown("---")

        # Daily Transaction Volume Chart
        st.subheader("📊 Transaction Volume Over Time")

        # User guidance
        st.info(
            f"💡 Viewing transaction volume at **{aggregation_level.lower()}** level. "
            "Use the aggregation selector in the sidebar to change granularity. "
            "Click and drag to zoom, double-click to reset."
        )

        # Get transaction volume data
        try:
            volume_data = filtered_transformer.get_transaction_volume(freq=freq_code)

            if not volume_data.empty:
                DashboardComponents.render_area_chart(
                    data=volume_data,
                    x_col='date',
                    y_col='volume',
                    title=f'{aggregation_level} Transaction Volume',
                    x_label='Date',
                    y_label='Number of Transactions',
                    color='#4A90E2'
                )

                # Show summary statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "Total Transactions",
                        f"{int(volume_data['volume'].sum()):,}",
                        help=f"Total transactions in the selected {aggregation_level.lower()} period"
                    )
                with col2:
                    st.metric(
                        f"Avg {aggregation_level} Volume",
                        f"{int(volume_data['volume'].mean()):,}",
                        help=f"Average transactions per {aggregation_level.lower()} period"
                    )
                with col3:
                    st.metric(
                        f"Peak {aggregation_level}",
                        f"{int(volume_data['volume'].max()):,}",
                        help=f"Highest transaction count in a {aggregation_level.lower()} period"
                    )
            else:
                st.warning("No transaction volume data available for the selected filters.")
        except Exception as e:
            st.error(f"Error generating transaction volume chart: {str(e)}")
            st.exception(e)

        st.markdown("---")

        # Placeholder for remaining visualizations
        st.info(
            """
            **Coming Soon:**
            - Product-Specific Performance Line Chart

            Features will be built one at a time in subsequent iterations.
            """
        )

    except FileNotFoundError as e:
        st.error(f"Error: {str(e)}")
        st.info(
            f"Please ensure that the invoices.csv file is located at: {DATA_FILE}"
        )
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.exception(e)


if __name__ == "__main__":
    main()
