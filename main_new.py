"""
Solar Solution - Solar System Dimensioning Application

A Streamlit application for calculating solar panel and battery requirements
based on equipment energy consumption profiles.

Author: Solar Solution Team
License: MIT
"""

import streamlit as st
import pandas as pd
from pathlib import Path

# Import local modules
from models import Equipment, EquipmentFactory
from utils import (
    # Calculations
    battery_needed,
    panel_needed,
    calculate_system_cost,
    calculate_roi,
    calculate_co2_impact,
    calculate_regulator,
    calculate_cable_section,
    # Translations
    load_translation,
    # Storage
    save_configuration,
    load_configuration,
    get_saved_configurations,
    delete_configuration,
    load_equipment_library,
    get_library_categories,
    # Charts
    create_consumption_pie_chart,
    create_power_time_chart,
    create_hourly_profile_chart
)


# ============================================================================
# Session State Initialization
# ============================================================================

def initialize_session_state():
    """Initialize session state variables"""
    if "language" not in st.session_state:
        st.session_state["language"] = load_translation("en")
    
    if "equipments" not in st.session_state:
        st.session_state["equipments"] = EquipmentFactory()


# ============================================================================
# Helper Functions
# ============================================================================

def sample_data():
    """Load sample data for demonstration"""
    st.session_state["equipments"].delete_all_equipments()
    st.session_state["equipments"].add_equipment(name="Laptop", power=65, time=4, start_hour=9)
    st.session_state["equipments"].add_equipment(name="Television", power=150, time=8, start_hour=18)
    st.session_state["equipments"].add_equipment(name="Light", power=80, time=5, start_hour=18)
    st.session_state["equipments"].add_equipment(name="Fridge", power=150, time=24, start_hour=0)
    st.session_state["equipments"].add_equipment(name="Pump", power=750, time=3, start_hour=10)
    st.session_state["equipments"].add_equipment(name="Washing Machine", power=500, time=1.5, start_hour=10)


# ============================================================================
# Main Application
# ============================================================================

