"""
Invoice Analytics Dashboard - Main Application

This is the main Streamlit application file that orchestrates the dashboard with
Power BI-inspired black and yellow theme.

Features:
---------
- **Power BI-Style Button Filters**: Interactive toggle buttons for year, product,
  and aggregation level selection
- **Dynamic KPI Cards**: 7 key performance indicators that update based on filters
- **Revenue Trend Analysis**: Interactive line chart showing total revenue over time
- **Product Quantity Trends**: Interactive line chart showing quantity sold evolution
- **Black & Yellow Theme**: Professional Power BI-inspired color scheme

Technology Stack:
-----------------
- **Streamlit**: Python web framework for data applications
- **Plotly**: Interactive charting library with dark theme support
- **Pandas**: Data manipulation and aggregation
- **Python 3.x**: Core programming language

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
    - Displays KPI cards with Power BI theme
    - Manages button-based filters with toggle functionality

Color Scheme:
-------------
- Primary: Black (#000000)
- Accent: Power BI Yellow (#FFC000)
- Background: Dark Gray (#1C1C1C)
- Borders: Medium Gray (#404040)
- Text: White (#FFFFFF)
"""

import streamlit as st
from pathlib import Path
import sys
from typing import Optional

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
def load_and_prepare_data() -> DataTransformer:
    """
    Load and prepare data with caching for performance.

    Returns:
        DataTransformer: Transformer instance with loaded data
    """
    loader = DataLoader(str(DATA_FILE))
    df = loader.load_data()
    transformer = DataTransformer(df)
    return transformer


def initialize_session_state() -> None:
    """
    Initialize session state for filter management.

    Session state variables:
    - selected_years: List of selected years for filtering
    - selected_products: List of selected product IDs for filtering
    - aggregation_level: Time granularity for transaction volume ('Daily', 'Weekly', 'Monthly')
    - show_all_products: Boolean to toggle between top 15 and all products in filter
    - selected_products_override: Override filter bar product selection (used for chart clicks)
    - filter_source: Track if filter came from 'filter_bar' or 'chart_click'
    """
    # Note: selected_years, selected_products, aggregation_level, and show_all_products
    # are initialized in render_button_filters() with proper defaults based on available data.
    # We only initialize the override and tracking variables here.

    if 'selected_products_override' not in st.session_state:
        st.session_state.selected_products_override = None
    if 'filter_source' not in st.session_state:
        st.session_state.filter_source = 'filter_bar'


def inject_button_filter_css() -> None:
    """
    Inject custom CSS for Power BI-style toggle button filters.

    This function adds professional styling for filter buttons with:
    - Active/inactive states with visual distinction
    - Hover effects for better UX
    - Power BI black and yellow color scheme
    - Filter bar container styling
    """
    st.markdown("""
        <style>
        /* Filter Bar Container */
        .filter-bar {
            background: #000000;
            padding: 20px;
            border-radius: 8px;
            border: 2px solid #404040;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px rgba(255, 192, 0, 0.1);
        }

        /* Filter Section */
        .filter-section {
            margin-bottom: 16px;
        }

        .filter-section-label {
            font-size: 14px;
            font-weight: 700;
            color: #FFC000 !important;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Selection Counter */
        .filter-selection-count {
            font-size: 12px;
            color: #CCCCCC !important;
            font-style: italic;
            margin-left: 8px;
        }

        /* Adjust button base styles */
        div[data-testid="column"] > div > div > div > button {
            width: 100%;
            border-radius: 6px !important;
            padding: 8px 16px !important;
            font-weight: 500 !important;
            border: 2px solid #404040 !important;
            background: #2D2D2D !important;
            color: #FFFFFF !important;
            transition: all 0.2s ease !important;
            margin-bottom: 8px !important;
        }

        /* Selected button state (buttons with checkmark ✓) */
        div[data-testid="column"] > div > div > div > button:has-text("✓"),
        div[data-testid="column"] > div > div > div > button[aria-label*="✓"] {
            background: #FFC000 !important;
            border-color: #FFC000 !important;
            color: #000000 !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 8px rgba(255, 192, 0, 0.4) !important;
        }

        /* Button hover state */
        div[data-testid="column"] > div > div > div > button:hover {
            border-color: #FFC000 !important;
            background: #404040 !important;
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(255, 192, 0, 0.2) !important;
        }

        /* Selected button hover state */
        div[data-testid="column"] > div > div > div > button:hover:has-text("✓") {
            background: #FFD740 !important;
            border-color: #FFD740 !important;
        }

        /* Clear All Button Styling */
        .clear-all-btn > div > div > div > button {
            background: transparent !important;
            border: 2px solid #E74C3C !important;
            color: #E74C3C !important;
        }

        .clear-all-btn > div > div > div > button:hover {
            background: #E74C3C !important;
            color: white !important;
        }

        /* Show More/Less Button */
        .toggle-visibility-btn > div > div > div > button {
            background: transparent !important;
            border: 2px dashed #FFC000 !important;
            color: #FFC000 !important;
            font-weight: 600 !important;
        }

        .toggle-visibility-btn > div > div > div > button:hover {
            background: #FFC000 !important;
            color: #000000 !important;
            border-style: solid !important;
        }
        </style>
    """, unsafe_allow_html=True)


