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

# Color scheme (Professional Blue theme from PRD)
COLORS = {
    'primary': '#1F4E78',
    'secondary': '#2E5C8A',
    'accent': '#4A90E2',
    'success': '#27AE60',
    'warning': '#F39C12',
    'danger': '#E74C3C',
    'neutral': '#7F8C8D'
}

# Chart configuration
CHART_COLORS = {
    'line': COLORS['primary'],
    'bar': 'Blues',
    'area': COLORS['accent'],
    'heatmap': 'Blues'
}

# Performance configuration
CACHE_TTL = 3600  # Cache time-to-live in seconds (1 hour)
