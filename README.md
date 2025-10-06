# Solar Solution ☀️

Une application web **multi-pages** interactive pour dimensionner des installations solaires photovoltaïques avec système de stockage par batteries.

## 📋 Description

Solar Solution est un outil de calcul professionnel qui permet de dimensionner automatiquement les composants d'une installation solaire autonome en fonction de vos besoins énergétiques. L'application calcule :

- La consommation énergétique journalière et horaire de vos équipements
- La capacité de batteries nécessaire avec autonomie configurable
- Le nombre de batteries et panneaux solaires requis
- Les spécifications du régulateur de charge (MPPT/PWM)
- Les sections de câbles avec calcul de chute de tension
- L'analyse économique (ROI, économies, impact CO₂)
- **Rapport imprimable complet** pour vos projets

## 🎯 Architecture Multi-Pages

L'application est structurée en **4 pages principales** avec navigation en haut :

1. **🏠 Home** - Vue d'ensemble et présentation
2. **⚡ Equipments** - Gestion des équipements électriques
3. **🔋 Calculations** - Dimensionnement du système
4. **📄 Report** - Rapport imprimable professionnel

## ✨ Fonctionnalités

### Page 1: Gestion des Équipements ⚡
- ➕ Ajout d'équipements avec puissance (W) et temps d'utilisation (h)
- ⏰ Configuration des horaires d'utilisation (profil horaire sur 24h)
- � **Bibliothèque d'équipements pré-configurés** avec 8 catégories
- �📊 Visualisation en tableau + 3 types de graphiques interactifs
- ✏️ Édition et suppression d'équipements
- 💾 Sauvegarde/chargement de configurations
- � Métriques en temps réel (puissance totale, énergie journalière)

### Page 2: Calculs du Système 🔋
- 🔋 **Batteries** : Support Plomb-Acide/Lithium, tensions 12/24/48V, autonomie 1-7 jours
- ☀️ **Panneaux Solaires** : Calcul basé sur l'ensoleillement local
- ⚙️ **Régulateur de charge** : MPPT (98% efficace) ou PWM (85%)
- 🔌 **Câblage** : Calcul des sections avec chute de tension (norme IEC)
- � **Analyse économique** : Coûts, ROI, économies mensuelles/annuelles
- 🌳 **Impact environnemental** : CO₂ évité, équivalent arbres

### Page 3: Rapport Imprimable 📄
- 📋 Informations projet (nom, client, localisation)
- � Résumé exécutif avec métriques clés
- 📈 Graphiques de consommation
- 🔧 Spécifications détaillées de tous les composants
- ✅ Recommandations d'installation
- 🔧 Diagramme de connexion du système
- 🖨️ **Format optimisé pour impression/PDF**

### Fonctionnalités Transversales
- 🌍 **Multilingue** : Anglais et Français (extensible)
- � **Persistance** : Sauvegarde des configurations
- 📊 **Visualisations** : Graphiques interactifs Plotly
- 🎨 **UI moderne** : Design responsive avec navigation intuitive

## 🚀 Installation

