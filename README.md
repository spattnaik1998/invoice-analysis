# Invoice Analytics Dashboard

A professional, Power BI-inspired analytics dashboard that transforms invoice data into actionable business intelligence. Features an interactive black and yellow theme with dynamic button filters and real-time visualizations.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![Plotly](https://img.shields.io/badge/Plotly-5.17+-yellow.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

![Dashboard Preview](https://img.shields.io/badge/Theme-Power%20BI%20Black%20%26%20Yellow-FFC000.svg)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Data Schema](#data-schema)
- [Development Roadmap](#development-roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The Invoice Analytics Dashboard provides comprehensive insights into historical invoice data spanning from 1970 to the present. Built with a **Power BI-inspired black and yellow theme**, it enables users to analyze sales patterns, product performance, and revenue trends through interactive visualizations and dynamic button-based filtering.

### Key Capabilities

- **Power BI-Style Button Filters**: Interactive toggle buttons for years, products, and aggregation levels
- **Dynamic KPI Cards**: 7 real-time performance indicators with black/yellow theme
- **Revenue Trend Analysis**: Interactive line chart showing total revenue evolution over time
- **Product Quantity Trends**: Track quantity sold evolution with visual trend analysis
- **Professional Power BI Design**: Black background with yellow accents for modern, striking appearance
- **Performance Optimized**: Sub-second filter updates and <3 second initial load time

---

## Features

### Current Features (v2.0 - Power BI Theme)

- ✅ **Power BI Black & Yellow Theme**: Professional dark theme with yellow accents
- ✅ **Interactive Button Filters**: Toggle buttons for year, product, and aggregation selection
- ✅ **7 Dynamic KPI Cards**: Real-time metrics with Power BI styling
  - Total Revenue, Total Quantity Sold, Avg Transaction Value, Number of Transactions
  - Filtered Records, Unique Customers, Unique Products
- ✅ **Revenue Trend Line Chart**: Interactive visualization showing total revenue over time
- ✅ **Product Quantity Trend Chart**: Track quantity sold evolution with yellow/amber line
- ✅ **Multi-Select Filters**: Select multiple years and products simultaneously
- ✅ **Top 15 Products Display**: Smart filtering to show top-selling products
- ✅ **Clean Architecture**: Three-layer design (Data Loading → Transformation → Visualization)
- ✅ **Performance Optimized**: Caching and efficient data processing

### Color Scheme

- **Primary**: Black (#000000)
- **Accent**: Power BI Yellow (#FFC000)
- **Light Accent**: Amber (#FFD740)
- **Background**: Dark Gray (#1C1C1C)
- **Borders**: Medium Gray (#404040)
- **Text**: White (#FFFFFF)

---

## Architecture

The application follows a **clean three-layer architecture** to ensure separation of concerns, maintainability, and testability:

```
┌─────────────────────────────────────────┐
│      Layer 3: Visualization             │
│  (app.py, components.py)                │
│  - Streamlit UI components              │
│  - Plotly charts                        │
│  - Filter management                    │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│   Layer 2: Data Transformation          │
│  (data_transformer.py)                  │
│  - Derived field calculations           │
│  - Filtering logic                      │
│  - Aggregations for visualizations      │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Layer 1: Data Loading              │
│  (data_loader.py)                       │
│  - CSV file reading                     │
│  - Schema validation                    │
│  - Data type conversions                │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Data Source                     │
│  (invoices.csv)                         │
└─────────────────────────────────────────┘
```

### Layer 1: Data Loading (`src/data/data_loader.py`)

**Responsibilities:**
- Read CSV files from disk
- Validate that all required columns exist
- Convert invoice_date to datetime format
- Provide basic dataset statistics

**Key Class:** `DataLoader`

### Layer 2: Data Transformation (`src/data/data_transformer.py`)

**Responsibilities:**
- Calculate derived fields (total_amount = qty × amount)
- Apply user-selected filters (years, products)
- Perform aggregations for visualizations (yearly totals, top products, etc.)
- Provide clean data structures for charts

**Key Class:** `DataTransformer`

### Layer 3: Visualization (`src/visualization/components.py` + `app.py`)

**Responsibilities:**
- Render interactive Plotly charts
- Display KPI metric cards
- Manage filter UI components
- Orchestrate the overall dashboard layout

**Key Class:** `DashboardComponents`

---

## Technology Stack

### Why Streamlit?

**Streamlit** was chosen as the frontend framework for the following reasons:

1. **Python-Native Integration**
   - Seamlessly works with pandas for data transformation
   - Leverages existing Python data analysis ecosystem
   - No need for separate backend API

2. **Rapid Development**
   - Built-in widgets (multi-select, sliders, etc.)
   - Automatic state management
   - Hot reloading for fast iteration

3. **Performance**
   - `@st.cache_data` decorator provides automatic optimization
   - Meets PRD requirement: <3s initial load, <500ms filter updates
   - Efficient handling of large datasets

4. **Interactive by Default**
   - All Plotly visualizations are interactive (zoom, pan, hover)
   - No additional JavaScript required
   - Professional tooltips and legends

5. **Professional Quality**
   - Widely used in industry for data analytics dashboards
   - Portfolio-worthy for recruiters and hiring managers
   - Clean, modern aesthetic

6. **Easy Deployment**
   - One-click deployment to Streamlit Cloud
   - Docker-ready
   - Works with major cloud providers (AWS, GCP, Azure)

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| **streamlit** | ≥1.28.0 | Web application framework |
| **pandas** | ≥2.0.0 | Data manipulation and analysis |
| **numpy** | ≥1.24.0 | Numerical operations |
| **plotly** | ≥5.17.0 | Interactive visualizations |

---

## Project Structure

```
invoice-analytics-dashboard/
│
├── app.py                          # Main Streamlit application
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .gitignore                      # Git ignore rules
│
├── data/                           # Data directory
│   └── invoices.csv                # Source invoice data (10,000 records)
│
├── src/                            # Source code
│   ├── data/                       # Data layer
│   │   ├── __init__.py
│   │   ├── data_loader.py          # CSV loading and validation
│   │   └── data_transformer.py     # Data transformations and aggregations
│   │
│   ├── visualization/              # Visualization layer
│   │   ├── __init__.py
│   │   └── components.py           # Reusable chart components
│   │
│   └── utils/                      # Utility functions
│       ├── __init__.py
│       └── helpers.py              # Formatting and calculation helpers
│
└── docs/                           # Documentation (future)
    └── Invoice_Analytics_Dashboard_PRD.docx  # Product Requirements Document
```

### Key Files Explained

- **`app.py`**: Main application entry point. Orchestrates data loading, filtering, and visualization rendering.
- **`config.py`**: Centralized configuration for colors, paths, and settings.
- **`src/data/data_loader.py`**: Handles CSV file reading and schema validation.
- **`src/data/data_transformer.py`**: Contains all business logic for data transformations.
- **`src/visualization/components.py`**: Reusable functions for rendering charts and KPI cards.
- **`src/utils/helpers.py`**: Utility functions for formatting currency, numbers, and calculations.

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for version control)

### Step 1: Clone the Repository

```bash
git clone https://github.com/spattnaik1998/invoice-analysis.git
cd invoice-analysis
```

### Step 2: Create a Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify Data File

Ensure that `data/invoices.csv` exists. The file should contain 10,000 invoice records with the following columns:
- first_name, last_name, email, product_id, qty, amount, invoice_date, address, city, stock_code, job

---

## Usage

### Running the Dashboard

From the project root directory, run:

```bash
streamlit run app.py
```

The dashboard will open in your default web browser at `http://localhost:8501`.

### Using the Dashboard

1. **Power BI-Style Button Filters** (Top of Dashboard):
   - **Year Range**: Click year buttons to toggle selection (yellow = selected)
   - **Products**: Click product buttons to select (shows top 15 by default)
   - **Show All Products**: Expand to see all 100 products
   - **Aggregation Level**: Select Daily, Weekly, or Monthly
   - **Quick Actions**: "All Years", "All Products", and "Clear All" buttons
   - Filters update all visualizations and KPIs instantly

2. **Key Performance Indicators** (7 Cards):
   - **Total Revenue**: Sum of all transaction amounts (yellow value)
   - **Total Quantity Sold**: Sum of quantities across all transactions
   - **Avg Transaction Value**: Average revenue per transaction
   - **Number of Transactions**: Count of invoice records
   - **Filtered Records**: Number of records matching current filters
   - **Unique Customers**: Count of distinct customers
   - **Unique Products**: Count of distinct products

3. **Interactive Visualizations**:
   - **Revenue Trend Chart**: Yellow line showing revenue over time
   - **Quantity Trend Chart**: Amber line showing quantity sold evolution
   - Both charts update dynamically based on filter selections
   - Hover over data points for detailed information
   - Dark background with yellow accents for Power BI aesthetic

### Stopping the Application

Press `Ctrl+C` in the terminal to stop the Streamlit server.

---

## Data Schema

### Source Data (`invoices.csv`)

| Column | Data Type | Description |
|--------|-----------|-------------|
| first_name | string | Customer's first name |
| last_name | string | Customer's last name |
| email | string | Customer email (9,769 unique) |
| product_id | integer | Product identifier (100-199) |
| qty | integer | Quantity ordered (1-9 units) |
| amount | float | Unit price ($5.01-$99.99) |
| invoice_date | string | Transaction date (DD/MM/YYYY format) |
| address | string | Customer street address |
| city | string | Customer city |
| stock_code | integer | Internal stock code |
| job | string | Customer's job title |

### Derived Fields

| Field | Calculation | Purpose |
|-------|-------------|---------|
| full_name | first_name + " " + last_name | Complete customer name |
| total_amount | qty × amount | Total transaction revenue |
| invoice_year | year(invoice_date) | Year for aggregations |
| invoice_month | month(invoice_date) | Month for aggregations |
| invoice_day | day(invoice_date) | Day for daily trends |

### Dataset Statistics

- **Total Records**: 10,000 invoices
- **Date Range**: January 5, 1970 to January 17, 2022 (52 years)
- **Total Products**: 100 distinct products (IDs 100-199)
- **Total Revenue**: $2,656,870.38
- **Total Quantity Sold**: 50,059 units
- **Unique Customers**: 9,769 unique email addresses

---

## Development Roadmap

### Phase 1: Foundation ✅ COMPLETE
- [x] Project structure setup
- [x] Data loading and validation
- [x] Data transformation pipeline
- [x] Filter components
- [x] KPI cards with real-time calculations

### Phase 2: Power BI Theme & Button Filters ✅ COMPLETE
- [x] Black and yellow Power BI color scheme
- [x] Interactive toggle button filters
- [x] Top 15 products smart filtering
- [x] Multi-select capability for years and products
- [x] Dynamic filter state management

### Phase 3: Core Visualizations ✅ COMPLETE
- [x] Yearly Revenue Trend Line Chart (Yellow theme)
- [x] Yearly Quantity Sold Trend Line Chart (Amber theme)
- [x] Dark theme Plotly charts with yellow accents
- [x] Interactive hover tooltips

### Phase 4: Future Enhancements (Optional)
- [ ] Additional chart types (heatmaps, bar charts)
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] Accessibility improvements (WCAG 2.1 AA)
- [ ] KPI percentage change calculations
- [ ] Export functionality (PDF/PowerPoint reports)
- [ ] Predictive analytics (ARIMA, Prophet)
- [ ] Customer segmentation (RFM analysis)

---

## Performance Optimization

The dashboard is optimized for performance through:

1. **Data Caching**: `@st.cache_data` decorator caches loaded data for 1 hour
2. **Lazy Loading**: Visualizations are only rendered when data is available
3. **Efficient Filtering**: Pandas operations are optimized for speed
4. **Minimal Re-renders**: Streamlit's reactive model only updates changed components

**Performance Targets (from PRD):**
- ✅ Initial load time: < 3 seconds
- ✅ Filter updates: < 500ms
- ✅ Support for datasets with up to 1 million records

---

## Contributing

This is a portfolio project, but contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Built following the comprehensive Product Requirements Document (PRD)
- Inspired by **Microsoft Power BI** dashboard aesthetics
- Color palette: Power BI black and yellow theme
- Interactive filters modeled after Power BI filter chips/buttons

---

## Contact

**Project Maintainer**: [Your Name]
- GitHub: [@spattnaik1998](https://github.com/spattnaik1998)
- Repository: [invoice-analysis](https://github.com/spattnaik1998/invoice-analysis)

---

**Built with ❤️ using Python and Streamlit**
