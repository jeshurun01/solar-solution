"""
Equipment models for Solar Solution.

This module contains the Equipment class and EquipmentFactory for managing
electrical equipment and their power consumption profiles.
"""

from typing import Optional
import pandas as pd


class Equipment:
    """
    Represents an electrical equipment with power consumption characteristics.
    
    Attributes:
        name (str): Name of the equipment
        power (int): Power consumption in Watts
        time (float): Daily usage time in hours
        start_hour (int): Hour when equipment starts (0-23)
        end_hour (int): Hour when equipment ends (0-23)
    """
    
    def __init__(
        self, 
        name: str, 
        power: int, 
        time: float, 
        start_hour: int = 0, 
        end_hour: Optional[int] = None
    ) -> None:
        """
        Initialize an Equipment instance.
        
        Args:
            name: Name of the equipment
            power: Power consumption in Watts
            time: Daily usage time in hours
            start_hour: Hour when equipment starts (0-23), defaults to 0
            end_hour: Hour when equipment ends (0-23), calculated if None
        """
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
        """
        Calculate the daily energy consumption of the equipment.
        
        Returns:
            float: Daily energy consumption in Watt-hours (Wh)
        """
        return self.power * self.time
    
    def get_hourly_consumption(self) -> list[float]:
        """
        Get hourly consumption distribution for 24 hours.
        
        Distributes the equipment's power consumption across the hours
        it is active, handling partial hours correctly.
        
        Returns:
            list[float]: List of 24 values representing power consumption 
                        for each hour of the day (Watts)
        """
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
    """
    Factory class for managing a collection of Equipment objects.
    
    Provides methods to add, edit, delete equipment and perform
    aggregate calculations on the entire collection.
    """
    
    def __init__(self):
        """Initialize an empty EquipmentFactory."""
        self._equipments: list[Equipment] = []

    def add_equipment(
        self, 
        name: str, 
        power: int, 
        time: float, 
        start_hour: int = 0
    ) -> None:
        """
        Add an equipment to the factory.
        
        Args:
            name: Name of the equipment
            power: Power consumption in Watts
            time: Daily usage time in hours
            start_hour: Hour when equipment starts (0-23)
            
        Raises:
            ValueError: If equipment with same name already exists
        """
        new_equipment = Equipment(name, power, time, start_hour)
        if new_equipment in self._equipments:
            # Note: Translation should be passed from outside
            raise ValueError(f"Equipment '{name}' already exists")
        self._equipments.append(new_equipment)

    def get_equipments(self) -> list[Equipment]:
        """
        Get all equipments from the factory.
        
        Returns:
            list[Equipment]: List of all equipment objects
        """
        return self._equipments

    def df_datas(self) -> pd.DataFrame:
        """
        Get all equipments as a pandas DataFrame.
        
        Returns:
            pd.DataFrame: DataFrame with columns: Name, Power, Usage Time, 
                         Schedule, Energie
        """
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
        """
        Calculate the total energy consumption of all equipments.
        
        Returns:
            float: Total daily energy consumption in Watt-hours (Wh)
        """
        return sum(equipment.daily_energy_consumption() for equipment in self._equipments)

    def total_power(self) -> float:
        """
        Calculate the total power of all equipments.
        
        Returns:
            float: Total power in Watts (W)
        """
        return sum(equipment.power for equipment in self._equipments)
    
    def get_hourly_profile(self) -> list[float]:
        """
        Get the total hourly consumption profile for all equipments.
        
        Aggregates the hourly consumption of all equipment to show
        the total power draw for each hour of the day.
        
        Returns:
            list[float]: List of 24 values representing total power consumption 
                        for each hour (Watts)
        """
        hourly_total = [0.0] * 24
        for equipment in self._equipments:
            hourly = equipment.get_hourly_consumption()
            for i in range(24):
                hourly_total[i] += hourly[i]
        return hourly_total

    def delete_equipment(self, equipment: Equipment) -> None:
        """
        Delete an equipment from the factory.
        
        Args:
            equipment: Equipment object to delete
        """
        self._equipments.remove(equipment)

    def delete_all_equipments(self) -> None:
        """Delete all equipments from the factory."""
        self._equipments.clear()

    def is_empty(self) -> bool:
        """
        Check if the factory is empty.
        
        Returns:
            bool: True if no equipment, False otherwise
        """
        return len(self._equipments) == 0

    def edit_equipment(
        self, 
        old_equipment: Equipment, 
        new_name: str, 
        new_power: int, 
        new_time: float, 
        new_start_hour: int = 0
    ) -> None:
        """
        Edit an existing equipment.
        
        Args:
            old_equipment: Equipment object to edit
            new_name: New name for the equipment
            new_power: New power consumption in Watts
            new_time: New daily usage time in hours
            new_start_hour: New start hour (0-23)
            
        Raises:
            ValueError: If equipment not found
        """
        if old_equipment in self._equipments:
            index = self._equipments.index(old_equipment)
            self._equipments[index] = Equipment(new_name, new_power, new_time, new_start_hour)
        else:
            raise ValueError(f"Equipment {old_equipment.name} not found.")

    def get_equipment_by_name(self, name: str) -> Optional[Equipment]:
        """
        Get an equipment by its name.
        
        Args:
            name: Name of the equipment to find
            
        Returns:
            Equipment | None: Equipment object if found, None otherwise
        """
        for equipment in self._equipments:
            if equipment.name == name:
                return equipment
        return None
