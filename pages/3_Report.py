"""
Page 3: Printable Report
Generate a complete, print-ready system design report
"""
import streamlit as st
import json
from pathlib import Path
import sys
from datetime import datetime
import math

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.equipment import EquipmentFactory
from utils.translations import load_translation
from utils.charts import create_consumption_pie_chart, create_power_time_chart, create_hourly_profile_chart

# Page configuration
st.set_page_config(
    page_title="Report - Solar Solution",
    page_icon=":material/description:",
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
        key="lang_selector_report"
    )
    
    if lang != st.session_state.get("current_lang", "en"):
        st.session_state["current_lang"] = lang
        st.session_state["language"] = load_translation(lang)
        st.rerun()

# Top Navigation
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button(":material/home: " + t.get("nav_home", "Home"), width="stretch", key="nav_home_top"):
        st.switch_page("app.py")
with col2:
    if st.button(":material/bolt: " + t.get("nav_equipments", "Equipments"), width="stretch", key="nav_eq_top"):
        st.switch_page("pages/1_Equipments.py")
with col3:
    if st.button(":material/battery_charging_full: " + t.get("nav_calculations", "Calculations"), width="stretch", key="nav_calc_top"):
        st.switch_page("pages/2_Calculations.py")
with col4:
    st.button(":material/description: " + t.get("nav_report", "Report"), width="stretch", disabled=True, type="primary", key="nav_report_top")

st.markdown("---")

# Check if equipment and calculations exist
if factory.is_empty():
    st.warning(":material/warning: " + t.get("Main", {}).get("no_equipment", "No equipment added. Please add equipment first."))
    if st.button("➕ " + t.get("nav_equipments", "Go to Equipments"), key="warn_goto_eq"):
        st.switch_page("pages/1_Equipments.py")
    st.stop()

if "calculation_results" not in st.session_state or not st.session_state["calculation_results"]:
    st.warning(":material/warning: No calculations found. Please configure your system first.")
    if st.button(":material/battery_charging_full: " + t.get("nav_calculations", "Go to Calculations"), key="warn_goto_calc"):
        st.switch_page("pages/2_Calculations.py")
    st.stop()

# Get calculation results
calc = st.session_state["calculation_results"]

# Print CSS
st.markdown("""
<style>
@media print {
    /* Hide Streamlit UI elements */
    header, footer, .stApp > header, .stApp > footer, 
    [data-testid="stSidebarNav"], [data-testid="stToolbar"],
    section[data-testid="stSidebar"], .stDeployButton {
        display: none !important;
    }
    
    /* Optimize page for printing */
    body {
        margin: 0;
        padding: 20px;
    }
    
    /* Prevent page breaks inside elements */
    .print-section {
        page-break-inside: avoid;
        margin-bottom: 20px;
    }
    
    /* Add page breaks between major sections */
    .page-break {
        page-break-before: always;
    }
    
    /* Ensure charts fit on page */
    .plotly {
        max-height: 300px !important;
    }
}

.report-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    text-align: center;
}

.report-section {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    border-left: 4px solid #667eea;
}

.report-subsection {
    background-color: white;
    padding: 1rem;
    border-radius: 5px;
    margin-top: 1rem;
}

.metric-box {
    background-color: white;
    padding: 1rem;
    border-radius: 5px;
    text-align: center;
    border: 2px solid #e0e0e0;
}

.metric-value {
    font-size: 2rem;
    font-weight: bold;
    color: #667eea;
}

.metric-label {
    font-size: 0.9rem;
    color: #666;
    margin-top: 0.5rem;
}

.recommendation-box {
    background-color: #e7f3ff;
    border-left: 4px solid #2196F3;
    padding: 1rem;
    margin: 1rem 0;
}

.warning-box {
    background-color: #fff3cd;
    border-left: 4px solid #ffc107;
    padding: 1rem;
    margin: 1rem 0;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

th {
    background-color: #667eea;
    color: white;
}

tr:hover {
    background-color: #f5f5f5;
}
</style>
""", unsafe_allow_html=True)

