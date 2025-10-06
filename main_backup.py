import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime


# @st.cache_data(ttl=360)
def load_translation(language_code: str):
    with open(f"locals/{language_code}.json", "r") as f:
        return json.load(f)

# # Trigger the change language
# def change_language(lang: str):
#     st.session_state["language"] = load_translation(lang)

# Add The language to the session
if "language" not in st.session_state:
    st.session_state["language"] = load_translation("en")

# Sidebar
with st.sidebar:
    lang = st.selectbox("lang.", ["en", "fr"], )
    st.session_state["language"] = load_translation(lang)
    t = st.session_state["language"]

class Equipment:
    def __init__(self, name: str, power: int, time: float, start_hour: int = 0, end_hour: int | None = None) -> None:
        self.name = name
        self.power = power
        self.time = time
        self.start_hour = start_hour
        # If end_hour not specified, calculate from start_hour + time
        if end_hour is None:
            self.end_hour = int((start_hour + time) % 24)
        else:
            self.end_hour = end_hour

    def daily_energy_consumption(self) -> float:
        """Get the daily energy consumption of the equipment."""
        return self.power * self.time
    
    def get_hourly_consumption(self) -> list[float]:
        """Get hourly consumption for 24 hours"""
        hourly = [0.0] * 24
        
        # Simple distribution: divide power equally across usage hours
        if self.time > 0:
            hours_used = self.time
            current_hour = self.start_hour
            remaining_time = hours_used
            
            while remaining_time > 0:
                if remaining_time >= 1:
                    hourly[current_hour % 24] += self.power
                    remaining_time -= 1
                else:
                    # Partial hour
                    hourly[current_hour % 24] += self.power * remaining_time
                    remaining_time = 0
                current_hour += 1
        
        return hourly

    def __repr__(self) -> str:
        return f"Equipment(name='{self.name}', power={self.power}, time={self.time}, start_hour={self.start_hour})"

    def __str__(self) -> str:
        return f"{self.name} ({self.power} W, {self.time} h, {self.start_hour}h-{self.end_hour}h)"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Equipment):
            return NotImplemented
        return self.name == other.name


class EquipmentFactory:
    def __init__(self):
        self._equipments = []

    def add_equipment(self, name: str, power: int, time: float, start_hour: int = 0) -> None:
        """Add an equipment to the factory."""
        if Equipment(name, power, time, start_hour) in self._equipments:
            raise ValueError(t["Equipment"]["error"].format(name=name))
        self._equipments.append(Equipment(name, power, time, start_hour))

    def get_equipments(self) -> list[Equipment]:
        return self._equipments

    def df_datas(self) -> pd.DataFrame:
        """Get all equipments from the factory."""
        datas = {
            "Name": [],
            "Power": [],
            "Usage Time": [],
            "Schedule": [],
            "Energie": []
        }
        for equipment in self._equipments:
            datas["Name"].append(equipment.name)
            datas["Power"].append(equipment.power)
            datas["Usage Time"].append(equipment.time)
            datas["Schedule"].append(f"{equipment.start_hour}h-{equipment.end_hour}h")
            datas["Energie"].append(equipment.daily_energy_consumption())

        return pd.DataFrame(datas)

    def total_energy_consumption(self) -> float:
        """Get the total energy consumption of all equipments in the factory."""
        return sum(equipment.daily_energy_consumption() for equipment in self._equipments)

    def total_power(self) -> float:
        """Get the total power of all equipments in the factory."""
        return sum(equipment.power for equipment in self._equipments)
    
    def get_hourly_profile(self) -> list[float]:
        """Get the total hourly consumption profile for all equipments"""
        hourly_total = [0.0] * 24
        for equipment in self._equipments:
            hourly = equipment.get_hourly_consumption()
            for i in range(24):
                hourly_total[i] += hourly[i]
        return hourly_total

    def delete_equipment(self, equipment: Equipment) -> None:
        """Delete an equipment from the factory."""
        self._equipments.remove(equipment)

    def delete_all_equipments(self) -> None:
        """Delete all equipments from the factory."""
        self._equipments.clear()

    def is_empty(self) -> bool:
        return len(self._equipments) == 0

    def edit_equipment(self, old_equipment: Equipment, new_name: str, new_power: int, new_time: float, new_start_hour: int = 0) -> None:
        """Edit an existing equipment"""
        if old_equipment in self._equipments:
            index = self._equipments.index(old_equipment)
            self._equipments[index] = Equipment(new_name, new_power, new_time, new_start_hour)
        else:
            raise ValueError(f"Equipment {old_equipment.name} not found.")

    def get_equipment_by_name(self, name: str) -> Equipment | None:
        """Get an equipment by its name"""
        for equipment in self._equipments:
            if equipment.name == name:
                return equipment
        return None


# Storage functions
STORAGE_DIR = Path("saved_configs")
STORAGE_DIR.mkdir(exist_ok=True)


