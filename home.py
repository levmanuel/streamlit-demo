import streamlit as st

st.set_page_config(
    page_title="Portfolio ML — levmanuel",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 Portfolio Data Science & ML")
st.write("Bienvenue sur mon portfolio interactif. Chaque page explore une technique ou un outil différent.")

st.divider()

DEMOS = [
    {
        "category": "Machine Learning & IA",
        "icon": "🤖",
        "items": [
            ("SHAP", "Explicabilité ML globale & locale sur California Housing"),
            ("Prophet", "Prévision de séries temporelles (températures Yosemite)"),
            ("mlflow simple classifier", "Classification + tuning d'hyperparamètres + MLflow tracking"),
            ("leaf detect", "Classification d'espèces de plantes via TensorFlow"),
            ("reco", "Évaluation de recommandations d'audit par LLM (Mistral)"),
        ],
    },
    {
        "category": "NLP & Recherche",
        "icon": "📝",
        "items": [
            ("BM25 vs TFIDF vs CV", "Comparaison interactive de méthodes de vectorisation"),
            ("Gale-Shapley", "Algorithme de matching stable équipes / joueurs"),
        ],
    },
    {
        "category": "Vision par ordinateur",
        "icon": "👁️",
        "items": [
            ("checkbox dbscan matchtemplate", "Détection de cases à cocher par contours + template matching"),
        ],
    },
    {
        "category": "Finance & Audit",
        "icon": "💼",
        "items": [
            ("Simulation LCR", "Simulation du Liquidity Coverage Ratio (Bâle III)"),
            ("ISIN check", "Validateur de codes ISIN (algorithme de Luhn)"),
            ("gsheet", "Cours TSLA sur 90 jours depuis Google Sheets"),
        ],
    },
    {
        "category": "Outils & APIs",
        "icon": "🛠️",
        "items": [
            ("API METEO", "Exploration de l'API Open-Meteo : météo, prévisions, historique"),
            ("The Game", "Jeu de cartes The Game — mode joueur & auto-play IA"),
            ("Cocktail", "Suggestions de cocktails selon les ingrédients disponibles"),
        ],
    },
]

cols = st.columns(2)
for i, section in enumerate(DEMOS):
    with cols[i % 2]:
        st.subheader(f"{section['icon']} {section['category']}")
        for name, desc in section["items"]:
            st.markdown(f"**{name}** — {desc}")
        st.write("")

st.divider()
st.caption("Source : [github.com/levmanuel/streamlit-demo](https://github.com/levmanuel/streamlit-demo) · Déployé sur [levmanuel-demo.streamlit.app](https://levmanuel-demo.streamlit.app)")