# Print button in sidebar
with st.sidebar:
    st.markdown("---")
    st.markdown("### :material/print: Print Options")
    st.info(":material/lightbulb: Use your browser's print function (Ctrl+P or Cmd+P) to print or save as PDF.")
    if st.button(":material/print: Print Report", width="stretch", type="primary", key="print_report_btn"):
        st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

# Report Header
st.markdown(":material/wb_sunny:")
st.markdown(f"""
<div class="report-header">
    <h1>☀️ Solar System Design Report</h1>
    <p style="font-size: 1.2rem; margin-top: 1rem;">
        Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}
    </p>
</div>
""", unsafe_allow_html=True)

# Project Information
st.markdown('<div class="print-section">', unsafe_allow_html=True)
st.markdown('<div class="report-section">', unsafe_allow_html=True)
st.subheader(":material/list: Project Information")

col1, col2, col3 = st.columns(3)

with col1:
    project_name = st.text_input("Project Name", value="My Solar System", key="project_name")

with col2:
    client_name = st.text_input("Client Name", value="", key="client_name")

with col3:
    location = st.text_input("Location", value="", key="location")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Executive Summary
st.markdown('<div class="print-section">', unsafe_allow_html=True)
st.markdown('<div class="report-section">', unsafe_allow_html=True)
st.subheader(":material/analytics: Executive Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-value">{calc['daily_energy']:.0f}</div>
        <div class="metric-label">Wh/day</div>
        <div style="font-size: 0.8rem; color: #888;">Daily Consumption</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-value">{calc['num_batteries']}</div>
        <div class="metric-label">Batteries</div>
        <div style="font-size: 0.8rem; color: #888;">{calc['battery_capacity']}Ah {calc['battery_voltage']}V</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-value">{calc['num_panels']}</div>
        <div class="metric-label">Solar Panels</div>
        <div style="font-size: 0.8rem; color: #888;">{calc['pv_power']}W each</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-value">{calc['total_pv_power']}</div>
        <div class="metric-label">W</div>
        <div style="font-size: 0.8rem; color: #888;">Total PV Power</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Equipment List
st.markdown('<div class="print-section">', unsafe_allow_html=True)
st.markdown('<div class="report-section">', unsafe_allow_html=True)
st.subheader(":material/bolt: Equipment List")

df = factory.df_datas()
st.dataframe(df, width="stretch", hide_index=True)

# Summary stats
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Equipment", len(factory.get_equipments()))

with col2:
    st.metric("Total Power", f"{calc['total_power']:.0f} W")

with col3:
    st.metric("Daily Energy", f"{calc['daily_energy']:.2f} Wh")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Consumption Charts
st.markdown('<div class="print-section">', unsafe_allow_html=True)
st.markdown('<div class="report-section">', unsafe_allow_html=True)
st.subheader(":material/analytics: Consumption Analysis")

col1, col2 = st.columns(2)

with col1:
    fig1 = create_consumption_pie_chart(factory, t)
    fig1.update_layout(height=300)
    st.plotly_chart(fig1, width="stretch")

with col2:
    fig2 = create_power_time_chart(factory, t)
    fig2.update_layout(height=300)
    st.plotly_chart(fig2, width="stretch")

# Hourly profile
fig3 = create_hourly_profile_chart(factory, t)
fig3.update_layout(height=350)
st.plotly_chart(fig3, width="stretch")

hourly_profile = factory.get_hourly_profile()
peak_consumption = max(hourly_profile)
peak_hour = hourly_profile.index(peak_consumption)
avg_consumption = sum(hourly_profile) / 24

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Peak Consumption", f"{peak_consumption:.0f} W", f"@ {peak_hour}h")

with col2:
    st.metric("Average Consumption", f"{avg_consumption:.0f} W")

with col3:
    active_hours = sum(1 for p in hourly_profile if p > 0)
    st.metric("Active Hours", f"{active_hours} h")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# System Specifications
st.markdown('<div class="print-section page-break">', unsafe_allow_html=True)
st.markdown('<div class="report-section">', unsafe_allow_html=True)
st.subheader(":material/battery_charging_full: Battery System Specifications")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    **Configuration:**
    - Battery Type: {calc['battery_type']}
    - Number of Batteries: **{calc['num_batteries']}**
    - Battery Voltage: {calc['battery_voltage']} V
    - Battery Capacity: {calc['battery_capacity']} Ah
    - Depth of Discharge: {calc['discharge_depth']*100:.0f}%
    - Autonomy: {calc['autonomy_days']} days
    """)

with col2:
    total_capacity = calc['num_batteries'] * calc['battery_capacity']
    total_energy = total_capacity * calc['battery_voltage']
    usable_energy = total_energy * calc['discharge_depth']
    
    st.markdown(f"""
    **Total Capacity:**
    - Total Amp-Hours: {total_capacity} Ah
    - Total Energy Storage: {total_energy:.0f} Wh ({total_energy/1000:.2f} kWh)
    - Usable Energy: {usable_energy:.0f} Wh ({usable_energy/1000:.2f} kWh)
    - Days of Autonomy: {calc['autonomy_days']} days
    """)

st.markdown('<div class="recommendation-box">', unsafe_allow_html=True)
st.markdown(f"""
**:material/lightbulb: Recommendation:** The battery bank provides {calc['autonomy_days']} days of autonomy at {calc['discharge_depth']*100:.0f}% depth of discharge. 
For {calc['battery_type']} batteries, this DoD level ensures optimal lifespan and performance.
""")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Solar Panel System
st.markdown('<div class="print-section">', unsafe_allow_html=True)
st.markdown('<div class="report-section">', unsafe_allow_html=True)
st.subheader(":material/wb_sunny: Solar Panel System Specifications")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    **Configuration:**
    - Number of Panels: **{calc['num_panels']}**
    - Panel Power: {calc['pv_power']} W
    - Total PV Power: **{calc['total_pv_power']} W** ({calc['total_pv_power']/1000:.2f} kW)
    - Peak Sun Hours: {calc['sun_hours']} h/day
    """)

