"""
Page 2: System Calculations
Calculate batteries, solar panels, regulator, and cables
"""
import streamlit as st
import json
from pathlib import Path
import sys
import math

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.equipment import EquipmentFactory
from utils.translations import load_translation
from utils.calculations import (
    battery_needed, panel_needed,
    calculate_system_cost, calculate_roi, calculate_co2_impact,
    calculate_regulator, calculate_cable_section
)

# Page configuration
st.set_page_config(
    page_title="Calculations - Solar Solution",
    page_icon=":material/battery_charging_full:",
    layout="wide"
)

# Initialize session state
if "language" not in st.session_state:
    st.session_state["language"] = load_translation("en")
    st.session_state["current_lang"] = "en"

if "equipments" not in st.session_state:
    st.session_state["equipments"] = EquipmentFactory()

t = st.session_state["language"]
factory = st.session_state["equipments"]

# Language selector in sidebar
with st.sidebar:
    st.markdown("### :material/settings: Settings")
    lang = st.selectbox(
        "🌍 Language", 
        ["en", "fr"],
        index=0 if st.session_state.get("current_lang", "en") == "en" else 1,
        key="lang_selector_calc"
    )
    
    if lang != st.session_state.get("current_lang", "en"):
        st.session_state["current_lang"] = lang
        st.session_state["language"] = load_translation(lang)
        st.rerun()

# Top Navigation
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button(":material/home: " + t.get("nav_home", "Home"), width="stretch", key="nav_home_calc"):
        st.switch_page("app.py")
with col2:
    if st.button(":material/bolt: " + t.get("nav_equipments", "Equipments"), width="stretch", key="nav_eq_calc"):
        st.switch_page("pages/1_Equipments.py")
with col3:
    st.button(":material/battery_charging_full: " + t.get("nav_calculations", "Calculations"), width="stretch", disabled=True, type="primary", key="nav_calc_calc")
with col4:
    if st.button(":material/description: " + t.get("nav_report", "Report"), width="stretch", key="nav_report_calc"):
        st.switch_page("pages/3_Report.py")

st.markdown("---")

# Page Title
st.title(":material/battery_charging_full: " + t.get("nav_calculations", "System Calculations"))

# Check if equipment exists
if factory.is_empty():
    st.warning(":material/warning: " + t.get("Main", {}).get("no_equipment", "No equipment added. Please add equipment first."))
    if st.button("➕ " + t.get("nav_equipments", "Go to Equipments")):
        st.switch_page("pages/1_Equipments.py")
    st.stop()

# Display consumption summary
daily_energy = factory.total_energy_consumption()
total_power = factory.total_power()

col1, col2 = st.columns(2)
with col1:
    st.metric(
        label=":material/battery_charging_full: " + t.get("Main", {}).get("daily_consumption", "Daily Consumption"),
        value=f"{daily_energy:.0f} Wh",
        delta=f"{daily_energy/1000:.2f} kWh"
    )
with col2:
    st.metric(
        label=":material/bolt: " + t.get("Main", {}).get("converter_power", "Total Power"),
        value=f"{total_power:.0f} W",
        delta=f"{total_power/1000:.2f} kW"
    )

st.markdown("---")

# Battery Configuration
st.subheader(":material/battery_charging_full: " + t.get("Battery", {}).get("title", "Battery Configuration"))

col1, col2 = st.columns(2)

with col1:
    battery_type = st.selectbox(
        t.get("Battery", {}).get("type", "Battery Type"),
        ["Lead-Acid", "Lithium"],
        index=0,
        key="battery_type"
    )
    
    # Discharge depth based on battery type
    default_dod = 0.5 if battery_type == "Lead-Acid" else 0.8
    
    battery_voltage = st.selectbox(
        t.get("Battery", {}).get("voltage", "Battery Voltage (V)"),
        [12, 24, 48],
        index=0,
        key="battery_voltage"
    )
    
    battery_capacity = st.number_input(
        t.get("Battery", {}).get("capacity", "Battery Capacity (Ah)"),
        min_value=10,
        value=200,
        step=10,
        key="battery_capacity"
    )

with col2:
    autonomy_days = st.number_input(
        t.get("Battery", {}).get("autonomy", "Autonomy (days)"),
        min_value=1,
        max_value=7,
        value=2,
        step=1,
        key="autonomy_days"
    )
    
    discharge_depth = st.slider(
        t.get("Battery", {}).get("dod", "Depth of Discharge (DoD)"),
        min_value=0.3,
        max_value=0.9,
        value=default_dod,
        step=0.05,
        key="discharge_depth",
        help="Lead-Acid: 50% | Lithium: 80%"
    )

