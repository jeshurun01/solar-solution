"""
Solar Solution - Multi-Page Application
Main entry point with navigation
"""
import streamlit as st
import json
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Solar Solution",
    page_icon=":material/wb_sunny:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load translation
def load_translation(language_code: str):
    """Load translation file"""
    with open(f"locals/{language_code}.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Initialize session state
if "language" not in st.session_state:
    st.session_state["language"] = load_translation("en")
    
if "current_lang" not in st.session_state:
    st.session_state["current_lang"] = "en"

# Language selector in sidebar
with st.sidebar:
    st.markdown("### :material/settings: Settings")
    lang = st.selectbox(
        "🌍 Language", 
        ["en", "fr"],
        index=0 if st.session_state["current_lang"] == "en" else 1,
        key="lang_selector"
    )
    
    if lang != st.session_state["current_lang"]:
        st.session_state["current_lang"] = lang
        st.session_state["language"] = load_translation(lang)
        st.rerun()

t = st.session_state["language"]

# Top Navigation Menu
st.markdown("""
<style>
    .nav-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
    }
    .nav-button {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        margin: 0.25rem;
        border-radius: 0.3rem;
        text-decoration: none;
        color: #262730;
        background-color: white;
        border: 1px solid #e0e0e0;
        transition: all 0.3s;
    }
    .nav-button:hover {
        background-color: #ff4b4b;
        color: white;
        border-color: #ff4b4b;
    }
    .nav-button.active {
        background-color: #ff4b4b;
        color: white;
        border-color: #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)

# Navigation
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button(":material/home: " + t.get("nav_home", "Home"), width="stretch", type="primary", key="nav_home_home"):
        st.session_state["current_page"] = "home"
        
with col2:
    if st.button(":material/bolt: " + t.get("nav_equipments", "Equipments"), width="stretch", key="nav_eq_home"):
        st.session_state["current_page"] = "equipments"
        st.switch_page("pages/1_Equipments.py")
        
with col3:
    if st.button(":material/battery_charging_full: " + t.get("nav_calculations", "Calculations"), width="stretch", key="nav_calc_home"):
        st.session_state["current_page"] = "calculations"
        st.switch_page("pages/2_Calculations.py")
        
with col4:
    if st.button(":material/description: " + t.get("nav_report", "Report"), width="stretch", key="nav_report_home"):
        st.session_state["current_page"] = "report"
        st.switch_page("pages/3_Report.py")

st.markdown("---")

# Home Page Content
st.title(":material/wb_sunny: " + t["title"])
st.markdown(f"### {t.get('subtitle', 'Solar System Dimensioning Tool')}")

# Welcome section
st.markdown("""
<div style="background-color: #f0f8ff; padding: 2rem; border-radius: 0.5rem; border-left: 5px solid #1f77b4;">
    <h2>👋 Welcome to Solar Solution</h2>
    <p style="font-size: 1.1rem;">
        A comprehensive tool for designing and sizing photovoltaic solar systems. 
        This application helps you calculate the right number of batteries, solar panels, 
        and other components for your solar installation.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Feature cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### :material/bolt: Equipment Management")
    st.markdown("""
    <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <p>Add and manage all your electrical equipment with power consumption, 
        usage time, and hourly schedules.</p>
        <ul>
            <li>Pre-configured library</li>
            <li>Custom equipment</li>
            <li>Hourly profiles</li>
            <li>Edit & delete</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("### :material/battery_charging_full: System Calculations")
    st.markdown("""
    <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <p>Calculate the exact specifications for your solar system based on 
        your consumption profile.</p>
        <ul>
            <li>Battery sizing</li>
            <li>Solar panel count</li>
            <li>Charge controller</li>
            <li>Cable sections</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("### :material/description: Printable Report")
    st.markdown("""
    <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <p>Generate a comprehensive report with all calculations, charts, 
        and recommendations.</p>
        <ul>
            <li>Complete summary</li>
            <li>Visual charts</li>
            <li>Economic analysis</li>
            <li>Print-ready format</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Quick stats if equipments exist
from models.equipment import EquipmentFactory

if "equipments" not in st.session_state:
    st.session_state["equipments"] = EquipmentFactory()

factory = st.session_state["equipments"]

if not factory.is_empty():
    st.markdown("### :material/analytics: Quick Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label=":material/power: Equipment Count",
            value=len(factory.get_equipments())
        )
    
    with col2:
        st.metric(
            label=":material/bolt: Total Power",
            value=f"{factory.total_power():.0f} W"
        )
    
    with col3:
        st.metric(
            label=":material/battery_charging_full: Daily Energy",
            value=f"{factory.total_energy_consumption():.2f} Wh"
        )
    
    with col4:
        st.metric(
            label=":material/lightbulb: Average Power",
            value=f"{factory.total_energy_consumption()/24:.0f} W"
        )

# Getting Started
st.markdown("---")
st.markdown("### 🚀 Getting Started")

st.markdown("""
1. **:material/bolt: Go to Equipments page** - Add your electrical devices
2. **:material/battery_charging_full: Go to Calculations page** - Configure system parameters
3. **:material/description: Generate Report** - Print your complete system design

Use the navigation buttons at the top to switch between pages.
""")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>Solar Solution v0.4.0 | Made with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)
