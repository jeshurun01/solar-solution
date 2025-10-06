#!/usr/bin/env python3
"""Script pour remplacer tous les emojis par des icônes Material Design"""

import re
from pathlib import Path

# Mapping emoji → Material icon
EMOJI_MAPPING = {
    # Navigation principale
    "🏠": ":material/home:",
    "⚡": ":material/bolt:",
    "🔋": ":material/battery_charging_full:",
    "📄": ":material/description:",
    
    # Actions
    "📋": ":material/list:",
    "🗑️": ":material/delete:",
    "✏️": ":material/edit:",
    "💾": ":material/save:",
    "📂": ":material/folder_open:",
    "🖨️": ":material/print:",
    "📊": ":material/analytics:",
    "📈": ":material/trending_up:",
    
    # Métriques et indicateurs
    "💰": ":material/attach_money:",
    "🌳": ":material/park:",
    "💡": ":material/lightbulb:",
    "🔌": ":material/power:",
    "☀️": ":material/wb_sunny:",
    "🌙": ":material/nights_stay:",
    "⚙️": ":material/settings:",
    "📏": ":material/straighten:",
    "🔧": ":material/build:",
    "⚖️": ":material/balance:",
    "🎯": ":material/target:",
    "✅": ":material/check_circle:",
    "❌": ":material/cancel:",
    "⚠️": ":material/warning:",
    "ℹ️": ":material/info:",
    "📝": ":material/edit_note:",
    "🔍": ":material/search:",
    "📅": ":material/calendar_today:",
    "🏢": ":material/business:",
    "📍": ":material/location_on:",
    "📞": ":material/phone:",
    "✉️": ":material/email:",
}

def replace_emojis_in_file(file_path: Path) -> int:
    """Remplace tous les emojis dans un fichier"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Remplacer chaque emoji
        for emoji, icon in EMOJI_MAPPING.items():
            content = content.replace(emoji, icon)
        
        # Compter les changements
        changes = sum(1 for e in EMOJI_MAPPING if e in original_content)
        
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            print(f"✓ {file_path.name}: {changes} emojis remplacés")
            return changes
        return 0
        
    except Exception as e:
        print(f"✗ {file_path.name}: Erreur - {e}")
        return 0

def main():
    """Point d'entrée principal"""
    base_dir = Path(__file__).parent
    
    # Fichiers à traiter
    files_to_process = [
        base_dir / "app.py",
        base_dir / "pages" / "1_⚡_Equipments.py",
        base_dir / "pages" / "2_🔋_Calculations.py", 
        base_dir / "pages" / "3_📄_Report.py",
        base_dir / "main.py",
        base_dir / "main_new.py",
    ]
    
    total_changes = 0
    files_changed = 0
    
    print("🔄 Remplacement des emojis par des icônes Material Design...\n")
    
    for file_path in files_to_process:
        if file_path.exists():
            changes = replace_emojis_in_file(file_path)
            if changes > 0:
                total_changes += changes
                files_changed += 1
        else:
            print(f"⚠ {file_path.name}: Fichier introuvable")
    
    print(f"\n✅ Terminé: {total_changes} emojis remplacés dans {files_changed} fichiers")

if __name__ == "__main__":
    main()
