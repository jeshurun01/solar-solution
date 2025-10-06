"""
Page 1: Equipment Management
Add, edit, and manage electrical equipment
"""
import streamlit as st
import json
from pathlib import Path
import sys

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.equipment import EquipmentFactory
from utils.translations import load_translation
from utils.storage import load_equipment_library, get_library_categories, save_configuration, get_saved_configurations, load_configuration, delete_configuration
from utils.charts import create_consumption_pie_chart, create_power_time_chart, create_hourly_profile_chart

# Page configuration
st.set_page_config(
    page_title="Equipments - Solar Solution",
    page_icon=":material/bolt:",
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
        key="lang_selector_eq"
    )
    
    if lang != st.session_state.get("current_lang", "en"):
        st.session_state["current_lang"] = lang
        st.session_state["language"] = load_translation(lang)
        st.rerun()

# Top Navigation
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button(":material/home: " + t.get("nav_home", "Home"), width="stretch", key="nav_home_eq"):
        st.switch_page("app.py")
with col2:
    st.button(":material/bolt: " + t.get("nav_equipments", "Equipments"), width="stretch", disabled=True, type="primary", key="nav_eq_eq")
with col3:
    if st.button(":material/battery_charging_full: " + t.get("nav_calculations", "Calculations"), width="stretch", key="nav_calc_eq"):
        st.switch_page("pages/2_Calculations.py")
with col4:
    if st.button(":material/description: " + t.get("nav_report", "Report"), width="stretch", key="nav_report_eq"):
        st.switch_page("pages/3_Report.py")

st.markdown("---")

# Page Title
st.title(":material/bolt: " + t.get("nav_equipments", "Equipment Management"))

# Sidebar - Add Equipment
with st.sidebar:
    st.markdown("---")
    st.subheader(t["New Equipment"]["title"])
    
    name_input = st.text_input(t["New Equipment"]["name"], key="new_eq_name")
    power_input = st.number_input(t["New Equipment"]["power"], min_value=1, value=100, step=1, key="new_eq_power")
    time_input = st.number_input(t["New Equipment"]["time"], min_value=0.1, value=1.0, step=0.1, key="new_eq_time", format="%.1f")
    
    # Hourly schedule
    with st.expander(t.get("New Equipment", {}).get("schedule", "Schedule"), expanded=False):
        start_hour_input = st.slider(
            t.get("New Equipment", {}).get("start_hour", "Start hour"),
            min_value=0,
            max_value=23,
            value=0,
            key="new_eq_start"
        )
    
    if st.button(t["New Equipment"]["add button"], type="primary", width="stretch", key="add_equipment_btn"):
        # Validation
        if not name_input.strip():
            st.error(t["Validation"]["name_empty"])
        elif power_input <= 0:
            st.error(t["Validation"]["power_invalid"])
        elif time_input <= 0:
            st.error(t["Validation"]["time_invalid"])
        else:
            try:
                factory.add_equipment(
                    name=name_input,
                    power=int(power_input),
                    time=float(time_input),
                    start_hour=int(start_hour_input)
                )
                st.success(t["New Equipment"]["success message"].format(
                    name=name_input,
                    power=int(power_input),
                    time=float(time_input)
                ))
                st.rerun()
            except ValueError as e:
                st.error(str(e))