def save_configuration(name: str, factory: EquipmentFactory) -> None:
    """Save current equipment configuration to JSON file"""
    config = {
        "name": name,
        "timestamp": datetime.now().isoformat(),
        "equipments": [
            {
                "name": eq.name,
                "power": eq.power,
                "time": eq.time,
                "start_hour": eq.start_hour
            }
            for eq in factory.get_equipments()
        ]
    }
    file_path = STORAGE_DIR / f"{name}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def load_configuration(name: str) -> list[dict]:
    """Load equipment configuration from JSON file"""
    file_path = STORAGE_DIR / f"{name}.json"
    with open(file_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config["equipments"]


def get_saved_configurations() -> list[str]:
    """Get list of saved configuration names"""
    return [f.stem for f in STORAGE_DIR.glob("*.json")]


def delete_configuration(name: str) -> None:
    """Delete a saved configuration"""
    file_path = STORAGE_DIR / f"{name}.json"
    if file_path.exists():
        file_path.unlink()


# Equipment library functions
@st.cache_data
def load_equipment_library() -> dict:
    """Load equipment library from JSON file"""
    library_path = Path("equipment_library.json")
    if library_path.exists():
        with open(library_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"categories": {}}


def get_library_categories(library: dict, lang: str) -> dict:
    """Get categories with translated names"""
    categories = {}
    for cat_id, cat_data in library.get("categories", {}).items():
        name_key = f"name_{lang}"
        categories[cat_id] = {
            "name": cat_data.get(name_key, cat_data.get("name_en", cat_id)),
            "icon": cat_data.get("icon", ""),
            "items": cat_data.get("items", [])
        }
    return categories


# Chart functions
def create_consumption_pie_chart(factory: EquipmentFactory, t: dict) -> go.Figure:
    """Create a pie chart showing energy consumption by equipment"""
    df = factory.df_datas()
    fig = px.pie(
        df,
        values="Energie",
        names="Name",
        title=t["Charts"]["consumption_subtitle"],
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=True, height=400)
    return fig


def create_power_time_chart(factory: EquipmentFactory, t: dict) -> go.Figure:
    """Create a bar chart showing power and time for each equipment"""
    df = factory.df_datas()
    
    fig = go.Figure()
    
    # Add power bars
    fig.add_trace(go.Bar(
        name=t["Charts"]["power"],
        x=df["Name"],
        y=df["Power"],
        marker_color='lightblue',
        yaxis='y',
        offsetgroup=1
    ))
    
    # Add time bars
    fig.add_trace(go.Bar(
        name=t["Charts"]["time"],
        x=df["Name"],
        y=df["Usage Time"],
        marker_color='lightcoral',
        yaxis='y2',
        offsetgroup=2
    ))
    
    fig.update_layout(
        title=t["Charts"]["power_time_title"],
        xaxis=dict(title=t["Charts"]["equipment"]),
        yaxis=dict(title=t["Charts"]["power"], side='left'),
        yaxis2=dict(title=t["Charts"]["time"], overlaying='y', side='right'),
        barmode='group',
        height=400,
        legend=dict(x=0.01, y=0.99)
    )
    
    return fig


def create_hourly_profile_chart(factory: EquipmentFactory, t: dict) -> go.Figure:
    """Create a line chart showing hourly consumption profile"""
    hourly_profile = factory.get_hourly_profile()
    hours = list(range(24))
    
    fig = go.Figure()
    
    # Add area chart for total consumption
    fig.add_trace(go.Scatter(
        x=hours,
        y=hourly_profile,
        mode='lines',
        name=t["Hourly"]["consumption"],
        fill='tozeroy',
        line=dict(color='rgb(255, 127, 14)', width=3),
        hovertemplate='<b>%{x}h</b><br>%{y:.0f} W<extra></extra>'
    ))
    
    # Add individual equipment traces
    colors = px.colors.qualitative.Set2
    for idx, equipment in enumerate(factory.get_equipments()):
        hourly = equipment.get_hourly_consumption()
        fig.add_trace(go.Scatter(
            x=hours,
            y=hourly,
            mode='lines',
            name=equipment.name,
            line=dict(color=colors[idx % len(colors)], width=1, dash='dot'),
            visible='legendonly',  # Hidden by default
            hovertemplate=f'<b>{equipment.name}</b><br>%{{x}}h: %{{y:.0f}} W<extra></extra>'
        ))
    
    # Calculate peak and average
    peak_consumption = max(hourly_profile)
    avg_consumption = sum(hourly_profile) / 24
    peak_hour = hourly_profile.index(peak_consumption)
    
    # Add peak line
    fig.add_hline(
        y=peak_consumption,
        line_dash="dash",
        line_color="red",
        annotation_text=f"{t['Hourly']['peak_consumption']}: {peak_consumption:.0f}W @ {peak_hour}h",
        annotation_position="top right"
    )
    
    # Add average line
    fig.add_hline(
        y=avg_consumption,
        line_dash="dash",
        line_color="green",
        annotation_text=f"{t['Hourly']['average_consumption']}: {avg_consumption:.0f}W",
        annotation_position="bottom right"
    )
    
    fig.update_layout(
        title=t["Hourly"]["chart_title"],
        xaxis=dict(
            title=t["Hourly"]["hour"],
            tickmode='linear',
            tick0=0,
            dtick=2,
            range=[-0.5, 23.5]
        ),
        yaxis=dict(title=t["Hourly"]["consumption"]),
        height=500,
        hovermode='x unified',
        legend=dict(x=0.01, y=0.99)
    )
    
    return fig


def sample() -> None:
    """Dammy data"""
    st.session_state["equipments"].delete_all_equipments()
    st.session_state["equipments"].add_equipment(name="Laptop", power=65, time=4)
    st.session_state["equipments"].add_equipment(name="Television", power=150, time=8)
    st.session_state["equipments"].add_equipment(name="Light", power=80, time=5)
    st.session_state["equipments"].add_equipment(name="Fridge", power=150, time=12)
    st.session_state["equipments"].add_equipment(name="Pump", power=750, time=3)
    st.session_state["equipments"].add_equipment(name="Washing Machine", power=500, time=1.5)


def capacity(energy: float, autonomy: float, discharge_factor: float, batterie_voltage: int) -> int:
    return round((energy * autonomy) / (discharge_factor * batterie_voltage))


def autonomy_calculator(energy:float, bat_capacity: int, discharge_factor: float, batterie_voltage: int) -> float:
    return discharge_factor * batterie_voltage * bat_capacity / energy


# Economic calculations
def calculate_system_cost(
    num_batteries: int,
    battery_unit_cost: float,
    num_pv: int,
    pv_unit_cost: float,
    converter_cost: float,
    regulator_cost: float,
    installation_cost: float
) -> dict:
    """Calculate total system costs breakdown"""
    battery_total = num_batteries * battery_unit_cost
    pv_total = num_pv * pv_unit_cost
    total = battery_total + pv_total + converter_cost + regulator_cost + installation_cost
    
    return {
        "battery_total": battery_total,
        "pv_total": pv_total,
        "converter": converter_cost,
        "regulator": regulator_cost,
        "installation": installation_cost,
        "total": total
    }


def calculate_roi(
    total_cost: float,
    daily_energy_kwh: float,
    electricity_price_per_kwh: float
) -> dict:
    """Calculate return on investment and savings"""
    daily_savings = daily_energy_kwh * electricity_price_per_kwh
    monthly_savings = daily_savings * 30
    annual_savings = daily_savings * 365
    
    roi_years = total_cost / annual_savings if annual_savings > 0 else float('inf')
    
    return {
        "daily": daily_savings,
        "monthly": monthly_savings,
        "annual": annual_savings,
        "roi_years": roi_years
    }


def calculate_co2_impact(annual_energy_kwh: float) -> dict:
    """Calculate CO2 emissions avoided
    Average: 0.5 kg CO2 per kWh (varies by country)
    1 tree absorbs ~21 kg CO2 per year
    """
    co2_avoided_kg = annual_energy_kwh * 0.5
    trees_equivalent = co2_avoided_kg / 21
    
    return {
        "co2_kg": co2_avoided_kg,
        "co2_tons": co2_avoided_kg / 1000,
        "trees": trees_equivalent
    }


# Regulator and wiring calculations
def calculate_regulator(pv_power: float, battery_voltage: int, regulator_type: str = "MPPT") -> dict:
    """Calculate charge controller specifications
    
    Args:
        pv_power: Total PV power in watts
        battery_voltage: Battery bank voltage (12, 24, or 48V)
        regulator_type: MPPT or PWM
    """
    # Calculate current with 25% safety margin
    nominal_current = pv_power / battery_voltage
    recommended_current = nominal_current * 1.25
    
    # MPPT is more efficient (can handle higher PV voltage)
    # PWM requires PV voltage close to battery voltage
    efficiency = 0.98 if regulator_type == "MPPT" else 0.85
    
    return {
        "nominal_current": nominal_current,
        "recommended_current": recommended_current,
        "nominal_power": pv_power,
        "efficiency": efficiency,
        "type": regulator_type
    }


def calculate_cable_section(current: float, length: float, voltage: int, max_drop_percent: float = 3.0) -> dict:
    """Calculate cable section based on voltage drop
    
    Args:
        current: Current in amperes
        length: Cable length in meters (one-way)
        voltage: System voltage
        max_drop_percent: Maximum acceptable voltage drop (default 3%)
    
    Returns:
        dict with cable section, actual drop, and fuse rating
    """
    # Resistivity of copper at 20°C (Ω·mm²/m)
    rho_copper = 0.01724
    
    # Maximum acceptable voltage drop
    max_drop_volts = voltage * (max_drop_percent / 100)
    
    # Calculate minimum cable section: S = (2 * ρ * I * L) / ΔV
    # Factor 2 because current goes out and returns
    min_section = (2 * rho_copper * current * length) / max_drop_volts
    
    # Standard cable sections (mm²)
    standard_sections = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240]
    
    # Find the next standard section
    cable_section = next((s for s in standard_sections if s >= min_section), 240)
    
    # Calculate actual voltage drop with selected section
    actual_drop_volts = (2 * rho_copper * current * length) / cable_section
    actual_drop_percent = (actual_drop_volts / voltage) * 100
    
    # Fuse rating: 1.25 × nominal current, rounded up
    fuse_rating = round(current * 1.25 / 5) * 5  # Round to nearest 5A
    if fuse_rating < 5:
        fuse_rating = 5
    
    return {
        "cable_section": cable_section,
        "actual_drop_volts": actual_drop_volts,
        "actual_drop_percent": actual_drop_percent,
        "fuse_rating": fuse_rating,
        "current": current
    }


