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
st.metric("Prix prédit", f"{pred_value:.3f}", f"{pred_value - base_value:.3f} par rapport à la moyenne")

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

# Nouvelle section: force plot pour visualiser les interactions entre variables
st.header("🧩 7. Interactions entre variables (Force Plot)")
st.markdown("""
### Visualisation des interactions complexes

Le force plot ci-dessous montre comment toutes les variables interagissent pour produire chaque prédiction:
- Chaque point représente une observation (une maison)
- La position sur l'axe horizontal indique la valeur SHAP (impact sur la prédiction)
- Les couleurs indiquent si la valeur de la variable est élevée (rouge) ou basse (bleu)
- On peut ainsi repérer des motifs récurrents et des interactions entre variables

**Comment l'interpréter:**
Cherchez des motifs de couleur qui se répètent. Par exemple, si des points avec revenu élevé (rouge) et âge faible (bleu) sont systématiquement à droite, cela suggère une interaction entre ces variables.
""")

st.subheader("Force Plot pour les 50 premières observations")
fig_force, ax_force = plt.subplots(figsize=(10, 3))
shap_values_subset = shap_values[:50]
X_sample_subset = X_sample.iloc[:50]
shap.force_plot(explainer.expected_value, shap_values_subset, X_sample_subset, matplotlib=True, show=False, plot_cmap=['#FF4B4B', '#4B4BFF'])
plt.tight_layout()
st.pyplot(fig_force)