import streamlit as st
import pandas as pd
import shap
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

st.set_page_config(page_title="Explicabilité IA avec SHAP", layout="wide")

st.title("🧠 Explicabilité des modèles d'IA avec SHAP")
st.write("""
Bienvenue ! Cette application a pour objectif de vous expliquer les notions **d'explicabilité globale** et **locale**
des modèles d'intelligence artificielle, à l'aide de **SHAP (SHapley Additive exPlanations)**.
""")

st.header("📦 1. Chargement des données")
@st.cache_data
def load_data():
    data = fetch_california_housing(as_frame=True)
    X = data.data
    y = data.target
    return X, y

X, y = load_data()
st.write("Voici un aperçu des données :")
st.dataframe(X.head())

st.header("🤖 2. Entraînement du modèle")
model = RandomForestRegressor(n_estimators=100, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model.fit(X_train, y_train)
st.success("Modèle Random Forest entraîné !")

st.header("🌐 3. Explicabilité Globale")
st.write("""
L'explicabilité **globale** nous aide à comprendre **quelles caractéristiques influencent le plus le modèle** en général.
""")

explainer = shap.Explainer(model, X_train)
shap_values = explainer(X_test)

st.subheader("📊 Importance moyenne des variables (globales)")
fig1, ax1 = plt.subplots()
shap.plots.bar(shap_values, max_display=10, show=False)
st.pyplot(fig1)

st.markdown("""
✅ **Interprétation** : plus une variable a une valeur SHAP moyenne élevée (en valeur absolue), plus elle contribue aux prédictions du modèle.
""")

st.header("🔎 4. Explicabilité Locale")
st.write("""
L'explicabilité **locale** s'intéresse à **une prédiction particulière** : pourquoi le modèle a-t-il prédit cette valeur pour cet individu ?
""")

index = st.slider("Choisissez l'observation à expliquer (entre 0 et 100)", 0, 100, 0)
individual_data = X_test.iloc[[index]]

st.write("🔍 Caractéristiques de l'observation sélectionnée :")
st.write(individual_data)

st.subheader("📈 Valeurs SHAP pour cette observation")
fig2, ax2 = plt.subplots()
shap.plots.waterfall(shap_values[index], show=False)
st.pyplot(fig2)

st.markdown("""
✅ **Interprétation** : le graphique en cascade montre comment chaque caractéristique influence la prédiction finale par rapport à la moyenne.
""")

st.info("""
💡 **Rappel** :
- Les **valeurs SHAP positives** poussent la prédiction **vers le haut**.
- Les **valeurs SHAP négatives** la poussent **vers le bas**.
""")

st.markdown("---")
st.caption("App créée avec ❤️ par ChatGPT - SHAP + Streamlit Demo")