def render_section_header(icon: str, title: str, description: Optional[str] = None) -> None:
    """
    Render a consistent section header with icon and description.

    Args:
        icon (str): Emoji icon for the section
        title (str): Section title
        description (str, optional): Brief description of the section
    """
    st.markdown(f"## {icon} {title}")
    if description:
        st.markdown(f"*{description}*")
    st.markdown("")  # Add spacing


def main() -> None:
    """
    Main application function.
    """
    # Initialize session state for filter management
    initialize_session_state()

    # Custom CSS for Power BI black and yellow theme
    st.markdown("""
        <style>
        /* Main app background */
        .stApp {
            background-color: #1C1C1C;
        }

        /* Section headers */
        h2 {
            padding-top: 2rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #404040;
            margin-bottom: 1rem;
            color: #FFC000;
        }

        /* Subsection headers */
        h3 {
            color: #FFC000;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }

        /* Title */
        h1 {
            color: #FFFFFF !important;
        }

        /* Text color */
        p, div, span, label {
            color: #FFFFFF !important;
        }

        /* Info boxes */
        [data-testid="stInfo"] {
            background-color: #2D2D2D;
            border-left: 4px solid #FFC000;
            color: #FFFFFF;
        }

        /* KPI cards styling */
        [data-testid="stMetricValue"] {
            font-size: 2.5rem;
            font-weight: 700;
            color: #FFC000 !important;
        }

        [data-testid="stMetricLabel"] {
            color: #FFFFFF !important;
            font-size: 1rem;
            font-weight: 500;
        }

        /* KPI metric containers */
        [data-testid="metric-container"] {
            background-color: #000000;
            padding: 20px;
            border-radius: 8px;
            border: 2px solid #404040;
            box-shadow: 0 4px 6px rgba(255, 192, 0, 0.1);
        }

        /* Consistent spacing */
        .stMarkdown {
            margin-bottom: 0.5rem;
        }

        /* Horizontal rule */
        hr {
            border-color: #404040;
        }
        </style>
    """, unsafe_allow_html=True)

    # Inject Power BI-style button filter CSS
    inject_button_filter_css()

    # Header
    st.title(f"{APP_ICON} {APP_TITLE}")
    st.markdown(
        """
        Transform invoice data into actionable business intelligence with Power BI-style analytics.
        Use the interactive filter buttons below to explore sales patterns, product performance, and revenue trends.
        """
    )

    # Load data
    try:
        with st.spinner("Loading invoice data..."):
            transformer = load_and_prepare_data()

        # Get available filter options
        available_years = transformer.get_available_years()
        available_products = transformer.get_available_products()

        # Render Power BI-style button filters
        selected_years, selected_products, aggregation_level = DashboardComponents.render_button_filters(
            transformer,
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

        # Get KPIs for display
        kpis = filtered_transformer.get_kpis()

        # ========================================
        # KPI CARDS SECTION
        # ========================================
        st.markdown("<br>", unsafe_allow_html=True)
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

        # Dataset info below KPIs
        st.markdown("---")
        info_col1, info_col2, info_col3 = st.columns(3)

        with info_col1:
            st.metric("Filtered Records", format_number(kpis['num_transactions']))
        with info_col2:
            st.metric("Unique Customers", format_number(kpis['unique_customers']))
        with info_col3:
            st.metric("Unique Products", format_number(kpis['unique_products']))

        st.markdown("---")
        st.markdown("<br>", unsafe_allow_html=True)

        # ========================================
        # REVENUE TREND LINE GRAPH
        # ========================================
        st.markdown("## 📈 Revenue Trend Over Time")
        st.markdown("*Track total revenue performance across selected years and products*")
        st.markdown("<br>", unsafe_allow_html=True)

        # Get yearly revenue data based on filtered selections
        yearly_revenue_data = filtered_transformer.get_yearly_revenue()

        if not yearly_revenue_data.empty:
            DashboardComponents.render_revenue_trend_chart(
                data=yearly_revenue_data,
                x_col='invoice_year',
                y_col='total_revenue',
                title='Total Revenue by Year',
                color='#FFC000'  # Power BI yellow
            )
        else:
            st.info("No revenue data available for the selected filters")

        st.markdown("<br>", unsafe_allow_html=True)

        # ========================================
        # PRODUCT QUANTITY TREND LINE GRAPH
        # ========================================
        st.markdown("## 📦 Product Quantity Trend Over Time")
        st.markdown("*Monitor total quantity sold evolution across selected years and products*")
        st.markdown("<br>", unsafe_allow_html=True)

        # Get yearly quantity data based on filtered selections
        yearly_quantity_data = filtered_transformer.get_yearly_quantity()

        if not yearly_quantity_data.empty:
            DashboardComponents.render_quantity_trend_chart(
                data=yearly_quantity_data,
                x_col='invoice_year',
                y_col='total_quantity',
                title='Total Quantity Sold by Year',
                color='#FFD740'  # Light yellow/amber to distinguish from revenue
            )
        else:
            st.info("No quantity data available for the selected filters")

        st.markdown("<br>", unsafe_allow_html=True)

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