def main():
    """Main application entry point"""
    
    # Page configuration
    st.set_page_config(
        page_title="Solar Solution",
        page_icon=":material/solar_power:",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session
    initialize_session_state()
    
    # Get translation dictionary
    t = st.session_state["language"]
    factory = st.session_state["equipments"]
    
    # ========================================================================
    # Sidebar - Equipment Management
    # ========================================================================
    
    with st.sidebar:
        # Language selection
        lang = st.selectbox(
            ":material/language: Language", 
            ["en", "fr"],
            key="lang_selector"
        )
        st.session_state["language"] = load_translation(lang)
        t = st.session_state["language"]  # Update translation
        
        st.divider()
        
        # ====================================================================
        # Add New Equipment
        # ====================================================================
        with st.expander(t["New Equipment"]["title"], expanded=True):
            name = st.text_input(t["New Equipment"]["name"])
            power = st.number_input(
                t["New Equipment"]["power"],
                min_value=1,
                value=100,
                step=10
            )
            time = st.number_input(
                t["New Equipment"]["time"],
                min_value=0.1,
                value=1.0,
                step=0.1
            )
            start_hour = st.slider(
                t["Hourly"]["start_hour"],
                min_value=0,
                max_value=23,
                value=0,
                key="new_start_hour"
            )
            
            if st.button(t["New Equipment"]["add"], width="stretch"):
                if name.strip() == "":
                    st.error(t["Validation"]["name_required"])
                elif power <= 0:
                    st.error(t["Validation"]["power_positive"])
                elif time <= 0:
                    st.error(t["Validation"]["time_positive"])
                else:
                    try:
                        factory.add_equipment(name, int(power), time, start_hour)
                        st.success(t["New Equipment"]["success message"].format(
                            name=name, power=power, time=time
                        ))
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
        
        # ====================================================================
        # Edit Equipment
        # ====================================================================
        if not factory.is_empty():
            st.divider()
            with st.expander(t["Edit Equipment"]["title"], expanded=False):
                equipment_names = [eq.name for eq in factory.get_equipments()]
                selected_name = st.selectbox(
                    t["Edit Equipment"]["select"],
                    equipment_names,
                    key="edit_select"
                )
                
                if selected_name:
                    equipment = factory.get_equipment_by_name(selected_name)
                    
                    if equipment:
                        edit_name = st.text_input(
                            t["New Equipment"]["name"],
                            value=equipment.name,
                            key="edit_name"
                        )
                        edit_power = st.number_input(
                            t["New Equipment"]["power"],
                            min_value=1.0,
                            value=float(equipment.power),
                            step=10.0,
                            key="edit_power"
                        )
                        edit_time = st.number_input(
                            t["New Equipment"]["time"],
                            min_value=0.1,
                            value=equipment.time,
                            step=0.1,
                            key="edit_time"
                        )
                        edit_start_hour = st.slider(
                            t["Hourly"]["start_hour"],
                            min_value=0,
                            max_value=23,
                            value=equipment.start_hour,
                            key="edit_start_hour"
                        )
                        
                        if st.button(t["Edit Equipment"]["save"], width="stretch"):
                            if not edit_name or edit_name.strip() == "":
                                st.error(t["Validation"]["name_required"])
                            elif edit_power <= 0:
                                st.error(t["Validation"]["power_positive"])
                            elif edit_time <= 0:
                                st.error(t["Validation"]["time_positive"])
                            else:
                                try:
                                    factory.edit_equipment(
                                        equipment,
                                        edit_name,
                                        int(edit_power),
                                        edit_time,
                                        edit_start_hour
                                    )
                                    st.success(t["Edit Equipment"]["success message"].format(name=edit_name))
                                    st.rerun()
                                except ValueError as e:
                                    st.error(str(e))
        
        # ====================================================================
        # Equipment Library
        # ====================================================================
        st.divider()
        with st.expander(t["Library"]["title"], expanded=False):
            library = load_equipment_library()
            categories = get_library_categories(library, lang)
            
            if categories:
                category_list = list(categories.keys())
                
                selected_category = st.selectbox(
                    t["Library"]["category"],
                    options=category_list,
                    format_func=lambda x: f"{categories[x]['icon']} {categories[x]['name']}",
                    key="library_category"
                )
                
                if selected_category:
                    category_data = categories[selected_category]
                    items = category_data["items"]
                    
                    st.markdown(f"### {category_data['icon']} {category_data['name']}")
                    
                    if items:
                        equipment_options = {i: item["name"] for i, item in enumerate(items)}
                        
                        selected_idx = st.selectbox(
                            t["Library"]["select_equipment"],
                            options=list(equipment_options.keys()),
                            format_func=lambda x: equipment_options[x],
                            key="library_equipment"
                        )
                        
                        if selected_idx is not None:
                            selected_item = items[selected_idx]
                            
                            st.info(
                                f"**{t['Library']['specifications']}:**\n\n"
                                f"- {t['New Equipment']['power']}: {selected_item['power']} W\n"
                                f"- {t['New Equipment']['time']}: {selected_item['time']} h\n"
                                f"- {t['Hourly']['start_hour']}: {selected_item['start_hour']}h\n\n"
                                f"*{selected_item.get(f'description_{lang}', '')}*"
                            )
                            
                            if st.button(t["Library"]["add_from_library"], width="stretch"):
                                try:
                                    factory.add_equipment(
                                        selected_item["name"],
                                        selected_item["power"],
                                        selected_item["time"],
                                        selected_item["start_hour"]
                                    )
                                    st.success(t["New Equipment"]["success message"].format(
                                        name=selected_item["name"],
                                        power=selected_item["power"],
                                        time=selected_item["time"]
                                    ))
                                    st.rerun()
                                except ValueError as e:
                                    st.error(str(e))
                    else:
                        st.warning("Aucun équipement dans cette catégorie" if lang == "fr" 
                                 else "No equipment in this category")
            else:
                st.warning("Bibliothèque vide" if lang == "fr" else "Empty library")
        
        # ====================================================================
        # Actions
        # ====================================================================
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t["Actions"]["sample"], width="stretch"):
                sample_data()
                st.rerun()
        with col2:
            if st.button(t["Actions"]["delete_all"], width="stretch"):
                factory.delete_all_equipments()
                st.rerun()
        
        # ====================================================================
        # Delete Individual Equipment
        # ====================================================================
        if not factory.is_empty():
            st.divider()
            with st.expander(t["Actions"]["delete"], expanded=False):
                equipment_to_delete = st.selectbox(
                    t["Actions"]["select_equipment"],
                    factory.get_equipments(),
                    format_func=lambda x: x.name
                )
                if st.button(t["Actions"]["confirm_delete"], width="stretch"):
                    factory.delete_equipment(equipment_to_delete)
                    st.success(t["Actions"]["deleted"].format(name=equipment_to_delete.name))
                    st.rerun()
        
        # ====================================================================
        # Save/Load Configuration
        # ====================================================================
        if not factory.is_empty():
            st.divider()
            with st.expander(t["Storage"]["save_title"], expanded=False):
                config_name = st.text_input(t["Storage"]["config_name"])
                if st.button(t["Storage"]["save"], width="stretch"):
                    if config_name.strip():
                        save_configuration(config_name, factory)
                        st.success(t["Storage"]["saved"].format(name=config_name))
                    else:
                        st.error(t["Storage"]["name_required"])
        
        saved_configs = get_saved_configurations()
        if saved_configs:
            st.divider()
            with st.expander(t["Storage"]["load_title"], expanded=False):
                selected_config = st.selectbox(
                    t["Storage"]["select_config"],
                    saved_configs
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(t["Storage"]["load"], width="stretch"):
                        equipments_data = load_configuration(selected_config)
                        factory.delete_all_equipments()
                        for eq_data in equipments_data:
                            factory.add_equipment(
                                eq_data["name"],
                                eq_data["power"],
                                eq_data["time"],
                                eq_data.get("start_hour", 0)
                            )
                        st.success(t["Storage"]["loaded"].format(name=selected_config))
                        st.rerun()
                
                with col2:
                    if st.button(t["Storage"]["delete"], width="stretch"):
                        delete_configuration(selected_config)
                        st.success(t["Storage"]["deleted"].format(name=selected_config))
                        st.rerun()
    
    # ========================================================================
    # Main Content Area
    # ========================================================================
    
    st.title(":material/solar_power: " + t["title"])
    st.markdown(t["subtitle"])
    
    if factory.is_empty():
        st.info(t["Equipment"]["empty"])
        st.stop()
    
    # ========================================================================
    # Equipment List
    # ========================================================================
    
    with st.expander(t["Equipment"]["title"], expanded=True):
        df = factory.df_datas()
        st.dataframe(df, width="stretch", hide_index=True)
        
        # Export to CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=t["Storage"]["export_csv"],
            data=csv,
            file_name="solar_equipment.csv",
            mime="text/csv",
            width="stretch"
        )
    
    # ========================================================================
    # Energy Metrics
    # ========================================================================
    
    total_energy = factory.total_energy_consumption()
    total_power = factory.total_power()
    num_equipment = len(factory.get_equipments())
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label=f":material/bolt: {t['Results']['daily_energy']}",
            value=f"{total_energy:.2f} Wh",
            delta=f"{total_energy/1000:.2f} kWh"
        )
    
    with col2:
        st.metric(
            label=f":material/flash_on: {t['Results']['total_power']}",
            value=f"{total_power:.0f} W",
            delta=f"{num_equipment} {t['Equipment']['title']}"
        )
    
    with col3:
        avg_time = sum(eq.time for eq in factory.get_equipments()) / num_equipment
        st.metric(
            label=f":material/schedule: {t['Results']['avg_usage']}",
            value=f"{avg_time:.1f} h",
            delta=f"{(avg_time/24)*100:.1f}%"
        )
    
    st.divider()
    
    # ========================================================================
    # Battery and Solar Panel Calculations
    # ========================================================================
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f":material/battery_charging_full: {t['Battery']['title']}")
        
        battery_voltage = st.selectbox(
            t["Battery"]["voltage"],
            [12, 24, 48],
            index=1
        )
        battery_capacity = st.number_input(
            t["Battery"]["capacity"],
            min_value=10,
            value=200,
            step=10
        )
        autonomy_days = st.number_input(
            t["Battery"]["autonomy"],
            min_value=1,
            value=2,
            step=1
        )
        discharge_depth = st.slider(
            t["Battery"]["discharge_depth"],
            min_value=0.3,
            max_value=0.8,
            value=0.5,
            step=0.05
        )
        
        num_batteries = battery_needed(
            total_energy,
            battery_voltage,
            battery_capacity,
            autonomy_days,
            discharge_depth
        )
        
        st.metric(
            label=t["Battery"]["number_needed"],
            value=num_batteries,
            delta=f"{battery_voltage}V × {battery_capacity}Ah"
        )
        
        total_capacity_ah = num_batteries * battery_capacity
        total_capacity_wh = total_capacity_ah * battery_voltage
        
        st.info(
            f"**{t['Battery']['total_capacity']}:** {total_capacity_ah} Ah ({total_capacity_wh/1000:.2f} kWh)"
        )
    
    with col2:
        st.subheader(f":material/wb_sunny: {t['Solar Panels']['title']}")
        
        pv_power = st.number_input(
            t["Solar Panels"]["pv_power"],
            min_value=50,
            value=300,
            step=50
        )
        sun_hours = st.number_input(
            t["Solar Panels"]["sun_hours"],
            min_value=1.0,
            value=5.0,
            step=0.5
        )
        
        num_panels = panel_needed(total_energy, pv_power, sun_hours)
        
        st.metric(
            label=t["Solar Panels"]["number_needed"],
            value=num_panels,
            delta=f"{pv_power}W × {num_panels}"
        )
        
        total_pv_power = num_panels * pv_power
        daily_production = total_pv_power * sun_hours
        
        st.info(
            f"**{t['Solar Panels']['total_power']}:** {total_pv_power} W\n\n"
            f"**{t['Solar Panels']['daily_production']}:** {daily_production:.0f} Wh ({daily_production/1000:.2f} kWh)"
        )
    
    st.divider()
    
    # ========================================================================
    # Charts
    # ========================================================================
    
    st.subheader(f":material/bar_chart: {t['Charts']['title']}")
    
    tab1, tab2, tab3 = st.tabs([
        f":material/pie_chart: {t['Charts']['consumption_title']}",
        f":material/bar_chart: {t['Charts']['power_time_title']}",
        f":material/show_chart: {t['Hourly']['title']}"
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
    
    st.divider()
    
    # ========================================================================
    # Economic Analysis
    # ========================================================================
    
    with st.expander(f":material/payments: {t['Economics']['title']}", expanded=False):
        st.subheader(t["Economics"]["costs_title"])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            battery_unit_cost = st.number_input(
                t["Economics"]["battery_cost"],
                min_value=0.0,
                value=200.0,
                step=10.0
            )
            pv_unit_cost = st.number_input(
                t["Economics"]["panel_cost"],
                min_value=0.0,
                value=150.0,
                step=10.0
            )
        
        with col2:
            converter_cost = st.number_input(
                t["Economics"]["converter_cost"],
                min_value=0.0,
                value=300.0,
                step=50.0
            )
            regulator_cost = st.number_input(
                t["Economics"]["regulator_cost"],
                min_value=0.0,
                value=200.0,
                step=50.0
            )
        
        with col3:
            installation_cost = st.number_input(
                t["Economics"]["installation_cost"],
                min_value=0.0,
                value=500.0,
                step=100.0
            )
            electricity_price = st.number_input(
                t["Economics"]["electricity_price"],
                min_value=0.0,
                value=0.15,
                step=0.01
            )
        
        # Calculate costs
        costs = calculate_system_cost(
            num_batteries,
            battery_unit_cost,
            num_panels,
            pv_unit_cost,
            converter_cost,
            regulator_cost,
            installation_cost
        )
        
        # Calculate ROI
        roi_data = calculate_roi(
            costs["total"],
            total_energy / 1000,  # Convert to kWh
            electricity_price
        )
        
        # Calculate CO2 impact
        co2_data = calculate_co2_impact((total_energy / 1000) * 365)
        
        st.divider()
        
        # Display costs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label=t["Economics"]["battery_total"],
                value=f"€{costs['battery_total']:.2f}",
                delta=f"{num_batteries} × €{battery_unit_cost}"
            )
        
        with col2:
            st.metric(
                label=t["Economics"]["panel_total"],
                value=f"€{costs['pv_total']:.2f}",
                delta=f"{num_panels} × €{pv_unit_cost}"
            )
        
        with col3:
            st.metric(
                label=t["Economics"]["equipment_total"],
                value=f"€{costs['converter'] + costs['regulator']:.2f}",
                delta=f"€{converter_cost} + €{regulator_cost}"
            )
        
        with col4:
            st.metric(
                label=t["Economics"]["total_cost"],
                value=f"€{costs['total']:.2f}",
                delta=f"+ €{installation_cost} " + t["Economics"]["installation"]
            )
        
        st.divider()
        
        # Display ROI
        st.subheader(t["Economics"]["roi_title"])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label=t["Economics"]["daily_savings"],
                value=f"€{roi_data['daily']:.2f}",
                delta="/ " + t["Economics"]["day"]
            )
        
        with col2:
            st.metric(
                label=t["Economics"]["monthly_savings"],
                value=f"€{roi_data['monthly']:.2f}",
                delta="/ " + t["Economics"]["month"]
            )
        
        with col3:
            st.metric(
                label=t["Economics"]["annual_savings"],
                value=f"€{roi_data['annual']:.2f}",
                delta="/ " + t["Economics"]["year"]
            )
        
        with col4:
            roi_text = f"{roi_data['roi_years']:.1f} " + t["Economics"]["years"] \
                       if roi_data['roi_years'] != float('inf') else "∞"
            st.metric(
                label=t["Economics"]["payback_period"],
                value=roi_text,
                delta=t["Economics"]["to_break_even"]
            )
        
        st.divider()
        
        # Display CO2 impact
        st.subheader(t["Economics"]["co2_title"])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label=t["Economics"]["co2_avoided"],
                value=f"{co2_data['co2_kg']:.0f} kg",
                delta=f"{co2_data['co2_tons']:.2f} " + t["Economics"]["tons"]
            )
        
        with col2:
            st.metric(
                label=t["Economics"]["trees_equivalent"],
                value=f"{co2_data['trees']:.0f}",
                delta=t["Economics"]["trees"] + " / " + t["Economics"]["year"]
            )
        
        with col3:
            # Additional context
            st.info(f":material/lightbulb: {t['Economics']['co2_note']}")
    
    # ========================================================================
    # Regulator and Wiring
    # ========================================================================
    
    with st.expander(f":material/cable: {t['Regulator']['title']}", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(t["Regulator"]["subtitle"])
            
            regulator_type = st.radio(
                t["Regulator"]["type"],
                ["MPPT", "PWM"],
                horizontal=True
            )
            
            reg_specs = calculate_regulator(
                total_pv_power,
                battery_voltage,
                regulator_type
            )
            
            st.metric(
                label=t["Regulator"]["nominal_current"],
                value=f"{reg_specs['nominal_current']:.1f} A",
                delta=f"{reg_specs['efficiency']*100:.0f}% " + t["Regulator"]["efficiency"]
            )
            
            st.metric(
                label=t["Regulator"]["recommended_current"],
                value=f"{reg_specs['recommended_current']:.1f} A",
                delta="+25% " + t["Regulator"]["safety_margin"]
            )
            
            st.info(
                f"**{t['Regulator']['specifications']}:**\n\n"
                f"- {t['Regulator']['type']}: {reg_specs['type']}\n"
                f"- {t['Regulator']['power']}: {reg_specs['nominal_power']} W\n"
                f"- {t['Regulator']['voltage']}: {battery_voltage} V"
            )
        
        with col2:
            st.subheader(t["Wiring"]["title"])
            
            cable_length = st.number_input(
                t["Wiring"]["length"],
                min_value=1.0,
                value=10.0,
                step=1.0
            )
            
            max_drop = st.slider(
                t["Wiring"]["max_drop"],
                min_value=1.0,
                max_value=5.0,
                value=3.0,
                step=0.5
            )
            
            cable_specs = calculate_cable_section(
                float(reg_specs['recommended_current']),
                cable_length,
                battery_voltage,
                max_drop
            )
            
            st.metric(
                label=t["Wiring"]["section"],
                value=f"{cable_specs['cable_section']:.1f} mm²",
                delta=f"{cable_specs['actual_drop_percent']:.2f}% " + t["Wiring"]["drop"]
            )
            
            st.metric(
                label=t["Wiring"]["fuse_rating"],
                value=f"{cable_specs['fuse_rating']} A",
                delta=t["Wiring"]["protection"]
            )
            
            st.info(
                f"**{t['Wiring']['specifications']}:**\n\n"
                f"- {t['Wiring']['section']}: {cable_specs['cable_section']:.1f} mm²\n"
                f"- {t['Wiring']['current']}: {cable_specs['current']:.1f} A\n"
                f"- {t['Wiring']['actual_drop']}: {cable_specs['actual_drop_volts']:.2f} V ({cable_specs['actual_drop_percent']:.2f}%)"
            )


# ============================================================================
# Run Application
# ============================================================================

if __name__ == "__main__":
    main()
