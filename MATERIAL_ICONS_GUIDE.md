# Guide : Utilisation des Icônes Material dans Streamlit

## ⚠️ Règle Importante

**Les icônes Material Design de Streamlit NE FONCTIONNENT PAS dans du HTML brut.**

---

## ✅ Syntaxe Correcte

### 1. Dans les composants Streamlit natifs

```python
# ✅ CORRECT - Fonctionne parfaitement
st.title(":material/home: Welcome")
st.header(":material/settings: Configuration")
st.subheader(":material/info: Information")
st.markdown("### :material/bolt: Equipment")
st.button(":material/save: Save", width="stretch")
st.metric(":material/attach_money: Cost", "5000 €")
```

### 2. Dans le texte Markdown simple

```python
# ✅ CORRECT
st.markdown(":material/check_circle: Task completed")
st.write(":material/warning: Warning message")
```

---

## ❌ Syntaxe Incorrecte

### 1. Dans du HTML avec `unsafe_allow_html=True`

```python
# ❌ INCORRECT - L'icône ne s'affichera PAS
st.markdown("""
<h1>:material/home: Title</h1>
<div>:material/info: Information</div>
""", unsafe_allow_html=True)
```

**Pourquoi ?** Streamlit ne peut pas interpréter la syntaxe `:material/icon:` dans du HTML brut.

---

## 🔧 Solutions

### Solution 1 : Séparer l'icône du HTML

**Avant (incorrect)** :
```python
st.markdown("""
<div class="card">
    <h3>:material/bolt: Equipment Management</h3>
    <p>Add and manage equipment...</p>
</div>
""", unsafe_allow_html=True)
```

**Après (correct)** :
```python
st.markdown("### :material/bolt: Equipment Management")
st.markdown("""
<div class="card">
    <p>Add and manage equipment...</p>
</div>
""", unsafe_allow_html=True)
```

### Solution 2 : Utiliser des émojis Unicode dans le HTML

**Avant (incorrect)** :
```python
st.markdown("""
<h1>:material/wb_sunny: Solar Report</h1>
""", unsafe_allow_html=True)
```

**Après (correct)** :
```python
st.markdown("""
<h1>☀️ Solar Report</h1>
""", unsafe_allow_html=True)
```

### Solution 3 : Icône avant le HTML

**Avant (incorrect)** :
```python
st.markdown("""
<div class="report-header">
    <h1>:material/description: Report</h1>
</div>
""", unsafe_allow_html=True)
```

**Après (correct)** :
```python
st.markdown(":material/description:")  # Icône Material
st.markdown("""
<div class="report-header">
    <h1>📄 Report</h1>  <!-- Emoji Unicode pour l'impression -->
</div>
""", unsafe_allow_html=True)
```

---

## 📋 Tableau de Conversion : Material Icons → Unicode

Pour les cas où vous devez utiliser du HTML (impression, mise en page complexe) :

| Material Icon | Syntaxe Streamlit | Unicode | Nom |
|---------------|-------------------|---------|-----|
| `:material/home:` | `st.title(":material/home:")` | 🏠 | Maison |
| `:material/wb_sunny:` | `st.title(":material/wb_sunny:")` | ☀️ | Soleil |
| `:material/bolt:` | `st.title(":material/bolt:")` | ⚡ | Éclair |
| `:material/battery_charging_full:` | `st.title(":material/battery_charging_full:")` | 🔋 | Batterie |
| `:material/description:` | `st.title(":material/description:")` | 📄 | Document |
| `:material/settings:` | `st.title(":material/settings:")` | ⚙️ | Paramètres |
| `:material/save:` | `st.button(":material/save:")` | 💾 | Sauvegarder |
| `:material/delete:` | `st.button(":material/delete:")` | 🗑️ | Supprimer |
| `:material/edit:` | `st.button(":material/edit:")` | ✏️ | Éditer |
| `:material/print:` | `st.button(":material/print:")` | 🖨️ | Imprimer |
| `:material/check_circle:` | `st.success(":material/check_circle:")` | ✅ | Succès |
| `:material/warning:` | `st.warning(":material/warning:")` | ⚠️ | Avertissement |
| `:material/info:` | `st.info(":material/info:")` | ℹ️ | Information |
| `:material/attach_money:` | `st.metric(":material/attach_money:")` | 💰 | Argent |
| `:material/park:` | `st.metric(":material/park:")` | 🌳 | Arbre |

---

## 🎯 Cas d'Usage Pratiques