with col2:
    daily_production = calc['total_pv_power'] * calc['sun_hours']
    surplus = daily_production - calc['daily_energy']
    surplus_percent = (surplus / calc['daily_energy'] * 100) if calc['daily_energy'] > 0 else 0
    panel_area = calc['num_panels'] * 1.7
    
    st.markdown(f"""
    **Production:**
    - Daily Production: {daily_production:.0f} Wh ({daily_production/1000:.2f} kWh)
    - Daily Consumption: {calc['daily_energy']:.0f} Wh ({calc['daily_energy']/1000:.2f} kWh)
    - Surplus: {surplus:.0f} Wh ({surplus_percent:.1f}%)
    - Estimated Panel Area: {panel_area:.1f} m²
    """)

st.markdown('<div class="recommendation-box">', unsafe_allow_html=True)
st.markdown(f"""
**:material/lightbulb: Recommendation:** The solar array produces approximately {surplus_percent:.1f}% more energy than daily consumption, 
providing a safety margin for cloudy days and ensuring the batteries are fully charged.
""")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Charge Controller
st.markdown('<div class="print-section">', unsafe_allow_html=True)
st.markdown('<div class="report-section">', unsafe_allow_html=True)
st.subheader(":material/settings: Charge Controller Specifications")

regulator_specs = calc['regulator_specs']

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    **Controller Type:** {calc['regulator_type']}
    - Nominal Current: {regulator_specs['nominal_current']:.1f} A
    - **Recommended Current: {regulator_specs['recommended_current']:.1f} A**
    - Efficiency: {regulator_specs['efficiency']*100:.0f}%
    """)

with col2:
    st.markdown(f"""
    **System Parameters:**
    - PV Power: {regulator_specs['nominal_power']} W
    - Battery Voltage: {calc['battery_voltage']} V
    - Safety Margin: 25%
    """)

st.markdown('<div class="recommendation-box">', unsafe_allow_html=True)
recommended_current_val = float(regulator_specs['recommended_current'])
if calc['regulator_type'] == "MPPT":
    st.markdown(f"""
    **:material/lightbulb: Recommendation:** MPPT controller recommended for maximum efficiency (98%). 
    Select a controller rated for at least {math.ceil(recommended_current_val)} A.
    """)
else:
    st.markdown(f"""
    **:material/lightbulb: Recommendation:** PWM controller is a cost-effective option (85% efficiency). 
    Select a controller rated for at least {math.ceil(recommended_current_val)} A.
    """)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Cable Specifications
st.markdown('<div class="print-section">', unsafe_allow_html=True)
st.markdown('<div class="report-section">', unsafe_allow_html=True)
st.subheader(":material/power: Cable and Protection Specifications")

cable_specs = calc['cable_specs']

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    **Cable Specifications:**
    - **Cable Section: {cable_specs['cable_section']:.1f} mm²**
    - Maximum Current: {cable_specs['current']:.1f} A
    - **Fuse Rating: {cable_specs['fuse_rating']} A**
    """)