# Calculate batteries needed
num_batteries = battery_needed(
    daily_energy_wh=daily_energy,
    battery_voltage=battery_voltage,
    battery_capacity_ah=battery_capacity,
    autonomy_days=autonomy_days,
    discharge_depth=discharge_depth
)

st.success(f"**{t.get('Battery', {}).get('result', 'Batteries Needed')}: {num_batteries}**")

# Detailed info
with st.expander(":material/info: " + t.get("Battery", {}).get("details", "Battery Details")):
    total_capacity_ah = num_batteries * battery_capacity
    total_energy_wh = total_capacity_ah * battery_voltage * discharge_depth
    
    st.markdown(f"""
    - **Total Capacity:** {total_capacity_ah} Ah ({total_energy_wh:.0f} Wh usable)
    - **Total Energy Storage:** {total_capacity_ah * battery_voltage:.0f} Wh
    - **Energy per battery:** {battery_voltage * battery_capacity:.0f} Wh
    - **Usable per battery:** {battery_voltage * battery_capacity * discharge_depth:.0f} Wh
    - **Safety margin:** Autonomy for {autonomy_days} days
    """)

st.markdown("---")

# Solar Panel Configuration
st.subheader(":material/wb_sunny: " + t.get("PV", {}).get("title", "Solar Panel Configuration"))

col1, col2 = st.columns(2)

with col1:
    pv_power = st.number_input(
        t.get("PV", {}).get("power", "Panel Power (W)"),
        min_value=50,
        value=300,
        step=50,
        key="pv_power"
    )

with col2:
    sun_hours = st.number_input(
        t.get("PV", {}).get("sun_hours", "Peak Sun Hours"),
        min_value=1.0,
        max_value=10.0,
        value=5.0,
        step=0.5,
        key="sun_hours",
        help="Average daily peak sun hours in your location"
    )

# Calculate panels needed
num_panels = panel_needed(
    daily_energy_wh=daily_energy,
    pv_power_w=pv_power,
    sun_hours=sun_hours
)

total_pv_power = num_panels * pv_power

st.success(f"**{t.get('PV', {}).get('result', 'Panels Needed')}: {num_panels}** ({total_pv_power} W total)")

# Detailed info
with st.expander(":material/info: " + t.get("PV", {}).get("details", "Solar Panel Details")):
    daily_production = total_pv_power * sun_hours
    surplus = daily_production - daily_energy
    surplus_percent = (surplus / daily_energy * 100) if daily_energy > 0 else 0
    
    st.markdown(f"""
    - **Total PV Power:** {total_pv_power} W ({total_pv_power/1000:.2f} kW)
    - **Daily Production:** {daily_production:.0f} Wh ({daily_production/1000:.2f} kWh)
    - **Daily Consumption:** {daily_energy:.0f} Wh ({daily_energy/1000:.2f} kWh)
    - **Surplus:** {surplus:.0f} Wh ({surplus_percent:.1f}%)
    - **Panel Area (approx):** {num_panels * 1.7:.1f} m² (assuming 1.7m² per panel)
    """)

st.markdown("---")

# Charge Controller
st.subheader(":material/settings: " + t.get("Regulator", {}).get("title", "Charge Controller"))

col1, col2 = st.columns(2)

with col1:
    regulator_type = st.selectbox(
        t.get("Regulator", {}).get("type", "Controller Type"),
        ["MPPT", "PWM"],
        index=0,
        key="regulator_type",
        help="MPPT: More efficient (98%), PWM: Less efficient (85%)"
    )

regulator_specs = calculate_regulator(
    pv_power=total_pv_power,
    battery_voltage=battery_voltage,
    regulator_type=regulator_type
)

with col2:
    recommended_current = float(regulator_specs['recommended_current'])
    st.metric(
        t.get("Regulator", {}).get("current", "Recommended Current"),
        f"{math.ceil(recommended_current)} A"
    )

with st.expander(":material/info: " + t.get("Regulator", {}).get("details", "Controller Details")):
    st.markdown(f"""
    - **Type:** {regulator_specs['type']}
    - **Nominal Current:** {regulator_specs['nominal_current']:.1f} A
    - **Recommended Current:** {regulator_specs['recommended_current']:.1f} A (with 25% safety margin)
    - **Efficiency:** {regulator_specs['efficiency']*100:.0f}%
    - **PV Power:** {regulator_specs['nominal_power']} W
    - **Battery Voltage:** {battery_voltage} V
    """)

st.markdown("---")

# Cable Sizing
st.subheader(":material/power: " + t.get("Cable", {}).get("title", "Cable Sizing"))

col1, col2, col3 = st.columns(3)