### Cas 1 : Cartes avec HTML stylisé

```python
# ✅ SOLUTION OPTIMALE
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### :material/bolt: Equipment")  # Icône Material visible
    st.markdown("""
    <div style="background: white; padding: 1rem;">
        <p>⚡ Manage your equipment</p>  <!-- Emoji pour l'impression -->
        <ul>
            <li>Add equipment</li>
            <li>Edit profiles</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
```

### Cas 2 : Rapport imprimable

```python
# ✅ DOUBLE ICÔNE : Material pour l'écran, Unicode pour l'impression
st.markdown(":material/description:")  # Visible à l'écran uniquement

st.markdown(f"""
<div class="report-header">
    <h1>📄 System Report</h1>  <!-- Visible à l'impression -->
    <p>Generated on {datetime.now().strftime('%B %d, %Y')}</p>
</div>
""", unsafe_allow_html=True)
```

### Cas 3 : Navigation

```python
# ✅ PARFAIT - Pas de HTML
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.button(":material/home: Home", width="stretch")
    
with col2:
    st.button(":material/bolt: Equipments", width="stretch")
    
with col3:
    st.button(":material/battery_charging_full: Calculations", width="stretch")
    
with col4:
    st.button(":material/description: Report", width="stretch")
```

---

## 🐛 Débogage

### Problème : L'icône affiche `:material/icon_name:` au lieu de l'icône

**Causes possibles** :
1. ✅ L'icône est dans du HTML (`unsafe_allow_html=True`)
2. ✅ Mauvaise syntaxe (underscore au lieu de slash : `:material_icon:`)
3. ✅ Version de Streamlit trop ancienne (< 1.35.0)

**Solutions** :
1. Sortir l'icône du HTML
2. Vérifier la syntaxe : `:material/icon_name:` (avec `/`)
3. Mettre à jour Streamlit : `uv pip install --upgrade streamlit`

---

## 📚 Ressources

### Documentation officielle
- [Streamlit Material Icons](https://docs.streamlit.io/develop/api-reference/text/st.markdown#material-icons)
- [Google Material Symbols](https://fonts.google.com/icons)

### Recherche d'icônes
1. Aller sur : https://fonts.google.com/icons
2. Rechercher l'icône (ex: "home", "settings", "battery")
3. Copier le nom en snake_case
4. Utiliser : `:material/icon_name:`

### Exemples de noms
- `home` → `:material/home:`
- `settings` → `:material/settings:`
- `battery_charging_full` → `:material/battery_charging_full:`
- `wb_sunny` → `:material/wb_sunny:`
- `attach_money` → `:material/attach_money:`

---

## ✅ Checklist de Validation

Avant de pousser du code avec des icônes Material :

- [ ] Les icônes Material sont **en dehors** des blocs HTML
- [ ] La syntaxe est correcte : `:material/icon:` (avec `/`)
- [ ] Pour le HTML imprimable, utiliser des **émojis Unicode**
- [ ] Tester l'affichage dans le navigateur
- [ ] Tester l'impression (Ctrl+P) si applicable
- [ ] Vérifier que les icônes ne s'affichent pas comme texte brut

---

## 📝 Notes Importantes

### Pour l'équipe de développement

1. **Toujours privilégier** les composants Streamlit natifs
2. **Éviter** `unsafe_allow_html=True` quand possible
3. **Documenter** les cas où HTML est nécessaire (impression, mise en page complexe)
4. **Tester** sur plusieurs navigateurs
5. **Double icône** pour les rapports : Material (écran) + Unicode (impression)

### Pour les reviews de code

❌ **Rejeter** :
```python
st.markdown("<h1>:material/icon: Title</h1>", unsafe_allow_html=True)
```

✅ **Accepter** :
```python
st.markdown("### :material/icon: Title")
# ou
st.markdown(":material/icon:")
st.markdown("<h1>📄 Title</h1>", unsafe_allow_html=True)
```

---

## 🔄 Historique des Modifications

### Version 1.1.0 (6 octobre 2025)
- Migration complète des emojis vers Material icons
- Correction des icônes dans HTML (`app.py`, `3_Report.py`)
- Création de ce guide

### Fichiers modifiés
- `app.py` : Cartes de fonctionnalités (3 corrections)
- `pages/3_Report.py` : Titre du rapport (1 correction)

---

**Maintenu par** : L'équipe Solar Solution  
**Dernière mise à jour** : 6 octobre 2025  
**Version du guide** : 1.0
