"""
Unit tests for Equipment and EquipmentFactory models.

Tests cover:
- Equipment creation and properties
- Energy consumption calculations
- Hourly consumption distribution
- EquipmentFactory operations (add, edit, delete)
- Data validation
"""

import pytest
from models import Equipment, EquipmentFactory


class TestEquipment:
    """Test cases for the Equipment class"""
    
    def test_equipment_creation(self):
        """Test basic equipment creation"""
        eq = Equipment("Laptop", 65, 4.0, start_hour=9)
        assert eq.name == "Laptop"
        assert eq.power == 65
        assert eq.time == 4.0
        assert eq.start_hour == 9
        assert eq.end_hour == 13  # 9 + 4
    
    def test_equipment_with_explicit_end_hour(self):
        """Test equipment creation with explicit end_hour"""
        eq = Equipment("TV", 150, 3.0, start_hour=18, end_hour=22)
        assert eq.start_hour == 18
        assert eq.end_hour == 22
    
    def test_daily_energy_consumption(self):
        """Test daily energy consumption calculation"""
        eq = Equipment("Fridge", 150, 24.0)
        assert eq.daily_energy_consumption() == 3600.0  # 150W × 24h
    
    def test_hourly_consumption_distribution(self):
        """Test hourly consumption distribution over 24 hours"""
        eq = Equipment("Heater", 2000, 3.0, start_hour=6)
        hourly = eq.get_hourly_consumption()
        
        # Should have 24 hours
        assert len(hourly) == 24
        
        # Power should be distributed from hour 6 to 9 (3 hours)
        assert hourly[6] == 2000
        assert hourly[7] == 2000
        assert hourly[8] == 2000
        
        # Other hours should be zero
        assert hourly[5] == 0
        assert hourly[9] == 0
    
    def test_hourly_consumption_with_fractional_hour(self):
        """Test hourly consumption with partial hours"""
        eq = Equipment("Microwave", 1000, 0.5, start_hour=12)
        hourly = eq.get_hourly_consumption()
        
        # Should have power for 0.5 hours at hour 12
        assert hourly[12] == 500.0  # 1000W × 0.5h
        assert hourly[13] == 0
    
    def test_hourly_consumption_wrapping_midnight(self):
        """Test hourly consumption that wraps around midnight"""
        eq = Equipment("Night light", 10, 2.0, start_hour=23)
        hourly = eq.get_hourly_consumption()
        
        # Should have power at hour 23 and 0 (wraps around)
        assert hourly[23] == 10
        assert hourly[0] == 10
        assert hourly[1] == 0
    
    def test_equipment_equality(self):
        """Test equipment equality based on name"""
        eq1 = Equipment("Laptop", 65, 4.0)
        eq2 = Equipment("Laptop", 100, 8.0)  # Different specs, same name
        eq3 = Equipment("Desktop", 65, 4.0)  # Different name
        
        assert eq1 == eq2  # Same name
        assert eq1 != eq3  # Different name
    
    def test_equipment_string_representation(self):
        """Test string representation of equipment"""
        eq = Equipment("Laptop", 65, 4.0, start_hour=9)
        assert str(eq) == "Laptop (65 W, 4.0 h, 9h-13h)"
    
    def test_equipment_repr(self):
        """Test repr of equipment"""
        eq = Equipment("Laptop", 65, 4.0, start_hour=9)
        assert repr(eq) == "Equipment(name='Laptop', power=65, time=4.0, start_hour=9)"