with col1:
    cable_current = st.number_input(
        t.get("Cable", {}).get("current", "Current (A)"),
        min_value=1.0,
        value=float(regulator_specs['recommended_current']),
        step=1.0,
        key="cable_current"
    )

with col2:
    cable_length = st.number_input(
        t.get("Cable", {}).get("length", "Cable Length (m)"),
        min_value=1.0,
        value=10.0,
        step=1.0,
        key="cable_length",
        help="One-way distance"
    )

with col3:
    max_voltage_drop = st.slider(
        t.get("Cable", {}).get("max_drop", "Max Voltage Drop (%)"),
        min_value=1.0,
        max_value=5.0,
        value=3.0,
        step=0.5,
        key="max_drop"
    )

cable_specs = calculate_cable_section(
    current=cable_current,
    length=cable_length,
    voltage=battery_voltage,
    max_drop_percent=max_voltage_drop
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        t.get("Cable", {}).get("section", "Cable Section"),
        f"{cable_specs['cable_section']:.1f} mm²"
    )

with col2:
    st.metric(
        t.get("Cable", {}).get("actual_drop", "Actual Drop"),
        f"{cable_specs['actual_drop_percent']:.2f}%",
        delta=f"{cable_specs['actual_drop_volts']:.2f}V"
    )

with col3:
    st.metric(
        t.get("Cable", {}).get("fuse", "Fuse Rating"),
        f"{cable_specs['fuse_rating']} A"
    )

with st.expander(":material/info: " + t.get("Cable", {}).get("details", "Cable Details")):
    st.markdown(f"""
    **Calculation Details:**
    - Current: {cable_specs['current']} A
    - Cable length: {cable_length} m (one-way)
    - Total circuit length: {cable_length * 2} m (round-trip)
    - System voltage: {battery_voltage} V
    - Maximum acceptable drop: {max_voltage_drop}% ({battery_voltage * max_voltage_drop/100:.2f} V)
    - **Selected cable section: {cable_specs['cable_section']:.1f} mm²**
    - **Actual voltage drop: {cable_specs['actual_drop_volts']:.2f} V ({cable_specs['actual_drop_percent']:.2f}%)**
    - **Fuse protection: {cable_specs['fuse_rating']} A**
    
    *Standard cable sizes (IEC): 1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240 mm²*
    """)

st.markdown("---")

