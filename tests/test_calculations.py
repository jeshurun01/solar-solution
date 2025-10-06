"""
Unit tests for calculation utilities.

Tests cover:
- Battery sizing calculations
- Solar panel sizing calculations
- Economic analysis (costs, ROI, CO2)
- Regulator specifications
- Cable section calculations
"""

import pytest
from utils.calculations import (
    battery_needed,
    panel_needed,
    calculate_system_cost,
    calculate_roi,
    calculate_co2_impact,
    calculate_regulator,
    calculate_cable_section
)


class TestBatteryCalculations:
    """Test cases for battery sizing"""
    
    def test_battery_needed_basic(self):
        """Test basic battery calculation"""
        # 1000 Wh/day, 12V, 200Ah, 2 days autonomy, 50% DoD
        num = battery_needed(1000, 12, 200, 2, 0.5)
        # Energy needed = 1000 * 2 = 2000 Wh
        # Battery energy = 12 * 200 * 0.5 = 1200 Wh
        # Batteries needed = ceil(2000 / 1200) = 2
        assert num == 2
    
    def test_battery_needed_exact_match(self):
        """Test when energy requirement matches exactly"""
        num = battery_needed(1200, 12, 200, 1, 0.5)
        # Energy needed = 1200 Wh
        # Battery energy = 1200 Wh
        assert num == 1
    
    def test_battery_needed_high_autonomy(self):
        """Test with high autonomy days"""
        num = battery_needed(500, 24, 100, 5, 0.5)
        # Energy needed = 500 * 5 = 2500 Wh
        # Battery energy = 24 * 100 * 0.5 = 1200 Wh
        # Batteries needed = ceil(2500 / 1200) = 3
        assert num == 3
    
    def test_battery_needed_deep_discharge(self):
        """Test with different discharge depths"""
        # Same setup, different DoD
        num_50 = battery_needed(1000, 12, 200, 2, 0.5)
        num_80 = battery_needed(1000, 12, 200, 2, 0.8)
        
        # Higher DoD means fewer or equal batteries needed
        assert num_80 <= num_50


class TestPanelCalculations:
    """Test cases for solar panel sizing"""
    
    def test_panel_needed_basic(self):
        """Test basic panel calculation"""
        # 1500 Wh/day, 300W panels, 5 sun hours
        num = panel_needed(1500, 300, 5.0)
        # Daily production per panel = 300 * 5 = 1500 Wh
        # Panels needed = ceil(1500 / 1500) = 1
        assert num == 1
    
    def test_panel_needed_multiple_panels(self):
        """Test requiring multiple panels"""
        num = panel_needed(3000, 300, 5.0)
        # Daily production per panel = 1500 Wh
        # Panels needed = ceil(3000 / 1500) = 2
        assert num == 2
    
    def test_panel_needed_low_sun_hours(self):
        """Test with low sun hours (cloudy climate)"""
        num_high = panel_needed(1500, 300, 5.0)
        num_low = panel_needed(1500, 300, 3.0)
        
        # Lower sun hours means more panels needed
        assert num_low > num_high
    
    def test_panel_needed_small_panels(self):
        """Test with smaller panel power"""
        num = panel_needed(1500, 100, 5.0)
        # Daily production per panel = 100 * 5 = 500 Wh
        # Panels needed = ceil(1500 / 500) = 3
        assert num == 3


class TestSystemCostCalculations:
    """Test cases for system cost calculations"""
    
    def test_calculate_system_cost_basic(self):
        """Test basic system cost calculation"""
        costs = calculate_system_cost(
            num_batteries=4,
            battery_unit_cost=200.0,
            num_pv=6,
            pv_unit_cost=150.0,
            converter_cost=300.0,
            regulator_cost=200.0,
            installation_cost=500.0
        )
        
        assert costs["battery_total"] == 800.0  # 4 * 200
        assert costs["pv_total"] == 900.0       # 6 * 150
        assert costs["converter"] == 300.0
        assert costs["regulator"] == 200.0
        assert costs["installation"] == 500.0
        assert costs["total"] == 2700.0         # Sum of all
    
    def test_calculate_system_cost_zero_components(self):
        """Test with zero cost components"""
        costs = calculate_system_cost(0, 0.0, 0, 0.0, 0.0, 0.0, 0.0)
        
        assert costs["total"] == 0.0


class TestROICalculations:
    """Test cases for ROI and savings calculations"""
    
    def test_calculate_roi_basic(self):
        """Test basic ROI calculation"""
        roi = calculate_roi(
            total_cost=5000.0,
            daily_energy_kwh=10.0,
            electricity_price_per_kwh=0.15
        )
        
        # Daily savings = 10 * 0.15 = 1.5
        assert roi["daily"] == 1.5
        # Monthly savings = 1.5 * 30 = 45
        assert roi["monthly"] == 45.0
        # Annual savings = 1.5 * 365 = 547.5
        assert roi["annual"] == 547.5
        # ROI = 5000 / 547.5 ≈ 9.13 years
        assert pytest.approx(roi["roi_years"], 0.01) == 9.13
    
    def test_calculate_roi_high_electricity_price(self):
        """Test ROI with high electricity prices"""
        roi_low = calculate_roi(5000.0, 10.0, 0.10)
        roi_high = calculate_roi(5000.0, 10.0, 0.30)
        
        # Higher electricity price = faster ROI
        assert roi_high["roi_years"] < roi_low["roi_years"]
    
    def test_calculate_roi_zero_savings(self):
        """Test ROI with zero energy consumption"""
        roi = calculate_roi(5000.0, 0.0, 0.15)
        
        assert roi["daily"] == 0.0
        assert roi["annual"] == 0.0
        assert roi["roi_years"] == float('inf')


