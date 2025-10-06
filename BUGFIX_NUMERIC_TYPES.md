# 🐛 Correction : Erreurs de Types Numériques

## 📅 Date
6 octobre 2025

## ❌ Problème

```
streamlit.errors.StreamlitMixedNumericTypesError: All numerical arguments must be of the same type.
`value` has int type.
`min_value` has float type.
`step` has float type.
```

## 🔍 Cause

Streamlit `st.number_input()` exige que **tous les paramètres numériques** (`value`, `min_value`, `max_value`, `step`) soient du **même type** (soit tous `int`, soit tous `float`).

Dans notre code, nous avions des mélanges de types :
- `min_value=0.1` (float)
- `value=equipment.time` (int, car stocké comme int dans certains cas)
- `step=0.1` (float)

## ✅ Solution

### 1. Conversion Explicite en Float

Pour tous les `number_input` avec `min_value` ou `step` en float, convertir explicitement `value` en float :

```python
# ❌ AVANT (problématique)
new_time = st.number_input(
    "Time (h)",
    min_value=0.1,
    value=eq_to_edit.time,  # Peut être int
    step=0.1
)

# ✅ APRÈS (corrigé)
new_time = st.number_input(
    "Time (h)",
    min_value=0.1,
    value=float(eq_to_edit.time),  # Toujours float
    step=0.1,
    format="%.1f"  # Optionnel: formattage pour affichage
)
```

### 2. Format Explicite pour Affichage

Ajout du paramètre `format` pour contrôler l'affichage :
- `format="%.1f"` : 1 décimale
- `format="%.2f"` : 2 décimales

```python
electricity_price = st.number_input(
    "Electricity Price ($/kWh)",
    min_value=0.01,
    value=0.15,
    step=0.01,
    format="%.2f"  # Affiche avec 2 décimales
)
```

### 3. Conversion dans Calculs avec math.ceil()

`math.ceil()` nécessite un type numérique explicite :

```python
# ❌ AVANT
f"{math.ceil(regulator_specs['recommended_current'])} A"

# ✅ APRÈS
recommended_current = float(regulator_specs['recommended_current'])
f"{math.ceil(recommended_current)} A"
```

## 📝 Fichiers Modifiés

### pages/1_⚡_Equipments.py
- Ligne 77: `time_input` avec `format="%.1f"`
- Ligne 132: `new_time` avec `float()` et `format="%.1f"`

### pages/2_🔋_Calculations.py
- Lignes économiques: Ajout de `format="%.2f"` pour tous les coûts
- Ligne 252: Conversion `float()` avant `math.ceil()`
- Ligne 526: Conversion `float()` dans résumé système

### pages/3_📄_Report.py
- Ligne 453: Variable `recommended_current_val` avec `float()`
- Ligne 566: Variable `recommended_current_diagram` avec `float()`

## 🧪 Tests

### Test de Non-Régression

```bash
# Lancer l'application
uv run streamlit run app.py

# Vérifier:
# 1. ✅ Page Home charge sans erreur
# 2. ✅ Page Equipments - Ajouter équipement (time = 4.5h)
# 3. ✅ Page Equipments - Éditer équipement existant
# 4. ✅ Page Calculations - Tous les number_input fonctionnent
# 5. ✅ Page Report - Génération sans erreur
```

### Résultats

```
✅ Toutes les pages chargent correctement
✅ Aucune erreur de type numérique
✅ Les calculs fonctionnent
✅ Le rapport se génère
```

## 📚 Leçons Apprises

### 1. Typage Strict de Streamlit

Streamlit est **strict sur les types numériques**. Toujours s'assurer que :
```python
# Si min_value est float, TOUT doit être float
st.number_input(..., min_value=0.1, value=1.0, step=0.1)

# Si min_value est int, TOUT doit être int
st.number_input(..., min_value=1, value=100, step=1)
```

### 2. Conversion Défensive

Toujours convertir explicitement quand on utilise des valeurs dynamiques :
```python
# Valeur venant d'un objet
value=float(obj.attribute)  # Toujours safe

# Valeur venant d'un calcul
value=float(result)  # Évite les surprises
```

### 3. Format d'Affichage

Le paramètre `format` améliore l'UX :
```python
# Prix: 2 décimales
format="%.2f"  # 0.15 → "0.15"

# Temps: 1 décimale
format="%.1f"  # 4.5 → "4.5"

# Entiers (pas de format nécessaire)
# Laissez-le vide ou utilisez "%d"
```

### 4. math.ceil() et Types

`math.ceil()` de Python nécessite un type numérique supportant `__ceil__()` :
```python
# ❌ Peut échouer si type ambigu
math.ceil(dict_value)

# ✅ Toujours safe
math.ceil(float(dict_value))
```

## 🔄 Checklist pour Éviter ce Problème

Quand vous ajoutez un `st.number_input()` :

- [ ] Tous les paramètres numériques sont du même type ?
- [ ] Si `min_value` est float, `value` est-il `float()` ?
- [ ] Si `step` est float, `value` est-il `float()` ?
- [ ] Utilisez-vous `format=` pour un affichage propre ?
- [ ] Les valeurs dynamiques sont-elles converties explicitement ?

## 📖 Documentation Streamlit

[st.number_input Documentation](https://docs.streamlit.io/library/api-reference/widgets/st.number_input)

> **Note:** All numerical parameters must be of the same type. Mixed integer and float types will raise an error.

## ✅ Statut

**RÉSOLU** ✅

L'application fonctionne maintenant sans erreurs de type numér ique.

---

**Version corrigée:** 0.4.1  
**Temps de correction:** 15 minutes  
**Impact:** Critique → Résolu