with col2:
    st.markdown(f"""
    **Voltage Drop:**
    - Actual Drop: {cable_specs['actual_drop_volts']:.2f} V ({cable_specs['actual_drop_percent']:.2f}%)
    - System Voltage: {calc['battery_voltage']} V
    - Within acceptable limits :material/check_circle:
    """)

st.markdown('<div class="warning-box">', unsafe_allow_html=True)
st.markdown(f"""
**:material/warning: Important:** Use cables with a section of at least {cable_specs['cable_section']:.1f} mm² to minimize voltage drop. 
Install appropriate fuses ({cable_specs['fuse_rating']} A) for safety.
""")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Installation Recommendations
st.markdown('<div class="print-section page-break">', unsafe_allow_html=True)
st.markdown('<div class="report-section">', unsafe_allow_html=True)
st.subheader(":material/check_circle: Installation Recommendations")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Solar Panel Installation:**
    - Orient panels toward the equator (South in Northern Hemisphere, North in Southern)
    - Tilt angle = latitude ± 15° (adjust seasonally for optimal performance)
    - Ensure no shading from trees or buildings
    - Allow proper ventilation to prevent overheating
    - Use corrosion-resistant mounting hardware
    - Ground the system properly
    """)

with col2:
    st.markdown("""
    **Battery Installation:**
    - Install in a well-ventilated area
    - Keep away from direct sunlight and heat sources
    - Ensure proper ventilation for gas release
    - Use appropriate battery enclosure
    - Connect batteries in series/parallel as needed
    - Label all connections clearly
    """)

st.markdown("""
**Electrical Safety:**
- Install appropriate circuit breakers and fuses at all critical points
- Use properly rated cables and connectors
- Ensure all connections are tight and corrosion-free
- Install a battery disconnect switch for maintenance
- Label all components clearly
- Follow local electrical codes and regulations
- Consider hiring a certified electrician for installation

**Maintenance:**
- Check battery water levels monthly (for lead-acid batteries)
- Clean solar panels quarterly
- Inspect all connections semi-annually
- Monitor system performance regularly
- Keep records of maintenance activities
""")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# System Diagram
st.markdown('<div class="print-section">', unsafe_allow_html=True)
st.markdown('<div class="report-section">', unsafe_allow_html=True)
st.subheader(":material/build: System Connection Diagram")

recommended_current_diagram = float(regulator_specs['recommended_current'])

# Create a more intuitive visual diagram using columns and boxes
st.markdown("""
<style>
.diagram-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    border-radius: 8px;
    text-align: center;
    margin: 0.5rem 0;
    font-weight: bold;
}
.diagram-arrow {
    text-align: center;
    font-size: 2rem;
    color: #667eea;
    margin: 0.5rem 0;
}
.diagram-info {
    text-align: center;
    font-size: 0.9rem;
    color: #666;
    font-style: italic;
}
</style>
""", unsafe_allow_html=True)

# Solar Panels
st.markdown(f"""
<div class="diagram-box">
    ☀️ PANNEAUX SOLAIRES<br>
    <span style="font-size: 1.2rem;">{calc['num_panels']} × {calc['pv_power']}W = {calc['total_pv_power']}W</span>
