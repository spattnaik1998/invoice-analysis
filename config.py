"""
Configuration Module

This module contains all configuration settings for the application.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Data configuration
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "invoices.csv"

# Application configuration
APP_TITLE = "Invoice Analytics Dashboard"
APP_ICON = ":bar_chart:"
APP_LAYOUT = "wide"

# Color scheme (Power BI Black and Yellow theme)
COLORS = {
    'primary': '#000000',      # Black
    'secondary': '#2D2D2D',    # Dark gray
    'accent': '#FFC000',       # Power BI Yellow/Gold
    'success': '#27AE60',      # Keep green for positive
    'warning': '#F39C12',      # Keep orange for warning
    'danger': '#E74C3C',       # Keep red for negative
    'neutral': '#7F8C8D',      # Gray
    'background': '#1C1C1C',   # Very dark gray background
    'text_light': '#FFFFFF',   # White text
    'border': '#404040'        # Medium gray for borders
}

# Chart configuration (kept for compatibility)
CHART_COLORS = {
    'line': COLORS['accent'],
    'bar': 'YlOrBr',
    'area': COLORS['accent'],
    'heatmap': 'YlOrBr'
}

# Performance configuration
CACHE_TTL = 3600  # Cache time-to-live in seconds (1 hour)
