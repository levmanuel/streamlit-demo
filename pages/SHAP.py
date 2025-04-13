import streamlit as st
import pandas as pd
import shap
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

st.set_page_config(page_title="SHAP & IA - Explicabilité", layout="wide")

st.title("🧠 Explicabilité locale et globale avec SHAP")
st.write("""
Cette application explore les concepts d’**explicabilité globale et locale** à l’aide de **SHAP**.
Nous utilisons un modèle de **Random Forest** sur le dataset *California Housing* pour prédire le prix moyen d’une maison.
""")

st.header("📦 1. Chargement et préparation des données")
@st.cache_data
def load_data():
    data = fetch_california_housing(as_frame=True)
    return data.data, data.target

X, y = load_data()
st.write("Aperçu des données :")
st.dataframe(X.head())

st.header("🧠 2. Modèle utilisé")
st.markdown("""
Nous utilisons un modèle **Random Forest Regressor** de Scikit-learn :
- `n_estimators = 100`
- `random_state = 42`
""")

model = RandomForestRegressor(n_estimators=100, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model.fit(X_train, y_train)
st.success("✅ Modèle entraîné avec succès !")

st.header("📊 3. Performance du modèle")
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

col1, col2 = st.columns(2)
col1.metric("📈 R² score", f"{r2:.3f}")
col2.metric("📉 Erreur absolue moyenne", f"{mae:.3f}")

st.subheader("Comparaison Prédictions vs Réel (échantillon)")
fig_perf, ax_perf = plt.subplots()
ax_perf.scatter(y_test[:100], y_pred[:100], alpha=0.6)
ax_perf.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
ax_perf.set_xlabel("Vrai prix")
ax_perf.set_ylabel("Prix prédit")
ax_perf.set_title("Prédictions vs Valeurs réelles")
st.pyplot(fig_perf)

# ------------------------------------
# Améliorations pour la section d'explicabilité globale
st.header("🌐 4. Explicabilité Globale")
st.write("Analyse de l'influence moyenne des variables à l'aide de SHAP.")

st.markdown("""
#### 📘 Comment lire ce graphique ?

Ce graphique montre l'**importance moyenne** de chaque variable dans les prédictions du modèle, mais d'une manière plus riche que les importances classiques de Random Forest.

- **Chaque barre** représente une variable du modèle
- **Plus la barre est longue**, plus cette variable a d'impact sur les prédictions en moyenne
- L'importance est mesurée par la **valeur absolue moyenne des SHAP values** pour chaque variable
- Contrairement aux mesures d'importance classiques, SHAP:
  - Est cohérent mathématiquement (basé sur la théorie des jeux)
  - Tient compte des interactions entre variables
  - Considère l'impact réel sur chaque prédiction individuelle

**Interprétation pour ce modèle:**
- `MedInc` (revenu médian) est le facteur le plus déterminant pour prédire le prix des logements
- `Latitude`, `AveOccup` (occupation moyenne) et `Longitude` jouent également un rôle important
- Les variables avec des barres plus courtes comme `HouseAge` ont un impact global plus limité
""")

@st.cache_resource
def get_explainer():
    return shap.TreeExplainer(model)

explainer = get_explainer()

# Réduire la taille pour éviter lenteurs
X_sample = X_test.iloc[:min(100, len(X_test))]
shap_values = explainer.shap_values(X_sample)

# Graphique d'importance
st.subheader("🔍 Graphique des importances moyennes (SHAP)")
fig_global, ax_global = plt.subplots(figsize=(10, 6))
shap.summary_plot(shap_values, X_sample, plot_type="bar", show=False)
plt.tight_layout()
st.pyplot(fig_global)

# Ajout d'un graphique de dépendance pour la variable la plus importante
st.subheader("📈 Graphique de dépendance pour le revenu médian")
st.markdown("""
Ce graphique montre comment la variable `MedInc` (revenu médian) influence les prédictions:
- L'axe X représente les valeurs de revenu médian
- L'axe Y représente l'impact SHAP (contribution à la prédiction)
- Chaque point est une observation
- Les couleurs indiquent une autre variable qui interagit potentiellement avec MedInc

On observe une **relation positive non-linéaire**: quand le revenu médian augmente, l'impact sur le prix prédit augmente aussi, mais pas de façon parfaitement linéaire.
""")

fig_depend, ax_depend = plt.subplots(figsize=(10, 6))
shap.dependence_plot("MedInc", shap_values, X_sample, ax=ax_depend, show=False)
plt.tight_layout()
st.pyplot(fig_depend)

# Améliorations pour la section d'explicabilité locale
st.header("🔎 5. Explicabilité Locale")
index = st.slider("Sélectionnez une observation à expliquer :", 0, len(X_sample) - 1, 0)
individual = X_sample.iloc[[index]]

pred_value = model.predict(individual)[0]
base_value = explainer.expected_value

st.write("Observation sélectionnée :")
st.write(individual)
# Afficher la prédiction de façon plus sûre
st.write(f"**Prix prédit:** {pred_value:.3f}")
st.write(f"**Valeur de base (moyenne du modèle):** {float(base_value):.3f}")
st.write(f"**Différence:** {pred_value - float(base_value):.3f}")

st.markdown("""
#### 📘 Comment lire ce graphique ?

Le waterfall plot explique la **prédiction pour une observation individuelle** en détaillant la contribution de chaque variable.

- **La base value (valeur de base)** est la moyenne des prédictions sur tout le dataset - c'est ce que prédirait le modèle sans aucune information sur cette observation spécifique
- **Chaque ligne** montre comment une variable particulière pousse la prédiction:
  - **En rouge**: la variable augmente la prédiction par rapport à la moyenne
  - **En bleu**: la variable diminue la prédiction par rapport à la moyenne
- **La taille** de chaque barre correspond à l'ampleur de l'impact
- **`f(x)`** est la prédiction finale pour cette observation, résultat de toutes ces contributions combinées

**Comment utiliser cette explication:**
- Pour les professionnels immobiliers: comprendre les facteurs qui valorisent ou dévalorisent un bien spécifique
- Pour les data scientists: détecter des anomalies ou biais potentiels dans le modèle
- Pour les décideurs: expliquer de manière transparente pourquoi une prédiction particulière a été faite
""")

st.subheader("📈 Waterfall plot de la prédiction")
fig_local, ax_local = plt.subplots(figsize=(10, 8))
shap.plots.waterfall(shap.Explanation(
    values=shap_values[index],
    base_values=explainer.expected_value,
    data=individual.values[0],
    feature_names=individual.columns.tolist()), show=False)
plt.tight_layout()
st.pyplot(fig_local)

# Nouvelle section: comparaison explicabilité globale vs locale
st.header("🔄 6. Comparaison Explicabilité Globale vs Locale")
st.markdown("""
### Quelle approche choisir?

**Explicabilité Globale** | **Explicabilité Locale**
--------------------------|-------------------------
Vue d'ensemble du modèle | Analyse d'une prédiction spécifique
Montre les tendances générales | Explique un cas particulier
Utile pour comprendre le modèle | Utile pour justifier une décision
Ne capture pas les comportements complexes | Ne révèle pas nécessairement les tendances générales

### Cas d'usage:

- **Développement de modèle**: utilisez l'explicabilité globale pour valider que votre modèle se base sur des variables pertinentes
- **Audit et conformité**: utilisez l'explicabilité locale pour justifier des décisions individuelles
- **Communication**: combinaison des deux approches pour une compréhension complète

### En pratique:
- Commencez par l'explicabilité globale pour comprendre le comportement général du modèle
- Utilisez l'explicabilité locale pour investiguer des cas particuliers ou des anomalies
- Présentez toujours les limites de ces interprétations (corrélation ≠ causalité)
""")

# Nouvelle section: visualisation avancée des interactions
st.header("🧩 7. Visualisation avancée des interactions")
st.markdown("""
### Visualisation des interactions complexes

La visualisation de type "SHAP Summary Plot" ci-dessous montre la distribution des valeurs SHAP pour chaque variable:
- Chaque point représente une observation (une maison)
- La position sur l'axe horizontal indique la valeur SHAP (impact sur la prédiction)
- Les couleurs indiquent si la valeur de la variable est élevée (rouge) ou basse (bleu)
- On peut ainsi repérer des motifs et des interactions entre variables

**Comment l'interpréter:**
- Un gradient de couleur (bleu à rouge) qui va de gauche à droite indique une relation positive
- Un gradient inversé (rouge à gauche, bleu à droite) indique une relation négative
- Des motifs non-linéaires suggèrent des interactions complexes ou des effets de seuil
""")

st.subheader("Summary Plot des impacts variables")
fig_summary, ax_summary = plt.subplots(figsize=(10, 8))
shap.summary_plot(shap_values, X_sample, show=False)
plt.tight_layout()
st.pyplot(fig_summary)

# Ajout d'une visualisation pour une observation unique
st.subheader("Force Plot pour l'observation sélectionnée")
st.markdown("""
Ce graphique montre comment chaque variable contribue à la prédiction pour l'observation sélectionnée:
- Les variables rouges poussent la prédiction vers le haut
- Les variables bleues poussent la prédiction vers le bas
- La largeur de chaque segment correspond à l'ampleur de l'impact
""")
fig_force_single, ax_force_single = plt.subplots(figsize=(10, 3))
shap.force_plot(explainer.expected_value, shap_values[index], individual.values[0], 
               feature_names=individual.columns.tolist(), matplotlib=True, show=False)
plt.tight_layout()
st.pyplot(fig_force_single)