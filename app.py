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


def main():
    """
    Main application function.
    """
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

        # Placeholder for future visualizations
        st.header("Visualizations")
        st.info(
            """
            **Coming Soon:**
            - Yearly Revenue Trend Line Chart
            - Yearly Quantity Sold Trend Line Chart
            - Top 10 Products by Revenue (Bar Chart)
            - Product Performance Heatmap
            - Daily Transaction Volume (Area Chart)
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