### Prérequis
- Python 3.13 ou supérieur
- [uv](https://github.com/astral-sh/uv) (gestionnaire de packages recommandé)

### Installation avec uv (Recommandé)

```bash
# Cloner le repository
git clone https://github.com/jeshurun01/solar-solution.git
cd solar-solution

# Installer les dépendances
uv sync

# Lancer l'application
uv run streamlit run app.py
```

### Installation avec pip

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run app.py
```

## 💻 Utilisation

### Navigation Multi-Pages

L'application utilise une **navigation en haut de page** avec 4 boutons :

```
┌─────────┬─────────────┬──────────────┬──────────┐
│  🏠 Home │ ⚡ Equipment │ 🔋 Calculs   │ 📄 Report │
└─────────┴─────────────┴──────────────┴──────────┘
```

### Workflow Recommandé

1. **⚡ Page Equipments**
   - Ajoutez vos équipements manuellement ou depuis la bibliothèque
   - Configurez les horaires d'utilisation
   - Visualisez les graphiques de consommation
   - Sauvegardez votre configuration

2. **🔋 Page Calculations**
   - Configurez le type de batteries (Plomb/Lithium)
   - Choisissez la tension (12V/24V/48V) et l'autonomie
   - Configurez les panneaux solaires (puissance, ensoleillement)
   - Sélectionnez le type de régulateur (MPPT/PWM)
   - Calculez les sections de câbles
   - (Optionnel) Consultez l'analyse économique

3. **📄 Page Report**
   - Consultez le rapport complet
   - Ajoutez les informations du projet (nom, client, localisation)
   - Imprimez ou exportez en PDF (Ctrl+P / Cmd+P)

### Impression du Rapport

Pour imprimer ou sauvegarder le rapport :

1. Allez sur la page **📄 Report**
2. Utilisez le raccourci clavier :
   - **Windows/Linux** : `Ctrl + P`
   - **Mac** : `Cmd + P`
3. Choisissez "Imprimer" ou "Enregistrer au format PDF"

> 💡 Le CSS est optimisé pour l'impression : les éléments UI Streamlit sont masqués automatiquement.
## 📁 Structure du Projet

```
solar-solution/
├── app.py                      # 🏠 Page principale (Home)
├── pages/                      # 📂 Pages de l'application
│   ├── 1_⚡_Equipments.py     # Page gestion équipements
│   ├── 2_🔋_Calculations.py   # Page calculs système
│   └── 3_📄_Report.py         # Page rapport imprimable
├── models/                     # 📦 Modèles métier
│   └── equipment.py           # Equipment, EquipmentFactory
├── utils/                      # 🔧 Utilitaires
│   ├── calculations.py        # Fonctions de calcul
│   ├── charts.py              # Graphiques Plotly
│   ├── storage.py             # Sauvegarde/chargement
│   └── translations.py        # Gestion i18n
├── locals/                     # 🌍 Traductions
│   ├── en.json
│   └── fr.json
├── tests/                      # 🧪 Tests unitaires
│   ├── test_models.py
│   └── test_calculations.py
├── equipment_library.json      # 📚 Bibliothèque d'équipements
├── saved_configs/              # 💾 Configurations sauvegardées
├── README.md                   # 📖 Ce fichier
├── CONTRIBUTING.md             # 🤝 Guide de contribution
├── TECHNICAL.md                # 🔧 Documentation technique
└── pyproject.toml              # ⚙️ Configuration projet
```

## 📐 Formules de Calcul

### 1. Batteries
```
Nombre = ⌈(Énergie × Autonomie) / (Tension × Capacité × DoD)⌉

Où:
  - Énergie: Consommation journalière (Wh)
  - Autonomie: Jours d'autonomie souhaités
  - Tension: 12V, 24V ou 48V
  - Capacité: Capacité batterie (Ah)
  - DoD: Profondeur de décharge (0.5 pour Plomb, 0.8 pour Lithium)
```

### 2. Panneaux Solaires
```
Nombre = ⌈Énergie / (Puissance × Heures ensoleillement)⌉

Où:
  - Énergie: Consommation journalière (Wh)
  - Puissance: Puissance d'un panneau (W)
  - Heures: Heures d'ensoleillement de pointe par jour
```

### 3. Régulateur de Charge
```
Courant = (Puissance PV totale / Tension batteries) × 1.25

Le facteur 1.25 est une marge de sécurité de 25%
```

### 4. Section de Câble
```
Section (mm²) = (2 × ρ × I × L) / ΔV

Où:
  - ρ = 0.01724 Ω·mm²/m (résistivité cuivre à 20°C)
  - I = Courant (A)
  - L = Longueur aller (m)
  - ΔV = Chute tension maximale admissible (V)
  - Facteur 2 pour aller-retour du courant
```

## 🧪 Tests

Le projet inclut une suite de tests complète :

```bash
# Exécuter tous les tests
uv run pytest tests/ -v

# Avec couverture de code
uv run pytest tests/ --cov=models --cov=utils --cov-report=html

# Ouvrir le rapport de couverture
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
```

**Métriques actuelles:**
- 48 tests unitaires
- 72% couverture globale
- 99% couverture logique métier
Autonomie (jours) = (Capacité × Tension × Facteur de décharge) / Énergie journalière
```

## 📁 Structure du Projet

```
solar-solution/
├── main.py              # Application principale Streamlit
├── pyproject.toml       # Configuration du projet et dépendances
├── uv.lock             # Fichier de verrouillage des dépendances
├── README.md           # Documentation
└── locals/             # Fichiers de traduction
    ├── en.json         # Traduction anglaise
    └── fr.json         # Traduction française
```

## 🛠️ Technologies Utilisées

- **[Streamlit](https://streamlit.io/)** - Framework web pour applications de data science
- **[Pandas](https://pandas.pydata.org/)** - Manipulation et analyse de données
- **Python 3.13+** - Langage de programmation
- **[uv](https://github.com/astral-sh/uv)** - Gestionnaire de packages Python moderne

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 TODO / Améliorations Futures

- [ ] Implémenter la fonction d'édition des équipements
- [ ] Ajouter plus de langues (Espagnol, Allemand, etc.)
- [ ] Export des résultats en PDF
- [ ] Graphiques de visualisation de la production/consommation
- [ ] Calcul du coût total de l'installation
- [ ] Mode sombre/clair
- [ ] Sauvegarde et chargement de configurations

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👤 Auteur

**Jeshurun Nasser** - [@jeshurun01](https://github.com/jeshurun01)

## 🙏 Remerciements

- Streamlit pour leur excellent framework
- La communauté open source

---

⭐ N'hésitez pas à star le projet si vous le trouvez utile !