class TestCO2ImpactCalculations:
    """Test cases for CO2 impact calculations"""
    
    def test_calculate_co2_impact_basic(self):
        """Test basic CO2 impact calculation"""
        impact = calculate_co2_impact(annual_energy_kwh=3650.0)
        
        # CO2 avoided = 3650 * 0.5 = 1825 kg
        assert impact["co2_kg"] == 1825.0
        # CO2 in tons = 1.825 tons
        assert impact["co2_tons"] == 1.825
        # Trees = 1825 / 21 ≈ 86.9
        assert pytest.approx(impact["trees"], 0.1) == 86.9
    
    def test_calculate_co2_impact_small_system(self):
        """Test CO2 impact for small system"""
        impact = calculate_co2_impact(annual_energy_kwh=365.0)
        
        # CO2 avoided = 365 * 0.5 = 182.5 kg
        assert impact["co2_kg"] == 182.5
        # Trees ≈ 8.7
        assert pytest.approx(impact["trees"], 0.1) == 8.7
    
    def test_calculate_co2_impact_zero_energy(self):
        """Test CO2 impact with zero energy"""
        impact = calculate_co2_impact(annual_energy_kwh=0.0)
        
        assert impact["co2_kg"] == 0.0
        assert impact["co2_tons"] == 0.0
        assert impact["trees"] == 0.0


class TestRegulatorCalculations:
    """Test cases for charge controller specifications"""
    
    def test_calculate_regulator_mppt_12v(self):
        """Test MPPT regulator calculation for 12V system"""
        spec = calculate_regulator(pv_power=600.0, battery_voltage=12, regulator_type="MPPT")
        
        # Nominal current = 600 / 12 = 50 A
        assert spec["nominal_current"] == 50.0
        # Recommended = 50 * 1.25 = 62.5 A
        assert spec["recommended_current"] == 62.5
        assert spec["nominal_power"] == 600.0
        assert spec["efficiency"] == 0.98  # MPPT
        assert spec["type"] == "MPPT"
    
    def test_calculate_regulator_pwm_24v(self):
        """Test PWM regulator calculation for 24V system"""
        spec = calculate_regulator(pv_power=1200.0, battery_voltage=24, regulator_type="PWM")
        
        # Nominal current = 1200 / 24 = 50 A
        assert spec["nominal_current"] == 50.0
        # Recommended = 50 * 1.25 = 62.5 A
        assert spec["recommended_current"] == 62.5
        assert spec["efficiency"] == 0.85  # PWM
        assert spec["type"] == "PWM"
    
    def test_calculate_regulator_48v(self):
        """Test regulator for 48V system"""
        spec = calculate_regulator(pv_power=2400.0, battery_voltage=48, regulator_type="MPPT")
        
        # Nominal current = 2400 / 48 = 50 A
        assert spec["nominal_current"] == 50.0
    
    def test_calculate_regulator_efficiency_difference(self):
        """Test that MPPT is more efficient than PWM"""
        mppt = calculate_regulator(600.0, 12, "MPPT")
        pwm = calculate_regulator(600.0, 12, "PWM")
        
        assert mppt["efficiency"] > pwm["efficiency"]


class TestCableSectionCalculations:
    """Test cases for cable sizing calculations"""
    
    def test_calculate_cable_section_basic(self):
        """Test basic cable section calculation"""
        spec = calculate_cable_section(
            current=50.0,
            length=10.0,
            voltage=12,
            max_drop_percent=3.0
        )
        
        # Should select a standard cable section
        assert spec["cable_section"] in [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240]
        # Actual drop should be <= max drop
        assert spec["actual_drop_percent"] <= 3.0
        # Fuse rating should be >= current
        assert spec["fuse_rating"] >= 50.0
        assert spec["current"] == 50.0
    
    def test_calculate_cable_section_long_distance(self):
        """Test cable sizing for long distances"""
        short = calculate_cable_section(50.0, 5.0, 12, 3.0)
        long = calculate_cable_section(50.0, 20.0, 12, 3.0)
        
        # Longer distance requires larger cable
        assert long["cable_section"] > short["cable_section"]
    
    def test_calculate_cable_section_high_voltage(self):
        """Test that higher voltage allows smaller cables"""
        low_v = calculate_cable_section(50.0, 10.0, 12, 3.0)
        high_v = calculate_cable_section(50.0, 10.0, 48, 3.0)
        
        # Higher voltage = smaller cable for same power
        assert high_v["cable_section"] < low_v["cable_section"]
    
    def test_calculate_cable_section_fuse_rating(self):
        """Test fuse rating calculation"""
        spec = calculate_cable_section(40.0, 10.0, 24, 3.0)
        
        # Fuse = 40 * 1.25 = 50 A
        assert spec["fuse_rating"] == 50
    
    def test_calculate_cable_section_minimum_fuse(self):
        """Test minimum fuse rating of 5A"""
        spec = calculate_cable_section(2.0, 5.0, 12, 3.0)
        
        # Even with low current, fuse should be at least 5A
        assert spec["fuse_rating"] >= 5
    
    def test_calculate_cable_section_tight_drop_requirement(self):
        """Test with tight voltage drop requirement"""
        loose = calculate_cable_section(50.0, 10.0, 12, 5.0)
        tight = calculate_cable_section(50.0, 10.0, 12, 1.0)
        
        # Tighter requirement needs larger cable
        assert tight["cable_section"] > loose["cable_section"]
