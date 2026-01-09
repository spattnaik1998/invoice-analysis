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
    - selected_products_override: Override sidebar product filter (used for chart clicks)
    - filter_source: Track if filter came from 'sidebar' or 'chart_click'
    """
    if 'selected_products_override' not in st.session_state:
        st.session_state.selected_products_override = None
    if 'filter_source' not in st.session_state:
        st.session_state.filter_source = 'sidebar'


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

    # Custom CSS for professional styling
    st.markdown("""
        <style>
        /* Section headers */
        h2 {
            padding-top: 2rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #f0f0f0;
            margin-bottom: 1rem;
        }

        /* Subsection headers */
        h3 {
            color: #1f4e78;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }

        /* Info boxes */
        [data-testid="stInfo"] {
            background-color: #f8f9fa;
            border-left: 4px solid #4a90e2;
        }

        /* KPI cards spacing */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: 600;
        }

        /* Consistent spacing */
        .stMarkdown {
            margin-bottom: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

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
        # SECTION 1: REVENUE & QUANTITY TRENDS
        # ========================================
        render_section_header(
            "📊",
            "Revenue & Quantity Trends",
            "Historical performance over time"
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Revenue Over Time")
            yearly_revenue_data = filtered_transformer.get_yearly_revenue()
            if not yearly_revenue_data.empty:
                DashboardComponents.render_revenue_trend_chart(
                    data=yearly_revenue_data,
                    x_col='invoice_year',
                    y_col='total_revenue',
                    title='Revenue Trend Over Time'
                )
            else:
                st.info("No revenue data for selected filters")

        with col2:
            st.markdown("### Quantity Sold Over Time")
            yearly_quantity_data = filtered_transformer.get_yearly_quantity()
            if not yearly_quantity_data.empty:
                DashboardComponents.render_quantity_trend_chart(
                    data=yearly_quantity_data,
                    x_col='invoice_year',
                    y_col='total_quantity',
                    title='Quantity Sold Trend Over Time'
                )
            else:
                st.info("No quantity data for selected filters")

        st.markdown("<br><br>", unsafe_allow_html=True)

        # ========================================
        # SECTION 2: PRODUCT ANALYSIS
        # ========================================
        render_section_header(
            "🏷️",
            "Product Analysis",
            "Performance breakdown by product"
        )

        # Top 10 Products
        st.markdown("### Top 10 Products by Revenue")
        st.markdown("*💡 Click on any bar to filter the dashboard to that product*")

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
            st.info("No product data available for the selected filters")

        st.markdown("<br>", unsafe_allow_html=True)

        # Product Heatmap
        st.markdown("### Product Performance Heatmap")
        st.markdown("*💡 Explore revenue patterns across all products and years. Darker colors indicate higher revenue*")

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
            st.info("No heatmap data available for the selected filters")

        st.markdown("<br>", unsafe_allow_html=True)

        # Multi-Product Comparison
        st.markdown("### Product Comparison")

        # User guidance based on number of products
        if len(selected_products) == 1:
            st.info("💡 Viewing performance for a single product. Select multiple products in the sidebar to compare.")
        elif len(selected_products) <= 10:
            st.info(
                f"💡 Comparing {len(selected_products)} products. "
                "Click legend items to hide/show products. Double-click to isolate a single product."
            )
        else:
            st.info(
                f"💡 Comparing {len(selected_products)} products. "
                "Chart may be cluttered - consider filtering to fewer products for clarity. "
                "Use the legend to toggle products on/off."
            )

        # Get multi-product performance data
        try:
            product_performance_data = filtered_transformer.get_multi_product_performance(
                product_ids=selected_products
            )

            if not product_performance_data.empty:
                DashboardComponents.render_multi_product_line_chart(
                    data=product_performance_data,
                    title='Yearly Revenue by Product',
                    y_metric='revenue'
                )

                # Show summary for selected products
                st.markdown("### Product Summary")

                # Calculate per-product totals
                product_totals = product_performance_data.groupby('product_id')['revenue'].agg([
                    ('total_revenue', 'sum'),
                    ('avg_yearly_revenue', 'mean'),
                    ('years_active', 'count')
                ]).reset_index()

                product_totals = product_totals.sort_values('total_revenue', ascending=False)

                # Display as table
                product_totals['total_revenue'] = product_totals['total_revenue'].apply(
                    lambda x: f"${x:,.2f}"
                )
                product_totals['avg_yearly_revenue'] = product_totals['avg_yearly_revenue'].apply(
                    lambda x: f"${x:,.2f}"
                )

                product_totals.columns = ['Product ID', 'Total Revenue', 'Avg Yearly Revenue', 'Years Active']

                st.dataframe(
                    product_totals,
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No product performance data available for the selected filters")
        except Exception as e:
            st.error(f"Error generating product performance chart: {str(e)}")
            st.exception(e)

        st.markdown("<br><br>", unsafe_allow_html=True)

        # ========================================
        # SECTION 3: TRANSACTION VOLUME
        # ========================================
        render_section_header(
            "📈",
            "Transaction Volume Analysis",
            "Activity patterns over time"
        )

        st.markdown(
            f"*💡 Viewing {aggregation_level.lower()} aggregation. "
            "Change in sidebar to adjust granularity. Click and drag to zoom, double-click to reset*"
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
                st.info("No transaction volume data available for the selected filters")
        except Exception as e:
            st.error(f"Error generating transaction volume chart: {str(e)}")
            st.exception(e)

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
