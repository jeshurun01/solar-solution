"""
Translation utilities for Solar Solution.

This module handles loading and managing translations for different languages.
"""

import json
from pathlib import Path
from typing import Dict, Any


def load_translation(language_code: str) -> Dict[str, Any]:
    """
    Load translation file for the specified language.
    
    Args:
        language_code: ISO 639-1 language code (e.g., 'en', 'fr', 'es')
        
    Returns:
        dict: Translation dictionary with all text strings
        
    Raises:
        FileNotFoundError: If translation file doesn't exist
        json.JSONDecodeError: If translation file is malformed
    """
    translation_path = Path(f"locals/{language_code}.json")
    
    if not translation_path.exists():
        raise FileNotFoundError(f"Translation file not found: {translation_path}")
    
    with open(translation_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_available_languages() -> list[str]:
    """
    Get list of available language codes.
    
    Returns:
        list[str]: List of ISO 639-1 language codes
    """
    locals_path = Path("locals")
    if not locals_path.exists():
        return []
    
    # Find all .json files in locals directory
    language_files = locals_path.glob("*.json")
    
    # Extract language codes from filenames
    return [f.stem for f in language_files]
