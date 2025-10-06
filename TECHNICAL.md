# 🔧 Documentation Technique - Solar Solution

Documentation technique complète du projet Solar Solution.

---

## 📋 Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Architecture](#architecture)
3. [Modèles de Données](#modèles-de-données)
4. [Modules Utilitaires](#modules-utilitaires)
5. [Interface Utilisateur](#interface-utilisateur)
6. [Flux de Données](#flux-de-données)
7. [Formules et Algorithmes](#formules-et-algorithmes)
8. [Internationalisation](#internationalisation)
9. [Stockage](#stockage)
10. [Performance](#performance)

---

## 🌐 Vue d'Ensemble

### Description

Solar Solution est une application web de dimensionnement de systèmes solaires photovoltaïques. Elle permet de calculer :
- Le nombre de batteries nécessaires
- Le nombre de panneaux solaires requis
- Les spécifications du régulateur de charge
- La section des câbles
- L'analyse économique (ROI, CO₂)
- Les profils de consommation horaire

### Technologies

| Composant | Technologie | Version | Usage |
|-----------|-------------|---------|-------|
| **Framework Web** | Streamlit | 1.45.1+ | Interface utilisateur |
| **Calculs Scientifiques** | Python | 3.13+ | Logique métier |
| **Visualisation** | Plotly | 5.24.0+ | Graphiques interactifs |
| **Data Manipulation** | Pandas | 2.2.0+ | Gestion des données tabulaires |
| **Package Manager** | uv | latest | Gestion des dépendances |
| **Tests** | pytest | 8.0.0+ | Tests unitaires |
| **Coverage** | pytest-cov | 4.1.0+ | Couverture de code |

### Paradigmes

- **Object-Oriented** : Classes Equipment, EquipmentFactory
- **Functional** : Fonctions pures pour les calculs
- **Type-Safe** : Type hints complets (Python 3.13+)
- **Test-Driven** : 48 tests unitaires, 72% coverage

---

## 🏗️ Architecture

### Vue Globale

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI Layer                   │
│                      (main.py)                          │
└────────────┬───────────────────────────┬────────────────┘
             │                           │
    ┌────────▼────────┐          ┌───────▼────────┐
    │   Models Layer  │          │  Utils Layer   │
    │ (Business Logic)│          │(Pure Functions)│
    └────────┬────────┘          └───────┬────────┘
             │                           │
    ┌────────▼───────────────────────────▼────────┐
    │           Storage & I/O Layer               │
    │  (JSON files, configurations, library)      │
    └─────────────────────────────────────────────┘
```

### Structure des Modules

```
solar_solution/
│
├── 🎨 UI Layer (Presentation)
│   └── main.py                    # Streamlit app, user interface
│
├── 📦 Models Layer (Business Logic)
│   └── models/
│       ├── __init__.py
│       └── equipment.py           # Equipment, EquipmentFactory
│
├── 🔧 Utils Layer (Application Services)
│   └── utils/
│       ├── __init__.py
│       ├── calculations.py        # Pure calculation functions
│       ├── charts.py              # Plotly chart generation
│       ├── storage.py             # Configuration persistence
│       └── translations.py        # i18n management
│
├── 🧪 Test Layer
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py         # Model tests
│       └── test_calculations.py   # Calculation tests
│
└── 📁 Data Layer
    ├── locals/                    # Translation files
    │   ├── en.json
    │   └── fr.json
    ├── equipment_library.json     # Equipment database
    └── saved_configs/             # User configurations
```

### Dépendances entre Modules

```
main.py
  ├─→ models.equipment
  │     └─→ pandas (DataFrame)
  │
  └─→ utils.calculations
  └─→ utils.charts
        └─→ models.equipment (for data)
        └─→ plotly
  └─→ utils.storage
        └─→ models.equipment (serialization)
  └─→ utils.translations
```

**Règles de dépendance:**
- `models/` ne dépend de rien (logique métier pure)
- `utils/` peut dépendre de `models/` mais pas vice-versa
- `main.py` orchestre tout mais ne contient pas de logique métier

---

## 📦 Modèles de Données

### Equipment

**Responsabilité:** Représenter un équipement électrique avec sa consommation.

```python
class Equipment:
    """
    Represents an electrical equipment.
    
    Attributes:
        name (str): Equipment name (unique identifier)
        power (int): Power consumption in Watts
        time (float): Daily usage time in hours
        start_hour (int): Hour when equipment starts (0-23)
        end_hour (int): Hour when equipment ends (0-23)
    """
```

**Diagramme de Classe:**
```
┌─────────────────────────────────────┐
│          Equipment                  │
├─────────────────────────────────────┤
│ - name: str                         │
│ - power: int                        │
│ - time: float                       │
│ - start_hour: int                   │
│ - end_hour: int                     │
├─────────────────────────────────────┤
│ + __init__(...)                     │
│ + daily_energy_consumption() → float│
│ + get_hourly_consumption() → list   │
│ + __eq__(other) → bool              │
│ + __str__() → str                   │
│ + __repr__() → str                  │
└─────────────────────────────────────┘
```

**Méthodes Clés:**

1. **`daily_energy_consumption()`**
   - Calcul : `power × time`
   - Retour : Énergie en Watt-heures (Wh)
   - Complexité : O(1)

2. **`get_hourly_consumption()`**
   - Distribue la puissance sur les heures d'utilisation
   - Gère les heures partielles
   - Gère le wraparound de minuit
   - Retour : Liste de 24 valeurs (Watts par heure)
   - Complexité : O(time) ≈ O(1) car time < 24

**Exemple:**
```python
# Laptop utilisé 4h à partir de 9h
laptop = Equipment("Laptop", power=65, time=4.0, start_hour=9)

# Consommation journalière
energy = laptop.daily_energy_consumption()  # 260 Wh

# Profil horaire
hourly = laptop.get_hourly_consumption()
# [0, 0, 0, 0, 0, 0, 0, 0, 0, 65, 65, 65, 65, 0, ...]
#  0h 1h 2h ... 8h 9h 10h 11h 12h 13h ...
```

### EquipmentFactory

**Responsabilité:** Gérer une collection d'équipements (pattern Factory + Repository).

```python
class EquipmentFactory:
    """
    Factory for managing Equipment collection.
    
    Attributes:
        _equipments (list[Equipment]): Internal equipment list
    """
```

**Diagramme de Classe:**
```
┌──────────────────────────────────────────┐
│       EquipmentFactory                   │
├──────────────────────────────────────────┤
│ - _equipments: list[Equipment]           │
├──────────────────────────────────────────┤
│ + __init__()                             │
│ + add_equipment(...)                     │
│ + get_equipments() → list                │
│ + df_datas() → DataFrame                 │
│ + total_energy_consumption() → float     │
│ + total_power() → float                  │
│ + get_hourly_profile() → list            │
│ + delete_equipment(eq)                   │
│ + delete_all_equipments()                │
│ + is_empty() → bool                      │
│ + edit_equipment(...)                    │
│ + get_equipment_by_name(name) → Equipment│
└──────────────────────────────────────────┘
           │
           │ contains
           ▼
     ┌─────────────┐
     │  Equipment  │
     └─────────────┘
       0..*
```

**Méthodes Clés:**

1. **`add_equipment()`**
   - Validation : Pas de doublons (basé sur le nom)
   - Lève : `ValueError` si équipement existe déjà
   - Complexité : O(n) pour vérifier doublons

2. **`get_hourly_profile()`**
   - Agrège les profils horaires de tous les équipements
   - Retour : Somme des consommations par heure
   - Complexité : O(n × 24) ≈ O(n)

3. **`df_datas()`**
   - Convertit la collection en DataFrame Pandas
   - Colonnes : Name, Power, Usage Time, Schedule, Energie
   - Usage : Affichage UI, export CSV

**Invariants:**
- Pas de doublons (unicité par nom)
- `_equipments` toujours une liste valide (jamais None)

---

## 🔧 Modules Utilitaires

### calculations.py

**Responsabilité:** Fonctions pures de calcul (batteries, panneaux, économie).

#### Fonctions de Dimensionnement

**1. `battery_needed()`**

```python
def battery_needed(
    daily_energy_wh: float,
    battery_voltage: int,
    battery_capacity_ah: int,
    autonomy_days: int,
    discharge_depth: float
) -> int:
    """Calculate number of batteries needed."""
```

**Formule:**
```
n = ⌈(E × A) / (V × C × DoD)⌉

Où:
  E = Énergie journalière (Wh)
  A = Jours d'autonomie
  V = Tension batterie (V)
  C = Capacité batterie (Ah)
  DoD = Profondeur de décharge (0-1)
```

**Exemple:**
```python
# 2400 Wh/jour, batteries 12V/200Ah, 2 jours autonomie, DoD 50%
n = battery_needed(2400, 12, 200, 2, 0.5)
# Calcul: (2400 × 2) / (12 × 200 × 0.5) = 4800 / 1200 = 4 batteries
```

**2. `panel_needed()`**

```python
def panel_needed(
    daily_energy_wh: float,
    pv_power_w: int,
    sun_hours: float
) -> int:
    """Calculate number of solar panels needed."""
```

**Formule:**
```
n = ⌈E / (P × H)⌉

Où:
  E = Énergie journalière (Wh)
  P = Puissance panneau (W)
  H = Heures d'ensoleillement de pointe
```

**Exemple:**
```python
# 3000 Wh/jour, panneaux 300W, 5h de soleil
n = panel_needed(3000, 300, 5.0)
# Calcul: 3000 / (300 × 5) = 3000 / 1500 = 2 panneaux
```

#### Fonctions Économiques

**3. `calculate_roi()`**

```python
def calculate_roi(
    total_cost: float,
    daily_energy_kwh: float,
    electricity_price_per_kwh: float
) -> Dict[str, float]:
    """Calculate ROI and savings."""
```

**Formule:**
```
Économies journalières = E × Prix
ROI (années) = Coût total / Économies annuelles
```

**Retour:**
```python
{
    "daily": 1.5,      # €/jour
    "monthly": 45.0,   # €/mois
    "annual": 547.5,   # €/an
    "roi_years": 9.13  # années
}
```

**4. `calculate_co2_impact()`**

**Formule:**
```
CO₂ évité (kg) = Énergie annuelle (kWh) × 0.5 kg/kWh
Arbres équivalents = CO₂ (kg) / 21 kg/arbre/an
```

**Constantes utilisées:**
- 0.5 kg CO₂/kWh (moyenne européenne)
- 21 kg CO₂/arbre/an (absorption moyenne)

#### Fonctions Électriques

**5. `calculate_regulator()`**

```python
def calculate_regulator(
    pv_power: float,
    battery_voltage: int,
    regulator_type: str = "MPPT"
) -> Dict[str, Union[float, str]]:
    """Calculate charge controller specs."""
```

**Formule:**
```
Courant nominal (A) = Puissance PV (W) / Tension batterie (V)
Courant recommandé (A) = Courant nominal × 1.25  (marge sécurité)
```

**Types de régulateurs:**
- **MPPT** (Maximum Power Point Tracking) : 98% efficacité
- **PWM** (Pulse Width Modulation) : 85% efficacité

**6. `calculate_cable_section()`**

```python
def calculate_cable_section(
    current: float,
    length: float,
    voltage: int,
    max_drop_percent: float = 3.0
) -> Dict[str, float]:
    """Calculate cable section based on voltage drop."""
```

**Formule (Loi d'Ohm):**
```
S = (2 × ρ × I × L) / ΔV

Où:
  S = Section câble (mm²)
  ρ = Résistivité cuivre = 0.01724 Ω·mm²/m (20°C)
  I = Courant (A)
  L = Longueur aller (m)
  ΔV = Chute tension maximale admissible (V)
  
Factor 2: aller + retour du courant
```

**Sections standard (IEC):**
```python
[1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240]  # mm²
```

**Exemple:**
```python
# 50A, 10m, 12V système, 3% chute max
specs = calculate_cable_section(50.0, 10.0, 12, 3.0)

# Calcul:
# ΔV_max = 12 × 0.03 = 0.36V
# S_min = (2 × 0.01724 × 50 × 10) / 0.36 = 47.9 mm²
# Section standard suivante = 50 mm²

{
    "cable_section": 50.0,      # mm²
    "actual_drop_volts": 0.344, # V
    "actual_drop_percent": 2.87,# %
    "fuse_rating": 65,          # A
    "current": 50.0             # A
}
```

### charts.py

**Responsabilité:** Générer des graphiques interactifs Plotly.

#### Types de Graphiques

**1. Pie Chart (Camembert)**
```python
def create_consumption_pie_chart(
    factory: EquipmentFactory,
    t: Dict[str, Any]
) -> go.Figure:
```

- **Usage:** Répartition de la consommation par équipement
- **Données:** Énergie journalière (Wh) par équipement
- **Features:** Hole (donut), couleurs Set3, labels avec %

**2. Bar Chart (Double Axe)**
```python
def create_power_time_chart(
    factory: EquipmentFactory,
    t: Dict[str, Any]
) -> go.Figure:
```

- **Usage:** Comparer puissance (W) et temps d'utilisation (h)
- **Type:** Grouped bar chart avec 2 axes Y
- **Axes:** Y1 = Puissance, Y2 = Temps

**3. Line Chart (Profil Horaire)**
```python
def create_hourly_profile_chart(
    factory: EquipmentFactory,
    t: Dict[str, Any]
) -> go.Figure:
```

- **Usage:** Courbe de charge sur 24h
- **Features:**
  - Area chart pour consommation totale
  - Traces individuelles par équipement (hidden by default)
  - Lignes de référence (pic, moyenne)
  - Annotations automatiques
  - Hover interactif

**Architecture Graphique:**
```
create_*_chart()
    ├─→ factory.df_datas() ou factory.get_hourly_profile()
    ├─→ Plotly Graph Objects (go.Figure)
    ├─→ Translation dict (t) pour labels
    └─→ Return: go.Figure (ready for st.plotly_chart)
```

### storage.py

**Responsabilité:** Persistence des données (configurations, bibliothèque).

#### Configuration Management

**Format JSON:**
```json
{
  "name": "Ma Config",
  "timestamp": "2025-10-06T15:30:00",
  "equipments": [
    {
      "name": "Laptop",
      "power": 65,
      "time": 4.0,
      "start_hour": 9
    }
  ]
}
```

**Fonctions:**
```python
save_configuration(name, factory)      # Sauvegarde
load_configuration(name) → list[dict]  # Chargement
get_saved_configurations() → list[str] # Liste
delete_configuration(name)             # Suppression
```

**Répertoire:** `saved_configs/` (créé automatiquement, gitignored)

#### Equipment Library

**Format JSON:**
```json
{
  "categories": {
    "kitchen": {
      "name_en": "Kitchen",
      "name_fr": "Cuisine",
      "icon": "🍳",
      "items": [
        {
          "name": "Réfrigérateur / Refrigerator",
          "power": 150,
          "time": 24,
          "start_hour": 0,
          "description_fr": "Réfrigérateur standard 24h/24",
          "description_en": "Standard refrigerator 24/7"
        }
      ]
    }
  }
}
```

**Fonctions:**
```python
@st.cache_data
def load_equipment_library() → dict

def get_library_categories(library, lang) → dict
```

**Cache Streamlit:** `@st.cache_data` pour éviter rechargement constant.

### translations.py

**Responsabilité:** Gestion des traductions i18n.

**Structure Translation File:**
```json
{
  "title": "Solar Solution",
  "subtitle": "Dimensioning tool",
  "New Equipment": {
    "title": "Add Equipment",
    "name": "Name",
    "power": "Power (W)",
    ...
  }
}
```

**Fonctions:**
```python
def load_translation(language_code: str) → Dict[str, Any]
def get_available_languages() → list[str]
```

**Langues supportées:**
- `en` : English
- `fr` : Français
- (Extensible : es, ar, de...)

---

## 🎨 Interface Utilisateur

### Architecture Streamlit

```
┌────────────────────────────────────────────────────────┐
│                    Page Config                          │
│  (title, icon, layout)                                 │
└────────────────┬───────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
    ┌───▼────┐      ┌────▼──────────────────────────┐
    │Sidebar │      │     Main Content Area          │
    │        │      │                                │
    │  📋    │      │  ┌──────────────────────────┐  │
    │  Add   │      │  │   Title & Subtitle       │  │
    │        │      │  └──────────────────────────┘  │
    │  ✏️    │      │                                │
    │  Edit  │      │  ┌──────────────────────────┐  │
    │        │      │  │   Equipment List         │  │
    │  📚    │      │  │   (DataFrame)            │  │
    │Library │      │  └──────────────────────────┘  │
    │        │      │                                │
    │  ⚙️    │      │  ┌──────────┬──────────────┐  │
    │Actions │      │  │ Battery  │ Solar Panels │  │
    │        │      │  └──────────┴──────────────┘  │
    │  💾    │      │                                │
    │ Save/  │      │  ┌──────────────────────────┐  │
    │ Load   │      │  │   Charts (Tabs)          │  │
    │        │      │  │   - Pie                  │  │
    │  🗑️    │      │  │   - Bar                  │  │
    │Delete  │      │  │   - Hourly               │  │
    └────────┘      │  └──────────────────────────┘  │
                    │                                │
                    │  ┌──────────────────────────┐  │
                    │  │   Economics (Expander)   │  │
                    │  └──────────────────────────┘  │
                    │                                │
                    │  ┌──────────────────────────┐  │
                    │  │   Regulator & Wiring     │  │
                    │  └──────────────────────────┘  │
                    └────────────────────────────────┘
```

### Session State

**Variables d'état:**
```python
st.session_state = {
    "language": dict,           # Translation dict
    "equipments": EquipmentFactory()  # Factory instance
}
```

**Lifecycle:**
- Initialisé au premier chargement
- Persisté entre reruns
- Réinitialisé si page refresh

### Widget Flow

```
User Input (sidebar)
    │
    ├─→ Validation
    │     ├─→ Valid: Update session_state
    │     └─→ Invalid: Show error
    │
    ├─→ st.rerun() déclenché
    │
    └─→ Main area re-rendered avec nouvelles données
```

---

## 🔄 Flux de Données

### Ajout d'Équipement

```
1. User fills form (name, power, time, start_hour)
   │
2. Click "Add" button
   │
3. Validation
   ├─→ name non vide
   ├─→ power > 0
   └─→ time > 0
   │
4. factory.add_equipment(...)
   ├─→ Check duplicates
   └─→ Add to _equipments list
   │
5. st.success("Equipment added")
   │
6. st.rerun()
   │
7. UI refresh
   ├─→ DataFrame updated
   ├─→ Metrics recalculated
   ├─→ Charts regenerated
   └─→ Calculations updated
```

### Calcul Système Complet

```
User Inputs
   ├─→ Equipments (via factory)
   ├─→ Battery specs (V, Ah, DoD, days)
   ├─→ PV specs (W, sun hours)
   └─→ System config (voltage, regulator, cable)
        │
        ▼
    Calculations
        ├─→ total_energy = Σ(power × time)
        ├─→ total_power = Σ(power)
        │
        ├─→ num_batteries = battery_needed(...)
        ├─→ num_panels = panel_needed(...)
        │
        ├─→ costs = calculate_system_cost(...)
        ├─→ roi = calculate_roi(...)
        ├─→ co2 = calculate_co2_impact(...)
        │
        ├─→ regulator = calculate_regulator(...)
        └─→ cable = calculate_cable_section(...)
            │
            ▼
        Display Results
            ├─→ Metrics (st.metric)
            ├─→ Charts (st.plotly_chart)
            ├─→ Info boxes (st.info)
            └─→ Expanders (st.expander)
```

---

## 📐 Formules et Algorithmes

### Dimensionnement Batteries

**Objectif:** Stocker l'énergie pour plusieurs jours d'autonomie.

**Paramètres:**
- `E` : Énergie journalière (Wh)
- `A` : Jours d'autonomie
- `V` : Tension batterie (V)
- `C` : Capacité batterie (Ah)
- `DoD` : Profondeur de décharge (0-1)

**Formule:**
```
Énergie nécessaire = E × A
Énergie par batterie = V × C × DoD
Nombre de batteries = ⌈Énergie nécessaire / Énergie par batterie⌉
```

**Exemple numérique:**
```
E = 2400 Wh/jour
A = 2 jours
V = 12 V
C = 200 Ah
DoD = 0.5 (50%)

Énergie nécessaire = 2400 × 2 = 4800 Wh
Énergie par batterie = 12 × 200 × 0.5 = 1200 Wh
Nombre = ⌈4800 / 1200⌉ = 4 batteries
```

**Notes:**
- DoD = 0.5 pour batteries plomb-acide (vie longue)
- DoD = 0.8 pour batteries lithium (tolèrent mieux)
- Toujours arrondir au supérieur (sécurité)

### Dimensionnement Panneaux Solaires

**Objectif:** Produire assez d'énergie en journée.

**Paramètres:**
- `E` : Énergie journalière (Wh)
- `P` : Puissance panneau (W)
- `H` : Heures ensoleillement de pointe

**Formule:**
```
Production par panneau = P × H
Nombre de panneaux = ⌈E / Production par panneau⌉
```

**Exemple numérique:**
```
E = 3000 Wh/jour
P = 300 W
H = 5 heures

Production = 300 × 5 = 1500 Wh/panneau
Nombre = ⌈3000 / 1500⌉ = 2 panneaux
```

**Notes:**
- H varie selon latitude et saison
- Compte déjà les pertes (rendement ~15-20%)
- Orientation optimale : sud (hémisphère nord)

### Section de Câble (Voltage Drop)

**Objectif:** Limiter les pertes en ligne.

**Paramètres:**
- `ρ` : Résistivité cuivre = 0.01724 Ω·mm²/m (20°C)
- `I` : Courant (A)
- `L` : Longueur aller (m)
- `ΔV` : Chute tension admissible (V)

**Formule (Loi d'Ohm):**
```
R = ρ × L / S             (résistance câble)
ΔV = R × I = (ρ × L × I) / S
S = (ρ × I × L) / ΔV

Pour aller-retour (factor 2):
S = (2 × ρ × I × L) / ΔV
```

**Dérivation:**
```
V = RI                    (Loi d'Ohm)
R = ρL/S                  (résistance fil)
ΔV = (ρL/S) × I
S = (ρLI) / ΔV
S_total = 2 × (ρLI) / ΔV  (aller + retour)
```

**Exemple numérique:**
```
ρ = 0.01724 Ω·mm²/m
I = 50 A
L = 10 m
ΔV_max = 3% de 12V = 0.36 V

S = (2 × 0.01724 × 50 × 10) / 0.36
S = 17.24 / 0.36
S = 47.9 mm²

Section standard suivante = 50 mm²
```

**Vérification:**
```
R = (2 × 0.01724 × 10) / 50 = 0.00689 Ω
ΔV = 0.00689 × 50 = 0.344 V
% = (0.344 / 12) × 100 = 2.87% ✓ (< 3%)
```

---

## 🌍 Internationalisation

### Structure

```
locals/
├── en.json    # Anglais (défaut)
└── fr.json    # Français
```

### Format

```json
{
  "title": "Solar Solution",
  "New Equipment": {
    "title": "Add Equipment",
    "name": "Name",
    "power": "Power (W)"
  }
}
```

### Usage

```python
# Chargement
t = load_translation("fr")

# Accès
title = t["title"]
power_label = t["New Equipment"]["power"]

# Avec formatting
message = t["success_message"].format(name="Laptop", power=65)
```

### Ajouter une Langue

1. Créer `locals/xx.json` (xx = code langue)
2. Copier structure de `en.json`
3. Traduire toutes les clés
4. Ajouter au selectbox dans `main.py`

---

## 💾 Stockage

### Configurations

**Format:** JSON
**Emplacement:** `saved_configs/*.json`
**Structure:**
```json
{
  "name": "Bureau",
  "timestamp": "2025-10-06T15:30:00",
  "equipments": [...]
}
```

**Opérations:**
- Create: `save_configuration()`
- Read: `load_configuration()`
- Update: Resave avec même nom (écrase)
- Delete: `delete_configuration()`

### Bibliothèque Équipements

**Format:** JSON
**Emplacement:** `equipment_library.json` (racine)
**Chargement:** Cached avec `@st.cache_data`

**Catégories:**
- Kitchen (Cuisine) 🍳
- Laundry (Buanderie) 🧺
- Electronics (Électronique) 💻
- Lighting (Éclairage) 💡
- Heating/Cooling (Chauffage/Climatisation) ❄️
- Water (Eau) 💧
- Personal Care (Soins personnels) 👤
- Workshop (Atelier) 🔧

---

## ⚡ Performance

### Optimisations Appliquées

1. **Caching Streamlit**
   ```python
   @st.cache_data
   def load_equipment_library() -> dict:
       # Chargé une seule fois
   ```

2. **Calculs Lazy**
   - Calculs seulement si données changent
   - Éviter recalculs inutiles

3. **DataFrames Pandas**
   - Vectorisation pour operations sur colonnes
   - Plus rapide que loops Python

### Métriques

**Tests de Performance:**
```
48 tests en 1.28s
Moyenne: ~27ms/test
```

**Couverture:**
```
72% global
99% logique métier
```

### Profiling

```bash
# Profiler l'application
python -m cProfile -o profile.stats main.py

# Analyser
python -m pstats profile.stats
>>> sort cumulative
>>> stats 20
```

---

## 🔐 Sécurité

### Validation des Entrées

```python
# Toujours valider
if name.strip() == "":
    raise ValueError("Name required")
if power <= 0:
    raise ValueError("Power must be positive")
if time <= 0:
    raise ValueError("Time must be positive")
```

### Sanitization

```python
# Éviter injection dans noms de fichiers
safe_name = "".join(c for c in name if c.isalnum() or c in (" ", "_", "-"))
```

### No Secrets in Code

- Pas de clés API hardcodées
- Utiliser variables d'environnement
- `.gitignore` pour fichiers sensibles

---

## 🧪 Tests

### Structure

```
tests/
├── __init__.py
├── test_models.py         # 22 tests
└── test_calculations.py   # 26 tests
```

### Coverage

```
models/equipment.py       99%
utils/calculations.py    100%
Total:                    72%
```

### Exécution

```bash
# Tous les tests
pytest tests/ -v

# Avec couverture
pytest tests/ --cov=models --cov=utils

# Rapport HTML
pytest tests/ --cov-report=html
open htmlcov/index.html
```

---

## 📚 Références

### Normes et Standards

- **IEC 60364** : Installations électriques basse tension
- **NF C 15-100** : Norme française installations électriques
- **PEP 8** : Style guide Python
- **Google Python Style Guide** : Docstrings

### Formules Électriques

- Loi d'Ohm : `V = RI`
- Puissance : `P = VI`
- Énergie : `E = Pt`
- Résistance fil : `R = ρL/S`

### Documentation Externe

- [Streamlit Docs](https://docs.streamlit.io/)
- [Plotly Python](https://plotly.com/python/)
- [Pandas Docs](https://pandas.pydata.org/docs/)
- [Pytest Docs](https://docs.pytest.org/)

---

**Version:** 0.3.0  
**Dernière mise à jour:** Octobre 2025  
**Auteur:** Solar Solution Team

