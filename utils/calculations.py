"""
Calculation utilities for Solar Solution.

This module contains all calculation functions for:
- Battery and solar panel sizing
- Economic analysis (costs, ROI, CO2)
- Regulator and wiring specifications
"""

from typing import Dict, Union


def battery_needed(
    daily_energy_wh: float, 
    battery_voltage: int, 
    battery_capacity_ah: int, 
    autonomy_days: int, 
    discharge_depth: float
) -> int:
    """
    Calculate the number of batteries needed for the system.
    
    Formula: n = (E × A) / (V × C × DoD)
    
    Args:
        daily_energy_wh: Daily energy consumption in Watt-hours
        battery_voltage: Battery voltage in Volts
        battery_capacity_ah: Battery capacity in Amp-hours
        autonomy_days: Number of days of autonomy required
        discharge_depth: Depth of discharge (0-1), typically 0.5 for lead-acid
        
    Returns:
        int: Number of batteries needed (rounded up)
    """
    import math
    energy_needed = daily_energy_wh * autonomy_days
    battery_energy = battery_voltage * battery_capacity_ah * discharge_depth
    return math.ceil(energy_needed / battery_energy)


def panel_needed(
    daily_energy_wh: float,
    pv_power_w: int,
    sun_hours: float
) -> int:
    """
    Calculate the number of solar panels needed.
    
    Formula: n = E / (P × H)
    
    Args:
        daily_energy_wh: Daily energy consumption in Watt-hours
        pv_power_w: Power of one solar panel in Watts
        sun_hours: Peak sun hours per day
        
    Returns:
        int: Number of panels needed (rounded up)
    """
    import math
    return math.ceil(daily_energy_wh / (pv_power_w * sun_hours))


def calculate_system_cost(
    num_batteries: int,
    battery_unit_cost: float,
    num_pv: int,
    pv_unit_cost: float,
    converter_cost: float,
    regulator_cost: float,
    installation_cost: float
) -> Dict[str, float]:
    """
    Calculate total system costs breakdown.
    
    Args:
        num_batteries: Number of batteries
        battery_unit_cost: Cost per battery in currency
        num_pv: Number of solar panels
        pv_unit_cost: Cost per solar panel in currency
        converter_cost: Cost of the inverter/converter
        regulator_cost: Cost of the charge controller
        installation_cost: Installation and labor costs
        
    Returns:
        dict: Breakdown of costs with keys:
            - battery_total: Total battery cost
            - pv_total: Total solar panel cost
            - converter: Converter cost
            - regulator: Regulator cost
            - installation: Installation cost
            - total: Total system cost
    """
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
) -> Dict[str, float]:
    """
    Calculate return on investment and savings.
    
    Args:
        total_cost: Total system cost in currency
        daily_energy_kwh: Daily energy consumption in kWh
        electricity_price_per_kwh: Price of electricity per kWh
        
    Returns:
        dict: Savings and ROI with keys:
            - daily: Daily savings
            - monthly: Monthly savings (30 days)
            - annual: Annual savings (365 days)
            - roi_years: Years to break even
    """
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


def calculate_co2_impact(annual_energy_kwh: float) -> Dict[str, float]:
    """
    Calculate CO2 emissions avoided by using solar energy.
    
    Uses average values:
    - 0.5 kg CO2 per kWh (varies by country and energy mix)
    - 1 tree absorbs ~21 kg CO2 per year
    
    Args:
        annual_energy_kwh: Annual energy consumption in kWh
        
    Returns:
        dict: CO2 impact with keys:
            - co2_kg: CO2 avoided in kilograms
            - co2_tons: CO2 avoided in metric tons
            - trees: Equivalent number of trees planted
    """
    co2_avoided_kg = annual_energy_kwh * 0.5
    trees_equivalent = co2_avoided_kg / 21
    
    return {
        "co2_kg": co2_avoided_kg,
        "co2_tons": co2_avoided_kg / 1000,
        "trees": trees_equivalent
    }


def calculate_regulator(
    pv_power: float, 
    battery_voltage: int, 
    regulator_type: str = "MPPT"
) -> Dict[str, Union[float, str]]:
    """
    Calculate charge controller (regulator) specifications.
    
    MPPT (Maximum Power Point Tracking): More efficient, can handle
    higher PV voltage, typically 96-98% efficient.
    
    PWM (Pulse Width Modulation): Less efficient, requires PV voltage
    close to battery voltage, typically 80-85% efficient.
    
    Args:
        pv_power: Total PV power in Watts
        battery_voltage: Battery bank voltage (12, 24, or 48V)
        regulator_type: Type of regulator - "MPPT" or "PWM"
        
    Returns:
        dict: Regulator specifications with keys:
            - nominal_current: Nominal current in Amperes
            - recommended_current: Recommended current with 25% safety margin
            - nominal_power: Nominal power in Watts
            - efficiency: Regulator efficiency (0-1)
            - type: Regulator type
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


def calculate_cable_section(
    current: float, 
    length: float, 
    voltage: int, 
    max_drop_percent: float = 3.0
) -> Dict[str, float]:
    """
    Calculate cable section based on voltage drop requirements.
    
    Uses the formula: S = (2 × ρ × I × L) / ΔV
    where:
    - S = cable cross-section (mm²)
    - ρ = resistivity of copper at 20°C (0.01724 Ω·mm²/m)
    - I = current (A)
    - L = cable length one-way (m)
    - ΔV = maximum acceptable voltage drop (V)
    
    Factor 2 accounts for current going out and returning (total cable length).
    
    Args:
        current: Current in Amperes
        length: Cable length in meters (one-way distance)
        voltage: System voltage in Volts
        max_drop_percent: Maximum acceptable voltage drop percentage (default 3%)
        
    Returns:
        dict: Cable specifications with keys:
            - cable_section: Selected cable section in mm²
            - actual_drop_volts: Actual voltage drop in Volts
            - actual_drop_percent: Actual voltage drop percentage
            - fuse_rating: Recommended fuse rating in Amperes
            - current: Operating current in Amperes
    """
    # Resistivity of copper at 20°C (Ω·mm²/m)
    rho_copper = 0.01724
    
    # Maximum acceptable voltage drop
    max_drop_volts = voltage * (max_drop_percent / 100)
    
    # Calculate minimum cable section: S = (2 * ρ * I * L) / ΔV
    # Factor 2 because current goes out and returns
    min_section = (2 * rho_copper * current * length) / max_drop_volts
    
    # Standard cable sections (mm²) according to IEC standards
    standard_sections = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240]
    
    # Find the next standard section
    cable_section = next((s for s in standard_sections if s >= min_section), 240)
    
    # Calculate actual voltage drop with selected section
    actual_drop_volts = (2 * rho_copper * current * length) / cable_section
    actual_drop_percent = (actual_drop_volts / voltage) * 100
    
    # Fuse rating: 1.25 × nominal current, rounded to nearest 5A
    fuse_rating = round(current * 1.25 / 5) * 5
    if fuse_rating < 5:
        fuse_rating = 5
    
    return {
        "cable_section": cable_section,
        "actual_drop_volts": actual_drop_volts,
        "actual_drop_percent": actual_drop_percent,
        "fuse_rating": fuse_rating,
        "current": current
    }
