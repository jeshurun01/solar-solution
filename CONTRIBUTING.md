# 🤝 Guide de Contribution - Solar Solution

Merci de votre intérêt pour contribuer à Solar Solution ! Ce document vous guidera à travers le processus de contribution.

---

## 📋 Table des Matières

1. [Code de Conduite](#code-de-conduite)
2. [Comment Contribuer](#comment-contribuer)
3. [Configuration de l'Environnement](#configuration-de-lenvironnement)
4. [Standards de Code](#standards-de-code)
5. [Tests](#tests)
6. [Processus de Pull Request](#processus-de-pull-request)
7. [Convention de Commit](#convention-de-commit)
8. [Architecture du Projet](#architecture-du-projet)

---

## 🌟 Code de Conduite

### Nos Engagements

Ce projet adhère aux principes suivants :
- **Respect** : Traiter tous les contributeurs avec respect et dignité
- **Inclusivité** : Créer un environnement accueillant pour tous
- **Collaboration** : Encourager le travail d'équipe et l'entraide
- **Qualité** : Maintenir des standards élevés de code et documentation

### Comportements Inacceptables

- Langage ou images inappropriés
- Attaques personnelles ou trolling
- Harcèlement public ou privé
- Publication d'informations privées sans permission

---

## 🚀 Comment Contribuer

### Types de Contributions

Nous accueillons différents types de contributions :

#### 1. 🐛 Signaler des Bugs

Créez une issue avec :
- **Titre clair** : Résumé du problème
- **Description** : Étapes pour reproduire
- **Environnement** : OS, Python version, navigateur
- **Comportement attendu vs actuel**
- **Captures d'écran** si applicable

**Template Bug Report:**
```markdown
**Description du Bug**
Description claire et concise du bug.

**Étapes pour Reproduire**
1. Aller à '...'
2. Cliquer sur '...'
3. Voir l'erreur

**Comportement Attendu**
Ce qui devrait se passer.

**Comportement Actuel**
Ce qui se passe réellement.

**Environnement**
- OS: [e.g., Ubuntu 22.04]
- Python: [e.g., 3.13]
- Streamlit: [e.g., 1.45.1]
- Navigateur: [e.g., Chrome 120]

**Captures d'Écran**
Si applicable, ajoutez des captures d'écran.
```

#### 2. 💡 Proposer des Fonctionnalités

Créez une issue avec :
- **Cas d'usage** : Problème que ça résout
- **Solution proposée** : Comment ça devrait fonctionner
- **Alternatives** : Autres approches considérées
- **Mockups/Wireframes** si applicable

**Template Feature Request:**
```markdown
**Problème à Résoudre**
Quel problème cette fonctionnalité résout-elle ?

**Solution Proposée**
Description claire de la fonctionnalité.

**Alternatives Considérées**
Autres solutions envisagées.

**Bénéfices**
- Bénéfice 1
- Bénéfice 2

**Complexité Estimée**
[Facile / Moyenne / Difficile]
```

#### 3. 📝 Améliorer la Documentation

- Corriger des typos
- Clarifier des sections confuses
- Ajouter des exemples
- Traduire dans d'autres langues

#### 4. 🔧 Contribuer du Code

Voir sections ci-dessous pour les détails.

---

## 🛠️ Configuration de l'Environnement

### Prérequis

- **Python 3.13+**
- **uv** (gestionnaire de paquets rapide)
- **Git**

### Installation

1. **Forker le Repository**
   ```bash
   # Sur GitHub, cliquer sur "Fork"
   ```

2. **Cloner votre Fork**
   ```bash
   git clone https://github.com/VOTRE-USERNAME/solar-solution.git
   cd solar-solution
   ```

3. **Configurer le Remote Upstream**
   ```bash
   git remote add upstream https://github.com/jeshurun01/solar-solution.git
   ```

4. **Installer les Dépendances**
   ```bash
   # Installation avec uv (recommandé)
   uv pip install -e ".[dev]"
   
   # Ou avec pip
   pip install -e ".[dev]"
   ```

5. **Vérifier l'Installation**
   ```bash
   # Lancer les tests
   pytest tests/ -v
   
   # Lancer l'application
   streamlit run main.py
   ```

### Structure des Branches

- `main` : Code stable en production
- `develop` : Branche de développement
- `feature/*` : Nouvelles fonctionnalités
- `bugfix/*` : Corrections de bugs
- `hotfix/*` : Corrections urgentes
- `docs/*` : Documentation

---

## 📐 Standards de Code

### Style Python

Nous suivons **PEP 8** avec quelques adaptations :

#### Longueur de Ligne
```python
# Maximum 100 caractères (pas 79)
# OK
result = calculate_battery_needed(daily_energy, voltage, capacity, autonomy, depth)

# À éviter (trop long)
result = calculate_battery_needed(daily_energy_consumption_wh, battery_voltage_v, battery_capacity_ah, autonomy_days, discharge_depth_percentage)
```

#### Nommage

```python
# Classes : PascalCase
class Equipment:
    pass

class EquipmentFactory:
    pass

# Fonctions/Variables : snake_case
def calculate_battery_needed():
    total_energy = 0
    num_batteries = 0

# Constantes : UPPER_CASE
MAX_VOLTAGE_DROP = 3.0
COPPER_RESISTIVITY = 0.01724

# Privé : préfixe underscore
def _internal_helper():
    pass

class MyClass:
    def __init__(self):
        self._private_var = 0
```

#### Imports

```python
# Standard library
import json
from pathlib import Path
from datetime import datetime

# Third-party
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Local
from models import Equipment, EquipmentFactory
from utils import battery_needed, panel_needed
```

### Type Hints

**Obligatoire** pour toutes les fonctions publiques :

```python
from typing import Optional, Dict, List

def calculate_roi(
    total_cost: float,
    daily_energy_kwh: float,
    electricity_price_per_kwh: float
) -> Dict[str, float]:
    """Calculate return on investment."""
    # Implementation
    pass

def get_equipment_by_name(name: str) -> Optional[Equipment]:
    """Get equipment by name or None if not found."""
    # Implementation
    pass
```

### Docstrings

**Google Style** obligatoire :

```python
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
            
    Examples:
        >>> specs = calculate_cable_section(50.0, 10.0, 12, 3.0)
        >>> print(f"Cable: {specs['cable_section']} mm²")
        Cable: 35.0 mm²
    """
    # Implementation
    pass
```

**Sections requises:**
- Description brève (1 ligne)
- Description détaillée (optionnelle)
- Args : Tous les paramètres
- Returns : Type et structure du retour
- Raises : Exceptions levées (si applicable)
- Examples : Au moins un exemple (recommandé)

### Commentaires

```python
# Bon : Expliquer le POURQUOI
# Calculate with 25% safety margin to handle peak loads
recommended_current = nominal_current * 1.25

# Mauvais : Expliquer le QUOI (évident)
# Multiply by 1.25
recommended_current = nominal_current * 1.25

# Formules complexes : documenter
# Formula: n = (E × A) / (V × C × DoD)
# Where:
#   E = Daily energy (Wh)
#   A = Autonomy days
#   V = Battery voltage (V)
#   C = Battery capacity (Ah)
#   DoD = Depth of discharge (0-1)
num_batteries = math.ceil((energy * autonomy) / (voltage * capacity * dod))
```

### Gestion d'Erreurs

```python
# Spécifique, pas générique
try:
    config = load_configuration(name)
except FileNotFoundError:
    logger.error(f"Configuration '{name}' not found")
    raise
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON in configuration: {e}")
    raise ValueError(f"Malformed configuration file: {name}")

# Éviter les except génériques
try:
    # ...
except Exception:  # ❌ Trop large
    pass
```

---

## 🧪 Tests

### Écriture de Tests

**Chaque fonctionnalité DOIT avoir des tests.**

#### Structure des Tests

```python
"""
Unit tests for XYZ module.

Tests cover:
- Feature 1
- Feature 2
- Edge cases
"""

import pytest
from module import function_to_test


class TestFeatureName:
    """Test cases for FeatureName"""
    
    def test_basic_case(self):
        """Test basic functionality"""
        # Arrange
        input_data = 100
        
        # Act
        result = function_to_test(input_data)
        
        # Assert
        assert result == expected_value
    
    def test_edge_case_zero(self):
        """Test with zero input"""
        result = function_to_test(0)
        assert result == 0
    
    def test_invalid_input_raises_error(self):
        """Test that invalid input raises appropriate error"""
        with pytest.raises(ValueError):
            function_to_test(-1)
```

#### Nommage des Tests

```python
# Pattern : test_<what>_<condition>_<expected>

def test_battery_needed_basic():
    """Test basic battery calculation"""
    pass

def test_battery_needed_zero_energy_returns_zero():
    """Test with zero energy consumption"""
    pass

def test_add_equipment_duplicate_name_raises_error():
    """Test that duplicate equipment raises ValueError"""
    pass
```

#### Assertions

```python
# Comparaisons exactes
assert result == expected_value
assert equipment.name == "Laptop"

# Comparaisons approximatives (float)
assert pytest.approx(result, 0.01) == 9.13

# Collections
assert len(equipments) == 3
assert "Laptop" in equipment_names

# Exceptions
with pytest.raises(ValueError) as exc_info:
    factory.add_equipment("Duplicate", 100, 2.0)
assert "already exists" in str(exc_info.value)

# Booléens
assert factory.is_empty()
assert not equipment.is_active()
```

### Exécution des Tests

```bash
# Tous les tests
pytest tests/ -v

# Tests spécifiques
pytest tests/test_models.py -v
pytest tests/test_models.py::TestEquipment -v
pytest tests/test_models.py::TestEquipment::test_creation -v

# Avec couverture
pytest tests/ --cov=models --cov=utils --cov-report=html

# Mode watch (re-run on file change)
pytest-watch tests/

# Parallèle (plus rapide)
pytest tests/ -n auto
```

### Couverture de Code

**Objectif : 80%+ de couverture**

```bash
# Générer rapport
pytest tests/ --cov=models --cov=utils --cov-report=html

# Ouvrir rapport
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**Lignes à exclure de la couverture:**
```python
# pragma: no cover - pour code non testable
if TYPE_CHECKING:  # pragma: no cover
    from models import Equipment

def debug_only_function():  # pragma: no cover
    """Function used only for debugging"""
    pass
```

---

## 🔄 Processus de Pull Request

### Avant de Créer une PR

1. **Créer une branche**
   ```bash
   git checkout -b feature/ma-nouvelle-fonctionnalite
   ```

2. **Faire des commits atomiques**
   ```bash
   git add fichier1.py
   git commit -m "feat: add battery temperature compensation"
   
   git add test_fichier1.py
   git commit -m "test: add tests for temperature compensation"
   ```

3. **Synchroniser avec upstream**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

4. **Exécuter tous les tests**
   ```bash
   pytest tests/ -v
   ```

5. **Vérifier le style**
   ```bash
   # Optionnel : utiliser black, flake8, mypy
   black .
   flake8 models/ utils/
   mypy models/ utils/
   ```

### Créer la Pull Request

1. **Pousser votre branche**
   ```bash
   git push origin feature/ma-nouvelle-fonctionnalite
   ```

2. **Ouvrir une PR sur GitHub**
   - Titre clair et descriptif
   - Description détaillée (voir template ci-dessous)
   - Lier les issues concernées

**Template Pull Request:**
```markdown
## Description
Brève description des changements.

## Type de Changement
- [ ] 🐛 Bug fix (changement non-breaking qui corrige un problème)
- [ ] ✨ New feature (changement non-breaking qui ajoute une fonctionnalité)
- [ ] 💥 Breaking change (correction ou fonctionnalité qui casse la compatibilité)
- [ ] 📝 Documentation (changements de documentation uniquement)
- [ ] ♻️ Refactoring (changement de code sans modification de fonctionnalité)
- [ ] ⚡ Performance (amélioration des performances)
- [ ] ✅ Tests (ajout ou correction de tests)

## Comment Tester
1. Étape 1
2. Étape 2
3. Résultat attendu

## Checklist
- [ ] Mon code suit les standards du projet
- [ ] J'ai commenté mon code, particulièrement les parties complexes
- [ ] J'ai mis à jour la documentation
- [ ] Mes changements ne génèrent pas de nouveaux warnings
- [ ] J'ai ajouté des tests qui prouvent que ma correction/fonctionnalité marche
- [ ] Les tests unitaires passent localement
- [ ] Les dépendances sont à jour dans pyproject.toml

## Issues Liées
Closes #123
Related to #456

## Captures d'Écran (si applicable)
```

### Review Process

1. **Automated Checks** (CI/CD)
   - Tests unitaires
   - Couverture de code
   - Linting
   - Type checking

2. **Code Review**
   - Au moins 1 approbation requise
   - Répondre aux commentaires
   - Faire les changements demandés

3. **Merge**
   - Squash & merge (commits propres)
   - Delete branch après merge

---

## 📝 Convention de Commit

Nous utilisons **Conventional Commits** :

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation uniquement
- `style`: Formatage, points-virgules, etc. (pas de changement de code)
- `refactor`: Refactoring (ni fix ni feat)
- `perf`: Amélioration des performances
- `test`: Ajout ou correction de tests
- `chore`: Maintenance (dépendances, config, etc.)
- `ci`: CI/CD (GitHub Actions, etc.)
- `build`: Système de build (pip, uv, etc.)
- `revert`: Revert d'un commit précédent

### Scopes (optionnels)

- `models`: Modèles de données
- `utils`: Utilitaires
- `ui`: Interface utilisateur
- `tests`: Tests
- `docs`: Documentation
- `i18n`: Internationalisation

### Exemples

```bash
# Feature
git commit -m "feat(models): add temperature compensation for batteries"

# Bug fix
git commit -m "fix(utils): correct voltage drop calculation in cables"

# Documentation
git commit -m "docs(readme): add installation instructions for Windows"

# Refactoring
git commit -m "refactor(utils): extract cable calculation to separate function"

# Tests
git commit -m "test(models): add tests for hourly consumption profile"

# Breaking change
git commit -m "feat(models)!: change Equipment constructor signature

BREAKING CHANGE: Equipment now requires start_hour parameter"

# Multiple scopes
git commit -m "feat(models,utils): add battery aging calculations"
```

### Body et Footer

```bash
git commit -m "feat(models): add battery temperature compensation

Temperature affects battery capacity and should be accounted for
in sizing calculations. This adds a temperature parameter with
default value of 25°C.

Implements the Arrhenius equation for capacity correction:
C_t = C_25 × exp(k × (T - 25))

Closes #123
Refs #456"
```

---

## 🏗️ Architecture du Projet

### Structure des Dossiers

```
solar_solution/
├── main.py                 # Application Streamlit principale
├── models/                 # Modèles de données
│   ├── __init__.py
│   └── equipment.py        # Equipment, EquipmentFactory
├── utils/                  # Fonctions utilitaires
│   ├── __init__.py
│   ├── calculations.py     # Calculs (batteries, panneaux, etc.)
│   ├── charts.py          # Graphiques Plotly
│   ├── storage.py         # Sauvegarde/chargement
│   └── translations.py    # Gestion des langues
├── tests/                 # Tests unitaires
│   ├── __init__.py
│   ├── test_models.py
│   └── test_calculations.py
├── locals/                # Fichiers de traduction
│   ├── en.json
│   └── fr.json
├── saved_configs/         # Configurations sauvegardées (gitignored)
├── equipment_library.json # Bibliothèque d'équipements
├── pyproject.toml        # Configuration du projet
├── pytest.ini            # Configuration pytest
├── README.md
├── CONTRIBUTING.md       # Ce fichier
├── ACTION_PLAN.md        # Plan de développement
└── .gitignore
```

### Principes Architecturaux

1. **Separation of Concerns**
   - Models : Logique métier
   - Utils : Fonctions pures
   - Main : UI et orchestration

2. **Single Responsibility**
   - Chaque module a une responsabilité unique
   - Fonctions courtes et focalisées

3. **Dependency Injection**
   - Passer les dépendances explicitement
   - Éviter les variables globales

4. **Testabilité**
   - Fonctions pures autant que possible
   - Mocking facile

### Ajouter un Nouveau Module

1. **Créer le fichier**
   ```bash
   touch utils/new_feature.py
   ```

2. **Ajouter docstring de module**
   ```python
   """
   Description of the module.
   
   This module provides...
   """
   ```

3. **Implémenter avec tests**
   ```bash
   touch tests/test_new_feature.py
   ```

4. **Exporter dans __init__.py**
   ```python
   # utils/__init__.py
   from .new_feature import my_function
   
   __all__ = [..., "my_function"]
   ```

5. **Documenter**
   - Ajouter dans README.md
   - Mettre à jour TECHNICAL.md

---

## 📚 Ressources

### Documentation

- [README.md](README.md) - Vue d'ensemble du projet
- [ACTION_PLAN.md](ACTION_PLAN.md) - Roadmap et progression
- [PHASE4_PROGRESS.md](PHASE4_PROGRESS.md) - Détails Phase 4
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Conventional Commits](https://www.conventionalcommits.org/)

### Outils Utiles

- **Formatter:** [black](https://github.com/psf/black)
- **Linter:** [flake8](https://flake8.pycqa.org/)
- **Type Checker:** [mypy](http://mypy-lang.org/)
- **Test Runner:** [pytest](https://pytest.org/)
- **Coverage:** [pytest-cov](https://pytest-cov.readthedocs.io/)

### Contact

- **Issues:** [GitHub Issues](https://github.com/jeshurun01/solar-solution/issues)
- **Discussions:** [GitHub Discussions](https://github.com/jeshurun01/solar-solution/discussions)
- **Email:** [maintainer email]

---

## 🙏 Remerciements

Merci à tous les contributeurs qui rendent ce projet possible !

### Hall of Fame

Consultez [CONTRIBUTORS.md](CONTRIBUTORS.md) pour la liste complète des contributeurs.

---

## 📄 Licence

En contribuant, vous acceptez que vos contributions soient sous la même licence que le projet (MIT License).

---

**Bon code ! 🚀**

*Dernière mise à jour : Octobre 2025*
