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

# ------------------------------------
st.header("📦 1. Chargement et préparation des données")
@st.cache_data
def load_data():
    data = fetch_california_housing(as_frame=True)
    return data.data, data.target

X, y = load_data()
st.write("Aperçu des données :")
st.dataframe(X.head())

# ------------------------------------
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

# ------------------------------------
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
st.header("🌐 4. Explicabilité Globale")
st.write("Analyse de l'influence moyenne des variables à l'aide de SHAP.")

st.markdown("""
#### 📘 Comment lire ce graphique ?

Ce graphique montre l'**importance moyenne** de chaque variable dans les prédictions du modèle.

- **Chaque barre bleue** représente une variable.
- **Plus la barre est longue**, plus la variable influence fortement les prédictions.
- L'importance est mesurée par la **valeur absolue moyenne des SHAP values** pour chaque variable.

Par exemple :
- `MedInc` (revenu médian) a l’impact moyen le plus fort sur le prix prédictif.
- `Latitude`, `AveOccup` (occupation moyenne) et `Longitude` suivent.

> Ce graphique donne une **vue globale** du fonctionnement du modèle : quelles variables il utilise le plus en moyenne.
""")

@st.cache_resource
def get_explainer():
    return shap.TreeExplainer(model)

explainer = get_explainer()

# Réduire la taille pour éviter lenteurs
X_sample = X_test.iloc[:min(100, len(X_test))]
shap_values = explainer.shap_values(X_sample)

st.subheader("🔍 Graphique des importances moyennes (SHAP)")
fig_global, ax_global = plt.subplots()
shap.summary_plot(shap_values, X_sample, plot_type="bar", show=False)
st.pyplot(fig_global)

# ------------------------------------
st.header("🔎 5. Explicabilité Locale")
index = st.slider("Sélectionnez une observation à expliquer :", 0, len(X_sample) - 1, 0)
individual = X_sample.iloc[[index]]

st.write("Observation sélectionnée :")
st.write(individual)

st.subheader("📈 Waterfall plot de la prédiction")
fig_local, ax_local = plt.subplots()
shap.plots.waterfall(shap.Explanation(
    values=shap_values[index],
    base_values=explainer.expected_value,
    data=individual.values[0],
    feature_names=individual.columns.tolist()), show=False)
st.pyplot(fig_local)