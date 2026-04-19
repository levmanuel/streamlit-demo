import streamlit as st
import matplotlib.pyplot as plt
import shap
from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

st.set_page_config(page_title="SHAP & IA - Explicabilité", layout="wide")

st.title("🧠 Explicabilité locale et globale avec SHAP")
st.write("""
Cette application explore les concepts d'**explicabilité globale et locale** à l'aide de **SHAP**.
Nous utilisons un modèle de **Random Forest** sur le dataset *California Housing* pour prédire le prix moyen d'une maison.
""")


@st.cache_data
def load_data():
    data = fetch_california_housing(as_frame=True)
    return data.data, data.target


@st.cache_resource
def train_model(test_size=0.2, random_state=42):
    X, y = load_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    model = RandomForestRegressor(n_estimators=100, random_state=random_state)
    model.fit(X_train, y_train)
    explainer = shap.TreeExplainer(model)
    return model, explainer, X_train, X_test, y_train, y_test


@st.cache_data
def compute_shap_values(sample_size=100):
    _, explainer, _, X_test, _, _ = train_model()
    X_sample = X_test.iloc[:sample_size]
    shap_values = explainer.shap_values(X_sample)
    return shap_values, X_sample


# --- 1. Données ---
st.header("📦 1. Chargement et préparation des données")
X, y = load_data()
st.write("Aperçu des données :")
st.dataframe(X.head())

# --- 2. Modèle ---
st.header("🧠 2. Modèle utilisé")
st.markdown("""
Nous utilisons un modèle **Random Forest Regressor** de Scikit-learn pour prédire le prix des maisons.
- **Random Forest**: un ensemble d'arbres de décision qui améliore la précision et réduit le sur-apprentissage
- **Hyperparamètres**: nous utilisons 100 arbres (`n_estimators=100`) et un état aléatoire fixe pour la reproductibilité
""")

model, explainer, X_train, X_test, y_train, y_test = train_model()
st.success("✅ Modèle entraîné avec succès !")

# --- 3. Performance ---
st.header("📊 3. Performance du modèle")
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

col1, col2, col3 = st.columns(3)
col1.metric("📈 R² score", f"{r2:.3f}")
col2.metric("📉 Erreur absolue moyenne", f"{mae:.3f}")
col3.metric("📊 Moy. des prédictions du modèle", f"{y_pred.mean():.3f}")

st.subheader("Comparaison Prédictions vs Réel (échantillon)")
fig_perf, ax_perf = plt.subplots()
ax_perf.scatter(y_test[:100], y_pred[:100], alpha=0.6)
ax_perf.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], "r--")
ax_perf.set_xlabel("Vrai prix")
ax_perf.set_ylabel("Prix prédit")
ax_perf.set_title("Prédictions vs Valeurs réelles")
st.pyplot(fig_perf)
plt.close(fig_perf)

# --- 4. Explicabilité globale ---
st.header("🌐 4. Explicabilité Globale")
st.write("Analyse de l'influence moyenne des variables à l'aide de SHAP.")

with st.expander("ℹ️ Comment lire ce graphique ?", expanded=False):
    st.markdown("""
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

shap_values, X_sample = compute_shap_values()

st.subheader("🔍 Graphique des importances moyennes (SHAP)")
shap.summary_plot(shap_values, X_sample, plot_type="bar", show=False)
plt.tight_layout()
fig_global = plt.gcf()
st.pyplot(fig_global)
plt.close(fig_global)

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
plt.close(fig_depend)

# --- 5. Explicabilité locale ---
st.header("🔎 5. Explicabilité Locale")
index = st.slider("Sélectionnez une observation à expliquer :", 0, len(X_sample) - 1, 0)
individual = X_sample.iloc[[index]]

pred_value = model.predict(individual)[0]
base_value = explainer.expected_value

st.write("Observation sélectionnée :")
st.write(individual)
st.write(f"**Prix prédit:** {pred_value:.3f}")
st.write(f"**Valeur de base (moyenne du modèle):** {float(base_value):.3f}")
st.write(f"**Différence:** {pred_value - float(base_value):.3f}")

with st.expander("ℹ️ Comment lire ce graphique ?", expanded=False):
    st.markdown("""
    #### 📘 Comment lire ce graphique ?

    Le waterfall plot explique la **prédiction pour une observation individuelle** en détaillant la contribution de chaque variable.

    - **La base value (valeur de base)** est la moyenne des prédictions sur tout le dataset - c'est ce que prédirait le modèle sans aucune information sur cette observation spécifique
    - **Chaque ligne** montre comment une variable particulière pousse la prédiction:
      - **En rouge**: la variable augmente la prédiction par rapport à la moyenne
      - **En bleu**: la variable diminue la prédiction par rapport à la moyenne
    - **La taille** de chaque barre correspond à l'ampleur de l'impact
    - **`f(x)`** est la prédiction finale pour cette observation, résultat de toutes ces contributions combinées
    """)

st.subheader("📈 Waterfall plot de la prédiction")
shap.plots.waterfall(shap.Explanation(
    values=shap_values[index],
    base_values=explainer.expected_value,
    data=individual.values[0],
    feature_names=individual.columns.tolist(),
), show=False)
plt.tight_layout()
fig_waterfall = plt.gcf()
st.pyplot(fig_waterfall)
plt.close(fig_waterfall)

# --- 6. Comparaison globale vs locale ---
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
""")

# --- 7. Summary plot ---
st.header("🧩 7. Visualisation avancée des interactions")
st.markdown("""
### Visualisation des interactions complexes

La visualisation de type "SHAP Summary Plot" ci-dessous montre la distribution des valeurs SHAP pour chaque variable:
- Chaque point représente une observation (une maison)
- La position sur l'axe horizontal indique la valeur SHAP (impact sur la prédiction)
- Les couleurs indiquent si la valeur de la variable est élevée (rouge) ou basse (bleu)
- On peut ainsi repérer des motifs et des interactions entre variables
""")

st.subheader("Summary Plot des impacts variables")
shap.summary_plot(shap_values, X_sample, show=False)
plt.tight_layout()
fig_summary = plt.gcf()
st.pyplot(fig_summary)
plt.close(fig_summary)