</div>
<div class="diagram-info">Production quotidienne: {calc['total_pv_power'] * calc['sun_hours']:.0f} Wh</div>
<div class="diagram-arrow">↓</div>
<div class="diagram-info">Câble: {cable_specs['cable_section']:.1f}mm² | Protection: Fusible {cable_specs['fuse_rating']}A</div>
<div class="diagram-arrow">↓</div>
""", unsafe_allow_html=True)

# Charge Controller
st.markdown(f"""
<div class="diagram-box">
    ⚙️ RÉGULATEUR DE CHARGE<br>
    <span style="font-size: 1.2rem;">{calc['regulator_type']} - {math.ceil(recommended_current_diagram)}A</span>
</div>
<div class="diagram-info">Efficacité: {regulator_specs['efficiency']*100:.0f}%</div>
<div class="diagram-arrow">↓</div>
""", unsafe_allow_html=True)

# Battery Bank and Inverter in columns
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="diagram-box" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
        🔋 BANQUE DE BATTERIES<br>
        <span style="font-size: 1.1rem;">{calc['num_batteries']} × {calc['battery_capacity']}Ah {calc['battery_voltage']}V</span><br>
        <span style="font-size: 0.9rem;">Capacité totale: {calc['num_batteries'] * calc['battery_capacity']}Ah</span><br>
        <span style="font-size: 0.9rem;">Énergie: {calc['num_batteries'] * calc['battery_capacity'] * calc['battery_voltage']:.0f}Wh</span>
    </div>
    <div class="diagram-info">Autonomie: {calc['autonomy_days']} jours | DoD: {calc['discharge_depth']*100:.0f}%</div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="diagram-box" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
        🔄 ONDULEUR / CONVERTISSEUR<br>
        <span style="font-size: 1.2rem;">{calc['total_power']}W minimum</span><br>
        <span style="font-size: 0.9rem;">DC {calc['battery_voltage']}V → AC 230V</span>
    </div>
    <div class="diagram-info">Puissance de pointe: {calc['total_power'] * 1.5:.0f}W recommandé</div>
    """, unsafe_allow_html=True)

st.markdown('<div class="diagram-arrow">↓</div>', unsafe_allow_html=True)

# Loads
st.markdown(f"""
<div class="diagram-box" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
    ⚡ CHARGES ÉLECTRIQUES<br>
    <span style="font-size: 1.2rem;">Consommation: {calc['daily_energy']:.0f} Wh/jour</span><br>
    <span style="font-size: 0.9rem;">Puissance totale: {calc['total_power']}W</span>
</div>
<div class="diagram-info">{len(factory.get_equipments())} équipements connectés</div>
""", unsafe_allow_html=True)

# Legend
st.markdown("---")
st.markdown("""
**📋 Légende du Flux d'Énergie:**
1. ☀️ **Panneaux Solaires** → Captent l'énergie solaire et la convertissent en électricité DC
2. ⚙️ **Régulateur** → Contrôle la charge des batteries et optimise le rendement
3. 🔋 **Batteries** → Stockent l'énergie pour utilisation durant la nuit ou jours nuageux
4. 🔄 **Onduleur** → Convertit le courant DC en AC 230V pour les appareils électriques
5. ⚡ **Charges** → Vos équipements électriques alimentés par le système
""")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<div class="print-section">', unsafe_allow_html=True)
st.markdown("""
---
<div style="text-align: center; color: #666; padding: 2rem;">
    <p><strong>Solar Solution</strong> - Professional Solar System Design Tool</p>
    <p>Report generated on {}</p>
    <p style="font-size: 0.9rem;">
        :material/warning: This report is for reference only. Please consult with a certified solar installer 
        for final system design and installation.
    </p>
</div>
""".format(datetime.now().strftime('%B %d, %Y at %H:%M')), unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Action buttons (not printed)
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button(":material/home: " + t.get("nav_home", "Back to Home"), width="stretch", key="action_home_bottom"):
        st.switch_page("app.py")

with col2:
    if st.button(":material/bolt: " + t.get("nav_equipments", "Modify Equipment"), width="stretch", key="action_eq_bottom"):
        st.switch_page("pages/1_Equipments.py")

with col3:
    if st.button(":material/battery_charging_full: " + t.get("nav_calculations", "Modify Calculations"), width="stretch", key="action_calc_bottom"):
        st.switch_page("pages/2_Calculations.py")