# Economic Analysis (expandable)
with st.expander(":material/attach_money: " + t.get("Economics", {}).get("title", "Economic Analysis"), expanded=False):
    st.subheader(t.get("Economics", {}).get("subtitle", "Cost Analysis & ROI"))
    
    col1, col2 = st.columns(2)
    
    with col1:
        battery_unit_cost = st.number_input(
            t.get("Economics", {}).get("battery_cost", "Battery Unit Cost ($)"),
            min_value=0.0,
            value=200.0,
            step=10.0,
            format="%.2f"
        )
        
        pv_unit_cost = st.number_input(
            t.get("Economics", {}).get("pv_cost", "Panel Unit Cost ($)"),
            min_value=0.0,
            value=150.0,
            step=10.0,
            format="%.2f"
        )
        
        converter_cost = st.number_input(
            t.get("Economics", {}).get("converter_cost", "Converter Cost ($)"),
            min_value=0.0,
            value=300.0,
            step=50.0,
            format="%.2f"
        )
    
    with col2:
        regulator_cost = st.number_input(
            t.get("Economics", {}).get("regulator_cost", "Regulator Cost ($)"),
            min_value=0.0,
            value=200.0,
            step=50.0,
            format="%.2f"
        )
        
        installation_cost = st.number_input(
            t.get("Economics", {}).get("installation_cost", "Installation Cost ($)"),
            min_value=0.0,
            value=500.0,
            step=50.0,
            format="%.2f"
        )
        
        electricity_price = st.number_input(
            t.get("Economics", {}).get("electricity_price", "Electricity Price ($/kWh)"),
            min_value=0.01,
            value=0.15,
            step=0.01,
            format="%.2f"
        )
    
    # Calculate costs
    costs = calculate_system_cost(
        num_batteries=num_batteries,
        battery_unit_cost=battery_unit_cost,
        num_pv=num_panels,
        pv_unit_cost=pv_unit_cost,
        converter_cost=converter_cost,
        regulator_cost=regulator_cost,
        installation_cost=installation_cost
    )
    
    # Calculate ROI
    roi_data = calculate_roi(
        total_cost=costs["total"],
        daily_energy_kwh=daily_energy / 1000,
        electricity_price_per_kwh=electricity_price
    )
    
    # Calculate CO2 impact
    co2_data = calculate_co2_impact(annual_energy_kwh=(daily_energy / 1000) * 365)
    
    st.markdown("### 💵 Cost Breakdown")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            t.get("Economics", {}).get("battery_total", "Batteries"),
            f"${costs['battery_total']:.2f}"
        )
        st.metric(
            t.get("Economics", {}).get("pv_total", "Solar Panels"),
            f"${costs['pv_total']:.2f}"
        )
    
    with col2:
        st.metric(
            t.get("Economics", {}).get("converter", "Converter"),
            f"${costs['converter']:.2f}"
        )
        st.metric(
            t.get("Economics", {}).get("regulator", "Regulator"),
            f"${costs['regulator']:.2f}"
        )
    
    with col3:
        st.metric(
            t.get("Economics", {}).get("installation", "Installation"),
            f"${costs['installation']:.2f}"
        )
        st.metric(
            t.get("Economics", {}).get("total", "**TOTAL**"),
            f"**${costs['total']:.2f}**"
        )
    
    st.markdown("### :material/trending_up: Return on Investment")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            t.get("Economics", {}).get("daily_savings", "Daily Savings"),
            f"${roi_data['daily']:.2f}"
        )
    
    with col2:
        st.metric(
            t.get("Economics", {}).get("monthly_savings", "Monthly Savings"),
            f"${roi_data['monthly']:.2f}"
        )
    
    with col3:
        st.metric(
            t.get("Economics", {}).get("annual_savings", "Annual Savings"),
            f"${roi_data['annual']:.2f}"
        )
    
    with col4:
        roi_years = roi_data['roi_years']
        roi_color = "🟢" if roi_years < 10 else "🟡" if roi_years < 15 else "🔴"
        st.metric(
            t.get("Economics", {}).get("roi_years", "ROI Period"),
            f"{roi_color} {roi_years:.1f} years"
        )
    
    st.markdown("### :material/park: Environmental Impact")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            t.get("Economics", {}).get("co2_annual", "CO₂ Avoided/Year"),
            f"{co2_data['co2_kg']:.0f} kg"
        )
    
    with col2:
        st.metric(
            t.get("Economics", {}).get("co2_lifetime", "CO₂ (25 years)"),
            f"{co2_data['co2_tons'] * 25:.1f} tons"
        )
    
    with col3:
        st.metric(
            t.get("Economics", {}).get("trees_equivalent", "Trees Equivalent"),
            f":material/park: {co2_data['trees']:.1f} trees/year"
        )

# Summary Box
st.markdown("---")
st.subheader(":material/list: " + t.get("Summary", {}).get("title", "System Summary"))

summary_col1, summary_col2, summary_col3 = st.columns(3)

with summary_col1:
    st.markdown(f"""
    **:material/bolt: Consumption**
    - Daily: {daily_energy:.0f} Wh
    - Total Power: {total_power:.0f} W
    - Equipment: {len(factory.get_equipments())}
    """)

with summary_col2:
    recommended_current_val = float(regulator_specs['recommended_current'])
    st.markdown(f"""
    **:material/battery_charging_full: System Components**
    - Batteries: {num_batteries} × {battery_capacity}Ah {battery_voltage}V
    - Solar Panels: {num_panels} × {pv_power}W
    - Controller: {regulator_type} {math.ceil(recommended_current_val)}A
    - Cable: {cable_specs['cable_section']:.1f}mm² (fuse: {cable_specs['fuse_rating']}A)
    """)

with summary_col3:
    st.markdown(f"""
    **:material/check_circle: Recommendations**
    - Battery Type: {battery_type}
    - DoD: {discharge_depth*100:.0f}%
    - Autonomy: {autonomy_days} days
    - Max Voltage Drop: {max_voltage_drop}%
    """)

# Save calculation to session for report
if "calculation_results" not in st.session_state:
    st.session_state["calculation_results"] = {}

st.session_state["calculation_results"] = {
    "daily_energy": daily_energy,
    "total_power": total_power,
    "num_batteries": num_batteries,
    "battery_voltage": battery_voltage,
    "battery_capacity": battery_capacity,
    "battery_type": battery_type,
    "discharge_depth": discharge_depth,
    "autonomy_days": autonomy_days,
    "num_panels": num_panels,
    "pv_power": pv_power,
    "total_pv_power": total_pv_power,
    "sun_hours": sun_hours,
    "regulator_type": regulator_type,
    "regulator_specs": regulator_specs,
    "cable_specs": cable_specs,
}

# Action button
st.markdown("---")
if st.button(":material/description: " + t.get("nav_report", "Generate Report"), type="primary", width="stretch", key="generate_report_btn"):
    st.switch_page("pages/3_Report.py")