class TestEquipmentFactory:
    """Test cases for the EquipmentFactory class"""
    
    def test_factory_creation(self):
        """Test factory initialization"""
        factory = EquipmentFactory()
        assert factory.is_empty()
        assert len(factory.get_equipments()) == 0
    
    def test_add_equipment(self):
        """Test adding equipment to factory"""
        factory = EquipmentFactory()
        factory.add_equipment("Laptop", 65, 4.0)
        
        assert not factory.is_empty()
        assert len(factory.get_equipments()) == 1
        
        eq = factory.get_equipments()[0]
        assert eq.name == "Laptop"
        assert eq.power == 65
    
    def test_add_duplicate_equipment_raises_error(self):
        """Test that adding duplicate equipment raises ValueError"""
        factory = EquipmentFactory()
        factory.add_equipment("Laptop", 65, 4.0)
        
        with pytest.raises(ValueError):
            factory.add_equipment("Laptop", 100, 8.0)
    
    def test_total_energy_consumption(self):
        """Test total energy consumption calculation"""
        factory = EquipmentFactory()
        factory.add_equipment("Laptop", 65, 4.0)  # 260 Wh
        factory.add_equipment("TV", 150, 8.0)     # 1200 Wh
        
        total = factory.total_energy_consumption()
        assert total == 1460.0  # 260 + 1200
    
    def test_total_power(self):
        """Test total power calculation"""
        factory = EquipmentFactory()
        factory.add_equipment("Laptop", 65, 4.0)
        factory.add_equipment("TV", 150, 8.0)
        
        total = factory.total_power()
        assert total == 215.0  # 65 + 150
    
    def test_get_hourly_profile(self):
        """Test aggregated hourly consumption profile"""
        factory = EquipmentFactory()
        factory.add_equipment("Heater", 1000, 2.0, start_hour=6)  # 6-8
        factory.add_equipment("Light", 100, 5.0, start_hour=18)   # 18-23
        
        profile = factory.get_hourly_profile()
        
        assert len(profile) == 24
        assert profile[6] == 1000   # Only heater
        assert profile[7] == 1000   # Only heater
        assert profile[18] == 100   # Only light
        assert profile[22] == 100   # Only light
        assert profile[12] == 0     # Nothing
    
    def test_delete_equipment(self):
        """Test deleting equipment"""
        factory = EquipmentFactory()
        factory.add_equipment("Laptop", 65, 4.0)
        factory.add_equipment("TV", 150, 8.0)
        
        eq = factory.get_equipments()[0]
        factory.delete_equipment(eq)
        
        assert len(factory.get_equipments()) == 1
        assert factory.get_equipments()[0].name == "TV"
    
    def test_delete_all_equipments(self):
        """Test deleting all equipment"""
        factory = EquipmentFactory()
        factory.add_equipment("Laptop", 65, 4.0)
        factory.add_equipment("TV", 150, 8.0)
        
        factory.delete_all_equipments()
        
        assert factory.is_empty()
        assert len(factory.get_equipments()) == 0
    
    def test_edit_equipment(self):
        """Test editing existing equipment"""
        factory = EquipmentFactory()
        factory.add_equipment("Laptop", 65, 4.0, start_hour=9)
        
        old_eq = factory.get_equipments()[0]
        factory.edit_equipment(old_eq, "Gaming Laptop", 150, 6.0, 14)
        
        eq = factory.get_equipments()[0]
        assert eq.name == "Gaming Laptop"
        assert eq.power == 150
        assert eq.time == 6.0
        assert eq.start_hour == 14
    
    def test_edit_nonexistent_equipment_raises_error(self):
        """Test editing non-existent equipment raises ValueError"""
        factory = EquipmentFactory()
        factory.add_equipment("Laptop", 65, 4.0)
        
        fake_eq = Equipment("Fake", 100, 2.0)
        
        with pytest.raises(ValueError):
            factory.edit_equipment(fake_eq, "New Name", 200, 4.0)
    
    def test_get_equipment_by_name(self):
        """Test getting equipment by name"""
        factory = EquipmentFactory()
        factory.add_equipment("Laptop", 65, 4.0)
        factory.add_equipment("TV", 150, 8.0)
        
        eq = factory.get_equipment_by_name("Laptop")
        assert eq is not None
        assert eq.name == "Laptop"
        assert eq.power == 65
    
    def test_get_equipment_by_name_not_found(self):
        """Test getting non-existent equipment returns None"""
        factory = EquipmentFactory()
        factory.add_equipment("Laptop", 65, 4.0)
        
        eq = factory.get_equipment_by_name("Desktop")
        assert eq is None
    
    def test_df_datas(self):
        """Test DataFrame generation"""
        factory = EquipmentFactory()
        factory.add_equipment("Laptop", 65, 4.0, start_hour=9)
        factory.add_equipment("TV", 150, 8.0, start_hour=18)
        
        df = factory.df_datas()
        
        assert len(df) == 2
        assert list(df.columns) == ["Name", "Power", "Usage Time", "Schedule", "Energie"]
        assert df.iloc[0]["Name"] == "Laptop"
        assert df.iloc[0]["Power"] == 65
        assert df.iloc[0]["Usage Time"] == 4.0
        assert df.iloc[0]["Schedule"] == "9h-13h"
        assert df.iloc[0]["Energie"] == 260.0