# Sidebar - Edit Equipment
with st.sidebar:
    st.markdown("---")
    st.subheader(t["Edit Equipment"]["title"])
    
    if not factory.is_empty():
        equipment_names = [eq.name for eq in factory.get_equipments()]
        selected_equipment_name = st.selectbox(
            t["Edit Equipment"]["select"],
            equipment_names,
            key="edit_eq_select"
        )
        
        if selected_equipment_name:
            eq_to_edit = factory.get_equipment_by_name(selected_equipment_name)
            
            new_name = st.text_input(t["New Equipment"]["name"], value=eq_to_edit.name, key="edit_eq_name")
            new_power = st.number_input(t["New Equipment"]["power"], min_value=1, value=eq_to_edit.power, step=1, key="edit_eq_power")
            new_time = st.number_input(t["New Equipment"]["time"], min_value=0.1, value=float(eq_to_edit.time), step=0.1, key="edit_eq_time", format="%.1f")
            
            with st.expander(t.get("New Equipment", {}).get("schedule", "Schedule"), expanded=False):
                new_start_hour = st.slider(
                    t.get("New Equipment", {}).get("start_hour", "Start hour"),
                    min_value=0,
                    max_value=23,
                    value=eq_to_edit.start_hour,
                    key="edit_eq_start"
                )
            
            if st.button(t["Edit Equipment"]["edit button"], type="secondary", width="stretch", key="edit_equipment_btn"):
                if not new_name.strip():
                    st.error(t["Validation"]["name_empty"])
                elif new_power <= 0:
                    st.error(t["Validation"]["power_invalid"])
                elif new_time <= 0:
                    st.error(t["Validation"]["time_invalid"])
                else:
                    try:
                        factory.edit_equipment(
                            old_name=selected_equipment_name,
                            new_name=new_name,
                            new_power=int(new_power),
                            new_time=float(new_time),
                            new_start_hour=int(new_start_hour)
                        )
                        st.success(t["Edit Equipment"]["success message"].format(name=new_name))
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
    else:
        st.info("No equipment to edit")

# Sidebar - Equipment Library
with st.sidebar:
    st.markdown("---")
    st.subheader(t["Library"]["title"])
    
    library = load_equipment_library()
    categories = get_library_categories(library, st.session_state.get("current_lang", "en"))
    
    if categories:
        category_options = {cat_data["name"]: cat_id for cat_id, cat_data in categories.items()}
        selected_category_name = st.selectbox(
            t["Library"]["category"],
            list(category_options.keys()),
            format_func=lambda x: f"{categories[category_options[x]]['icon']} {x}",
            key="lib_category"
        )
        
        selected_category_id = category_options[selected_category_name]
        category = categories[selected_category_id]
        
        if category["items"]:
            item_options = {item.get("name", "Unknown"): item for item in category["items"]}
            selected_item_name = st.selectbox(
                t["Library"]["select_equipment"],
                list(item_options.keys()),
                key="lib_item"
            )
            
            selected_item = item_options[selected_item_name]
            
            # Show description
            lang = st.session_state.get("current_lang", "en")
            description = selected_item.get(f"description_{lang}", selected_item.get("description_en", ""))
            if description:
                st.info(f"**{t['Library']['description']}:** {description}")
            
            # Show specs
            st.markdown(f"**{t['Library']['specifications']}:**")
            st.markdown(f"- {t['New Equipment']['power']}: {selected_item.get('power', 0)} W")
            st.markdown(f"- {t['New Equipment']['time']}: {selected_item.get('time', 0)} h")
            
            if st.button(t["Library"]["add_from_library"], width="stretch", key="add_from_lib_btn"):
                try:
                    factory.add_equipment(
                        name=selected_item.get("name", "Unknown"),
                        power=int(selected_item.get("power", 0)),
                        time=float(selected_item.get("time", 0)),
                        start_hour=int(selected_item.get("start_hour", 0))
                    )
                    st.success(f":material/check_circle: {selected_item.get('name', 'Unknown')} added!")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

