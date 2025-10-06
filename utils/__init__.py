"""
Utility modules for Solar Solution.

This package contains utility functions for:
- Calculations (batteries, solar, economics, regulator, wiring)
- Translations (loading and managing language files)
- Storage (saving/loading configurations)
- Charts (creating interactive Plotly visualizations)
"""

from .calculations import (
    battery_needed,
    panel_needed,
    calculate_system_cost,
    calculate_roi,
    calculate_co2_impact,
    calculate_regulator,
    calculate_cable_section
)
from .translations import load_translation, get_available_languages
from .storage import (
    save_configuration,
    load_configuration,
    get_saved_configurations,
    delete_configuration,
    load_equipment_library,
    get_library_categories
)
from .charts import (
    create_consumption_pie_chart,
    create_power_time_chart,
    create_hourly_profile_chart
)

__all__ = [
    # Calculations
    "battery_needed",
    "panel_needed",
    "calculate_system_cost",
    "calculate_roi",
    "calculate_co2_impact",
    "calculate_regulator",
    "calculate_cable_section",
    # Translations
    "load_translation",
    "get_available_languages",
    # Storage
    "save_configuration",
    "load_configuration",
    "get_saved_configurations",
    "delete_configuration",
    "load_equipment_library",
    "get_library_categories",
    # Charts
    "create_consumption_pie_chart",
    "create_power_time_chart",
    "create_hourly_profile_chart"
]