# Add the Equipement factory to the session
if "equipments" not in st.session_state:
    st.session_state["equipments"] = EquipmentFactory()
    st.rerun()


# Sidebar
with st.sidebar:
    st.divider()
    
    # Add Equipment
    with st.expander(t["New Equipment"]["title"]):
        name = st.text_input(t["New Equipment"]["name"])
        power = st.number_input(t["New Equipment"]["power"], value=100, min_value=1, step=1)
        time = st.number_input(t["New Equipment"]["time"], value=1.0, step=0.1, min_value=0.1)
        start_hour = st.slider(t["Hourly"]["start_hour"], min_value=0, max_value=23, value=8)
        if st.button(t["New Equipment"]["add button"]):
            # Validation
            if not name or name.strip() == "":
                st.error(t["Validation"]["name_empty"])
            elif power <= 0:
                st.error(t["Validation"]["power_invalid"])
            elif time <= 0:
                st.error(t["Validation"]["time_invalid"])
            else:
                try:
                    st.session_state["equipments"].add_equipment(name.strip(), int(power), time, start_hour)
                    st.success(t["New Equipment"]["success message"].format(name=name, power=power, time=time))
                except ValueError as e:
                    st.error(str(e))
    
    # Edit Equipment
    if not st.session_state["equipments"].is_empty():
        with st.expander(t["Edit Equipment"]["title"]):
            equipment_to_edit = st.selectbox(
                t["Edit Equipment"]["select"],
                st.session_state["equipments"].get_equipments(),
                key="edit_select"
            )
            if equipment_to_edit:
                edit_name = st.text_input(t["New Equipment"]["name"], value=equipment_to_edit.name, key="edit_name")
                edit_power = st.number_input(t["New Equipment"]["power"], value=equipment_to_edit.power, min_value=1, step=1, key="edit_power")
                edit_time = st.number_input(t["New Equipment"]["time"], value=float(equipment_to_edit.time), min_value=0.1, step=0.1, key="edit_time")
                edit_start_hour = st.slider(t["Hourly"]["start_hour"], min_value=0, max_value=23, value=equipment_to_edit.start_hour, key="edit_start_hour")
                
                if st.button(t["Edit Equipment"]["edit button"]):
                    if not edit_name or edit_name.strip() == "":
                        st.error(t["Validation"]["name_empty"])
                    elif edit_power <= 0:
                        st.error(t["Validation"]["power_invalid"])
                    elif edit_time <= 0:
                        st.error(t["Validation"]["time_invalid"])
                    else:
                        try:
                            st.session_state["equipments"].edit_equipment(
                                equipment_to_edit,
                                edit_name.strip(),
                                int(edit_power),
                                edit_time,
                                edit_start_hour
                            )
                            st.success(t["Edit Equipment"]["success message"].format(name=edit_name))
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))

    # Equipment Library
    st.divider()
    with st.expander(t["Library"]["title"], expanded=False):
        st.caption(t["Library"]["subtitle"])
        library = load_equipment_library()
        categories = get_library_categories(library, lang)
        
        if categories:
            # Category selection with emoji display
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
                    # Equipment selection
                    equipment_options = {i: item["name"] for i, item in enumerate(items)}
                    
                    selected_idx = st.selectbox(
                        t["Library"]["select_equipment"],
                        options=list(equipment_options.keys()),
                        format_func=lambda x: equipment_options[x],
                        key="library_equipment"
                    )
                    
                    if selected_idx is not None:
                        selected_item = items[selected_idx]
                        
                        # Display equipment info
                        st.info(
                            f"**{t['Library']['specifications']}:**\n\n"
                            f"- {t['New Equipment']['power']}: {selected_item['power']} W\n"
                            f"- {t['New Equipment']['time']}: {selected_item['time']} h\n"
                            f"- {t['Hourly']['start_hour']}: {selected_item['start_hour']}h\n\n"
                            f"*{selected_item.get(f'description_{lang}', '')}*"
                        )
                        
                        # Add button
                        if st.button(t["Library"]["add_from_library"], width="stretch"):
                            try:
                                st.session_state["equipments"].add_equipment(
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
                    st.warning("Aucun équipement dans cette catégorie" if lang == "fr" else "No equipment in this category")
        else:
            st.warning("Bibliothèque vide" if lang == "fr" else "Empty library")

    col1, col2 = st.columns(2)
    with col1:
        if st.button(t["Actions"]["sample"]):
            sample()
    with col2:
        if st.button(t["Actions"]["delete_all"]):
            st.session_state["equipments"].delete_all_equipments()
            st.rerun()

    # Delete Equipment
    if not st.session_state["equipments"].is_empty():
        with st.expander(t["Delete Equipment"]["title"]):
            equipment = st.selectbox(
                t["Delete Equipment"]["select"],
                st.session_state["equipments"].get_equipments(),
                key="delete_select"
            )
            if st.button(t["Delete Equipment"]["delete button"]):
                st.session_state["equipments"].delete_equipment(equipment)
                st.rerun()
    
    # Save/Load Configuration
    st.divider()
    with st.expander(t["Storage"]["title"]):
        # Save section
        st.subheader(t["Storage"]["save_button"])
        save_name = st.text_input(t["Storage"]["save_label"], key="save_name")
        col_save, col_export = st.columns(2)
        
        with col_save:
            if st.button(t["Storage"]["save_button"], width="stretch"):
                if save_name and save_name.strip():
                    save_configuration(save_name.strip(), st.session_state["equipments"])
                    st.success(t["Storage"]["save_success"].format(name=save_name))
                else:
                    st.error(t["Storage"]["name_required"])
        
        with col_export:
            if not st.session_state["equipments"].is_empty():
                csv = st.session_state["equipments"].df_datas().to_csv(index=False)
                st.download_button(
                    label=t["Storage"]["export_button"],
                    data=csv,
                    file_name=f"solar_equipment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    width="stretch"
                )
        
        # Load section
        st.divider()
        saved_configs = get_saved_configurations()
        if saved_configs:
            st.subheader(t["Storage"]["load_button"])
            selected_config = st.selectbox(
                t["Storage"]["load_label"],
                saved_configs,
                key="load_select"
            )
            
            col_load, col_del = st.columns(2)
            with col_load:
                if st.button(t["Storage"]["load_button"], width="stretch"):
                    equipments = load_configuration(selected_config)
                    st.session_state["equipments"].delete_all_equipments()
                    for eq in equipments:
                        st.session_state["equipments"].add_equipment(
                            eq["name"], 
                            eq["power"], 
                            eq["time"],
                            eq.get("start_hour", 0)  # Default to 0 for old configs
                        )
                    st.success(t["Storage"]["load_success"].format(name=selected_config))
                    st.rerun()
            
            with col_del:
                if st.button(t["Storage"]["delete_button"], width="stretch"):
                    delete_configuration(selected_config)
                    st.success(t["Storage"]["delete_success"].format(name=selected_config))
                    st.rerun()
        else:
            st.info(t["Storage"]["no_configs"])

# Displaying on the main page
st.title(t["Main"]["title"])
if not st.session_state["equipments"].is_empty():
    # Equipment table
    st.dataframe(st.session_state["equipments"].df_datas(), hide_index=True)

    # Showing the full daily energie consumption
    daily_energy = st.session_state['equipments'].total_energy_consumption()
    all_power = st.session_state['equipments'].total_power()
    
    # Metrics in columns
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label=":material/bolt: " + t["Main"]["daily_consumption"],
            value=f"{daily_energy:.0f} Wh",
            delta=f"{daily_energy/1000:.2f} kWh"
        )
    with col2:
        st.metric(
            label=":material/power: " + t["Main"]["converter_power"],
            value=f"{all_power:.0f} W",
            delta=f"{all_power/1000:.2f} kW"
        )
    
    # Charts section
    st.divider()
    st.subheader(":material/bar_chart: " + t["Charts"]["consumption_title"])
    
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        # Pie chart
        pie_chart = create_consumption_pie_chart(st.session_state["equipments"], t)
        st.plotly_chart(pie_chart, width="stretch")
    
    with chart_col2:
        # Bar chart
        bar_chart = create_power_time_chart(st.session_state["equipments"], t)
        st.plotly_chart(bar_chart, width="stretch")
    
    # Hourly Profile Section
    st.divider()
    st.subheader(":material/schedule: " + t["Hourly"]["title"])
    
    hourly_chart = create_hourly_profile_chart(st.session_state["equipments"], t)
    st.plotly_chart(hourly_chart, width="stretch")
    
    # Hourly stats
    hourly_profile = st.session_state["equipments"].get_hourly_profile()
    peak_consumption = max(hourly_profile)
    peak_hour = hourly_profile.index(peak_consumption)
    avg_consumption = sum(hourly_profile) / 24
    
    hourly_col1, hourly_col2, hourly_col3 = st.columns(3)
    with hourly_col1:
        st.metric(
            t["Hourly"]["peak_consumption"],
            f"{peak_consumption:.0f} W",
            delta=f"@ {peak_hour}h"
        )
    with hourly_col2:
        st.metric(
            t["Hourly"]["average_consumption"],
            f"{avg_consumption:.0f} W"
        )
    with hourly_col3:
        # Count non-zero hours
        active_hours = sum(1 for p in hourly_profile if p > 0)
        st.metric(
            "Heures actives" if lang == "fr" else "Active hours",
            f"{active_hours} h"
        )
    
    st.divider()

    # Battery capacity -- add to the session
    st.subheader(":material/battery_charging_full: Battery Configuration")
    battery_type = st.radio("Chose type of your batteries", ["Plomb", "Lithium"])

    side1, side2 = st.columns(2)

    discharge_factor = 0.5
    voltage = 12
    with side1:
        autonomy = st.number_input("Needed autonomy (h)", value=24.0, step=1.0, min_value=1.0)
        match battery_type:
            case "Plomb":
                voltage = st.selectbox("Select battery voltage", [12, 24, 48])
                discharge_factor = st.number_input("Discharge Factor", value=0.5, step=0.1, min_value=0.0, max_value=1.0)

            case "Lithium":
                voltage = st.selectbox("Select battery voltage", [12, 24, 48], index=1)
                discharge_factor = st.number_input("Discharge Factor", value=0.8, step=0.1, min_value=0.0, max_value=1.0)

    with side2:
        st.session_state["autonomy"] = round(autonomy / 24, 2)
        st.session_state["discharge_factor"] = discharge_factor

        # Choix de la batterie
        chosen_battery = st.selectbox("Chose your Batterie (Ah)", [100, 150, 200, 250, 280, 300])

        batteries_capacity = capacity(
            energy=daily_energy,
            autonomy=st.session_state["autonomy"],
            discharge_factor=st.session_state["discharge_factor"],
            batterie_voltage=voltage
        )

        st.metric("Batterie capacity needed", f"{batteries_capacity:.0f} Ah")

        # Number of batteries needed
        mod_bat = batteries_capacity % chosen_battery
        number_batteries = int(batteries_capacity / chosen_battery)
        if mod_bat > 0:
            number_batteries += 1

        if number_batteries % 2 != 0 and number_batteries != 1:
            number_batteries += 1

        autonomy_calc = autonomy_calculator(
            energy=daily_energy,
            bat_capacity=chosen_battery*number_batteries,
            discharge_factor=st.session_state["discharge_factor"],
            batterie_voltage=voltage
        )
        st.metric("Minimum Batteries", f"Qtt: {number_batteries}", delta=f"Autonomy: {int(autonomy_calc*24)}h")

    # Production
    st.divider()
    st.subheader(":material/wb_sunny: Solar Panels Configuration")
    
    pv_col1, pv_col2 = st.columns(2)
    
    with pv_col1:
        average_sunshine = st.number_input("Average sunshine (h/day)", value=7.5, step=0.1, min_value=0.1, max_value=24.0)
        security_factor = st.number_input("Security Factor", value=1.2, step=0.1, min_value=1.0, max_value=2.0)
    
    with pv_col2:
        needed_pv_power = daily_energy * security_factor / average_sunshine
        st.metric(":material/solar_power: PV Power needed", f"{needed_pv_power:.0f} W", delta=f"{needed_pv_power/1000:.2f} kW")
        
        pv_power = st.number_input("Your PV panel power (W)", value=300, min_value=1, step=1)

    mod_pv = needed_pv_power % pv_power
    number_pv = int(needed_pv_power / pv_power)
    if mod_pv > 0:
        number_pv += 1

    if number_pv % 2 != 0 and number_pv != 1:
        number_pv += 1

    st.metric(":material/inventory_2: Minimum PV Panels", f"Quantity: {number_pv}", delta=f"Total: {number_pv*pv_power*0.75:.0f} W (75% efficiency)")
    
    # Regulator and Wiring Section
    st.divider()
    st.subheader(":material/settings_input_component: " + t["Regulator"]["title"])
    
    with st.expander(t["Regulator"]["subtitle"], expanded=True):
        reg_col1, reg_col2 = st.columns(2)
        
        with reg_col1:
            regulator_type = st.radio(
                t["Regulator"]["type"],
                ["MPPT", "PWM"],
                help="MPPT est plus efficace (98%) mais plus cher. PWM est moins cher (85% efficacité)."
            )
            
            pv_voltage = st.number_input(
                t["Regulator"]["pv_voltage"],
                value=36,
                min_value=12,
                max_value=200,
                step=12,
                help="Tension nominale des panneaux PV (souvent 36V pour du 12V système)"
            )
        
        with reg_col2:
            # Calculate regulator specs
            total_pv_power = number_pv * pv_power
            regulator_specs = calculate_regulator(
                pv_power=total_pv_power,
                battery_voltage=voltage,
                regulator_type=regulator_type
            )
            
            st.metric(
                t["Regulator"]["current"],
                f"{regulator_specs['nominal_current']:.1f} A"
            )
            
            st.metric(
                t["Regulator"]["recommended"],
                f"{regulator_specs['recommended_current']:.0f} A",
                delta=t["Regulator"]["safety_margin"],
                help="Courant recommandé avec marge de sécurité de 25%"
            )
            
            st.metric(
                t["Regulator"]["power"],
                f"{regulator_specs['nominal_power']:.0f} W",
                delta=f"Rendement: {regulator_specs['efficiency']*100:.0f}%"
            )
    
    # Wiring Section
    st.divider()
    st.subheader(":material/cable: " + t["Wiring"]["title"])
    
    with st.expander(t["Wiring"]["subtitle"], expanded=True):
        # Configuration
        wire_config_col1, wire_config_col2 = st.columns(2)
        
        with wire_config_col1:
            pv_to_reg_length = st.number_input(
                t["Wiring"]["cable_length"] + " (PV → Régulateur)",
                value=10.0,
                min_value=1.0,
                max_value=100.0,
                step=1.0
            )
            
            reg_to_bat_length = st.number_input(
                t["Wiring"]["cable_length"] + " (Régulateur → Batteries)",
                value=3.0,
                min_value=0.5,
                max_value=50.0,
                step=0.5
            )
        
        with wire_config_col2:
            bat_to_conv_length = st.number_input(
                t["Wiring"]["cable_length"] + " (Batteries → Convertisseur)",
                value=2.0,
                min_value=0.5,
                max_value=50.0,
                step=0.5
            )
            
            max_voltage_drop = st.slider(
                t["Wiring"]["voltage_drop"],
                min_value=1.0,
                max_value=5.0,
                value=3.0,
                step=0.5,
                help="3% est la norme recommandée"
            )
        
        st.divider()
        
        # Calculate cables for each section
        # 1. PV to Regulator
        pv_current = regulator_specs['nominal_current']
        pv_to_reg_cable = calculate_cable_section(
            current=pv_current,
            length=pv_to_reg_length,
            voltage=voltage,
            max_drop_percent=max_voltage_drop
        )
        
        # 2. Regulator to Battery
        reg_to_bat_cable = calculate_cable_section(
            current=pv_current,
            length=reg_to_bat_length,
            voltage=voltage,
            max_drop_percent=max_voltage_drop
        )
        
        # 3. Battery to Converter (higher current due to AC conversion)
        converter_current = all_power / voltage  # DC current for AC load
        bat_to_conv_cable = calculate_cable_section(
            current=converter_current,
            length=bat_to_conv_length,
            voltage=voltage,
            max_drop_percent=max_voltage_drop
        )
        
        # Display results
        st.subheader("Résultats" if lang == "fr" else "Results")
        
        cable_col1, cable_col2, cable_col3 = st.columns(3)
        
        with cable_col1:
            st.markdown(f"**{t['Wiring']['pv_to_reg']}**")
            st.metric(
                t["Wiring"]["cable_section"],
                f"{pv_to_reg_cable['cable_section']:.1f} mm²"
            )
            st.metric(
                t["Wiring"]["fuse_rating"],
                f"{pv_to_reg_cable['fuse_rating']} A"
            )
            st.caption(f"Chute: {pv_to_reg_cable['actual_drop_percent']:.2f}%" if lang == "fr" else f"Drop: {pv_to_reg_cable['actual_drop_percent']:.2f}%")
        
        with cable_col2:
            st.markdown(f"**{t['Wiring']['reg_to_bat']}**")
            st.metric(
                t["Wiring"]["cable_section"],
                f"{reg_to_bat_cable['cable_section']:.1f} mm²"
            )
            st.metric(
                t["Wiring"]["fuse_rating"],
                f"{reg_to_bat_cable['fuse_rating']} A"
            )
            st.caption(f"Chute: {reg_to_bat_cable['actual_drop_percent']:.2f}%" if lang == "fr" else f"Drop: {reg_to_bat_cable['actual_drop_percent']:.2f}%")
        
        with cable_col3:
            st.markdown(f"**{t['Wiring']['bat_to_conv']}**")
            st.metric(
                t["Wiring"]["cable_section"],
                f"{bat_to_conv_cable['cable_section']:.1f} mm²"
            )
            st.metric(
                t["Wiring"]["fuse_rating"],
                f"{bat_to_conv_cable['fuse_rating']} A"
            )
            st.caption(f"Chute: {bat_to_conv_cable['actual_drop_percent']:.2f}%" if lang == "fr" else f"Drop: {bat_to_conv_cable['actual_drop_percent']:.2f}%")
        
        # Protection summary
        st.divider()
        st.info(
            f"⚠️ **Protections recommandées:**\n\n"
            f"- Fusibles DC: {pv_to_reg_cable['fuse_rating']}A (PV), {reg_to_bat_cable['fuse_rating']}A (Batterie)\n"
            f"- Disjoncteur batterie: {bat_to_conv_cable['fuse_rating']}A\n"
            f"- Câbles cuivre multiconducteurs recommandés\n"
            f"- Installation selon normes NF C 15-100 (France) ou équivalent"
        )
    
    # Economic Analysis Section
    st.divider()
    st.subheader(":material/payments: " + t["Economics"]["title"])
    
    with st.expander(t["Economics"]["costs_title"], expanded=True):
        cost_col1, cost_col2, cost_col3 = st.columns(3)
        
        with cost_col1:
            battery_unit_cost = st.number_input(
                t["Economics"]["battery_cost"],
                value=200.0,
                min_value=0.0,
                step=10.0
            )
            pv_unit_cost = st.number_input(
                t["Economics"]["pv_cost"],
                value=150.0,
                min_value=0.0,
                step=10.0
            )
        
        with cost_col2:
            converter_cost = st.number_input(
                t["Economics"]["converter_cost"],
                value=500.0,
                min_value=0.0,
                step=50.0
            )
            regulator_cost = st.number_input(
                t["Economics"]["regulator_cost"],
                value=300.0,
                min_value=0.0,
                step=50.0
            )
        
        with cost_col3:
            installation_cost = st.number_input(
                t["Economics"]["installation_cost"],
                value=1000.0,
                min_value=0.0,
                step=100.0
            )
        
        # Calculate costs
        costs = calculate_system_cost(
            num_batteries=number_batteries,
            battery_unit_cost=battery_unit_cost,
            num_pv=number_pv,
            pv_unit_cost=pv_unit_cost,
            converter_cost=converter_cost,
            regulator_cost=regulator_cost,
            installation_cost=installation_cost
        )
        
        st.divider()
        
        # Display cost breakdown
        cost_display_col1, cost_display_col2, cost_display_col3 = st.columns(3)
        
        with cost_display_col1:
            st.metric(
                t["Economics"]["total_batteries"],
                f"{costs['battery_total']:.2f} €",
                delta=f"{number_batteries} × {battery_unit_cost:.0f}€"
            )
            st.metric(
                t["Economics"]["total_pv"],
                f"{costs['pv_total']:.2f} €",
                delta=f"{number_pv} × {pv_unit_cost:.0f}€"
            )
        
        with cost_display_col2:
            st.metric("Convertisseur" if lang == "fr" else "Converter", f"{costs['converter']:.2f} €")
            st.metric("Régulateur" if lang == "fr" else "Regulator", f"{costs['regulator']:.2f} €")
        
        with cost_display_col3:
            st.metric("Installation", f"{costs['installation']:.2f} €")
            st.metric(
                ":material/account_balance: " + t["Economics"]["total_system"],
                f"{costs['total']:.2f} €",
                delta=f"{costs['total']/1000:.1f}k €"
            )
    
    # ROI and Savings
    with st.expander(t["Economics"]["savings_title"], expanded=True):
        roi_col1, roi_col2 = st.columns([1, 2])
        
        with roi_col1:
            electricity_price = st.number_input(
                t["Economics"]["electricity_price"],
                value=0.20,
                min_value=0.0,
                step=0.01,
                format="%.3f"
            )
        
        with roi_col2:
            daily_energy_kwh = daily_energy / 1000
            annual_energy_kwh = daily_energy_kwh * 365
            
            savings = calculate_roi(
                total_cost=costs['total'],
                daily_energy_kwh=daily_energy_kwh,
                electricity_price_per_kwh=electricity_price
            )
            
            savings_display_col1, savings_display_col2, savings_display_col3 = st.columns(3)
            
            with savings_display_col1:
                st.metric(
                    t["Economics"]["daily_savings"],
                    f"{savings['daily']:.2f} €"
                )
            
            with savings_display_col2:
                st.metric(
                    t["Economics"]["monthly_savings"],
                    f"{savings['monthly']:.2f} €"
                )
            
            with savings_display_col3:
                st.metric(
                    t["Economics"]["annual_savings"],
                    f"{savings['annual']:.2f} €"
                )
        
        st.divider()
        
        # ROI Display
        roi_display_col1, roi_display_col2 = st.columns(2)
        
        with roi_display_col1:
            if savings['roi_years'] != float('inf'):
                st.metric(
                    ":material/trending_up: " + t["Economics"]["roi_years"],
                    f"{savings['roi_years']:.1f} ans" if lang == "fr" else f"{savings['roi_years']:.1f} years",
                    delta=f"{int(savings['roi_years'] * 12)} mois" if lang == "fr" else f"{int(savings['roi_years'] * 12)} months"
                )
            else:
                st.warning("Impossible de calculer le ROI" if lang == "fr" else "Cannot calculate ROI")
        
        with roi_display_col2:
            # CO2 Impact
            co2_impact = calculate_co2_impact(annual_energy_kwh)
            st.metric(
                ":material/eco: " + t["Economics"]["co2_avoided"],
                f"{co2_impact['co2_tons']:.2f} tonnes",
                delta=f"{co2_impact['co2_kg']:.0f} kg"
            )
    
    # Environmental Impact
    with st.expander(t["Economics"]["co2_title"]):
        co2_col1, co2_col2 = st.columns(2)
        
        with co2_col1:
            st.metric(
                ":material/forest: " + t["Economics"]["trees_equivalent"],
                f"{co2_impact['trees']:.0f} arbres" if lang == "fr" else f"{co2_impact['trees']:.0f} trees"
            )
        
        with co2_col2:
            # Lifetime impact (25 years typical for solar)
            lifetime_co2 = co2_impact['co2_tons'] * 25
            st.metric(
                "Impact 25 ans" if lang == "fr" else "25-year Impact",
                f"{lifetime_co2:.1f} tonnes CO₂"
            )

else:
    st.info(t["Main"]["empty_state"])