# Sidebar - Actions
with st.sidebar:
    st.markdown("---")
    st.subheader(t.get("Actions", {}).get("title", "Actions"))
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(":material/list: " + t.get("Actions", {}).get("sample", "Sample"), width="stretch", key="sample_data_btn"):
            factory.delete_all_equipments()
            factory.add_equipment(name="Laptop", power=65, time=4, start_hour=9)
            factory.add_equipment(name="Television", power=150, time=8, start_hour=18)
            factory.add_equipment(name="Light", power=80, time=5, start_hour=18)
            factory.add_equipment(name="Fridge", power=150, time=24, start_hour=0)
            factory.add_equipment(name="Pump", power=750, time=3, start_hour=6)
            st.success("Sample data loaded!")
            st.rerun()
    
    with col2:
        if st.button(":material/delete: " + t.get("Actions", {}).get("delete_all", "Delete All"), width="stretch", key="delete_all_btn"):
            if not factory.is_empty():
                factory.delete_all_equipments()
                st.success("All equipment deleted!")
                st.rerun()
            else:
                st.warning("No equipment to delete")

# Main content
if factory.is_empty():
    st.info("👈 Add equipment using the sidebar to get started!")
else:
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label=":material/power: Total Equipment",
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
            value=f"{factory.total_energy_consumption():.2f} Wh",
            delta=f"{factory.total_energy_consumption()/1000:.2f} kWh"
        )
    
    with col4:
        avg_power = factory.total_energy_consumption() / 24
        st.metric(
            label=":material/lightbulb: Average Power",
            value=f"{avg_power:.0f} W"
        )
    
    st.markdown("---")
    
    # Equipment List
    st.subheader(":material/list: Equipment List")
    df = factory.df_datas()
    st.dataframe(df, width="stretch", hide_index=True)
    
    # Delete individual equipment
    with st.expander(":material/delete: " + t["Delete Equipment"]["title"]):
        equipment_names = [eq.name for eq in factory.get_equipments()]
        selected_to_delete = st.selectbox(
            t["Delete Equipment"]["select"],
            equipment_names,
            key="delete_eq_select"
        )
        
        if st.button(t["Delete Equipment"]["delete button"], type="secondary"):
            eq_to_delete = factory.get_equipment_by_name(selected_to_delete)
            factory.delete_equipment(eq_to_delete)
            st.success(f":material/check_circle: {selected_to_delete} deleted!")
            st.rerun()
    
    st.markdown("---")
    
    # Charts in tabs
    st.subheader(":material/analytics: Visualizations")
    tab1, tab2, tab3 = st.tabs([
        ":material/analytics: " + t["Charts"]["consumption_title"],
        ":material/trending_up: " + t["Charts"]["power_time_title"],
        "⏰ " + t.get("Hourly", {}).get("chart_title", "Hourly Profile")
    ])
    
    with tab1:
        fig1 = create_consumption_pie_chart(factory, t)
        st.plotly_chart(fig1, width="stretch")
    
    with tab2:
        fig2 = create_power_time_chart(factory, t)
        st.plotly_chart(fig2, width="stretch")
    
    with tab3:
        fig3 = create_hourly_profile_chart(factory, t)
        st.plotly_chart(fig3, width="stretch")
    
    st.markdown("---")
    
    # Save/Load Configuration
    st.subheader(":material/save: Save/Load Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Save Current Configuration**")
        config_name = st.text_input("Configuration name", key="save_config_name")
        if st.button(":material/save: Save", type="primary"):
            if config_name:
                save_configuration(config_name, factory)
                st.success(f"Configuration '{config_name}' saved!")
            else:
                st.error("Please enter a configuration name")
    
    with col2:
        st.markdown("**Load Configuration**")
        saved_configs = get_saved_configurations()
        if saved_configs:
            selected_config = st.selectbox("Select configuration", saved_configs, key="load_config_select")
            if st.button(":material/folder_open: Load"):
                equipments_data = load_configuration(selected_config)
                factory.delete_all_equipments()
                for eq_data in equipments_data:
                    factory.add_equipment(
                        name=eq_data["name"],
                        power=eq_data["power"],
                        time=eq_data["time"],
                        start_hour=eq_data.get("start_hour", 0)
                    )
                st.success(f"Configuration '{selected_config}' loaded!")
                st.rerun()
        else:
            st.info("No saved configurations")
