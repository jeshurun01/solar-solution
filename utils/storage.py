"""
Storage utilities for Solar Solution.

This module handles saving, loading, and managing configurations and equipment library.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from models import EquipmentFactory

# Storage directory for saved configurations
STORAGE_DIR = Path("saved_configs")
STORAGE_DIR.mkdir(exist_ok=True)


def save_configuration(name: str, factory: "EquipmentFactory") -> None:
    """
    Save current equipment configuration to JSON file.
    
    Args:
        name: Name for the configuration
        factory: EquipmentFactory instance with equipment data
        
    The configuration includes:
    - Configuration name
    - Timestamp
    - List of all equipment with their properties
    """
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


def load_configuration(name: str) -> List[Dict[str, Any]]:
    """
    Load equipment configuration from JSON file.
    
    Args:
        name: Name of the configuration to load
        
    Returns:
        list[dict]: List of equipment dictionaries with keys:
                   name, power, time, start_hour
                   
    Raises:
        FileNotFoundError: If configuration file doesn't exist
        json.JSONDecodeError: If configuration file is malformed
    """
    file_path = STORAGE_DIR / f"{name}.json"
    with open(file_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config["equipments"]


def get_saved_configurations() -> List[str]:
    """
    Get list of saved configuration names.
    
    Returns:
        list[str]: List of configuration names (without .json extension)
    """
    return [f.stem for f in STORAGE_DIR.glob("*.json")]


def delete_configuration(name: str) -> None:
    """
    Delete a saved configuration.
    
    Args:
        name: Name of the configuration to delete
    """
    file_path = STORAGE_DIR / f"{name}.json"
    if file_path.exists():
        file_path.unlink()


def load_equipment_library() -> Dict[str, Any]:
    """
    Load equipment library from JSON file.
    
    The library contains pre-configured equipment organized by categories
    (kitchen, electronics, lighting, etc.) with power, time, and description.
    
    Returns:
        dict: Equipment library with structure:
            {
                "categories": {
                    "category_id": {
                        "name_en": str,
                        "name_fr": str,
                        "icon": str,
                        "items": [...]
                    }
                }
            }
    """
    library_path = Path("equipment_library.json")
    if library_path.exists():
        with open(library_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"categories": {}}


def get_library_categories(library: Dict[str, Any], lang: str) -> Dict[str, Any]:
    """
    Get categories with translated names based on language.
    
    Args:
        library: Equipment library dictionary
        lang: Language code (e.g., 'en', 'fr')
        
    Returns:
        dict: Categories with translated names and items:
            {
                "category_id": {
                    "name": str,
                    "icon": str,
                    "items": [...]
                }
            }
    """
    categories = {}
    for cat_id, cat_data in library.get("categories", {}).items():
        name_key = f"name_{lang}"
        categories[cat_id] = {
            "name": cat_data.get(name_key, cat_data.get("name_en", cat_id)),
            "icon": cat_data.get("icon", ""),
            "items": cat_data.get("items", [])
        }
    return categories
