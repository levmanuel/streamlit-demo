"""Catalogue des démos : source unique pour la page d'accueil (et son test).

Chaque entrée : (titre affiché, fichier dans pages/, description).
"""

DEMOS = [
    {
        "category": "Machine Learning & IA",
        "icon": "🤖",
        "items": [
            ("SHAP", "SHAP.py", "Explicabilité ML globale & locale sur California Housing"),
            ("Prophet", "Prophet.py", "Prévision de séries temporelles (températures Yosemite)"),
            ("MLflow Classifier", "MLflow_Classifier.py", "Classification + tuning d'hyperparamètres + MLflow tracking"),
            ("Leaf Detect", "Leaf_Detect.py", "Classification d'espèces de plantes via TensorFlow"),
            ("Reco", "Reco.py", "Évaluation de recommandations d'audit par LLM (Mistral)"),
        ],
    },
    {
        "category": "NLP & Recherche",
        "icon": "📝",
        "items": [
            ("BM25 vs TFIDF vs CV", "BM25_vs_TFIDF_vs_CV.py", "Comparaison interactive de méthodes de vectorisation"),
            ("Gale-Shapley", "Gale_Shapley.py", "Algorithme de matching stable équipes / joueurs"),
        ],
    },
    {
        "category": "Vision par ordinateur",
        "icon": "👁️",
        "items": [
            ("Checkbox DBSCAN", "Checkbox_DBSCAN.py", "Détection de cases à cocher par contours + template matching"),
        ],
    },
    {
        "category": "Finance & Audit",
        "icon": "💼",
        "items": [
            ("Simulation LCR", "Simulation_LCR.py", "Simulation du Liquidity Coverage Ratio (Bâle III)"),
            ("ISIN check", "ISIN_check.py", "Validateur de codes ISIN (algorithme de Luhn)"),
            ("GSheet", "GSheet.py", "Cours TSLA sur 90 jours depuis Google Sheets"),
        ],
    },
    {
        "category": "Outils & APIs",
        "icon": "🛠️",
        "items": [
            ("API Météo", "API_Meteo.py", "Exploration de l'API Open-Meteo : météo, prévisions, historique"),
            ("The Game", "The_Game.py", "Jeu de cartes The Game — mode joueur & auto-play IA"),
            ("Cocktail", "Cocktail.py", "Suggestions de cocktails — st.connection SQLite (ajout/suppression persistant)"),
            ("TDEE", "TDEE.py", "Calculateur de dépense énergétique : BMR, TDEE, objectif calorique et macros"),
        ],
    },
    {
        "category": "LLM & RAG",
        "icon": "💬",
        "items": [
            ("Chat RAG", "Chat_RAG.py", "Assistant conversationnel sur le portfolio — RAG (Mistral Embeddings + streaming)"),
        ],
    },
]

# Pages volontairement absentes de l'accueil.
PAGES_HORS_CATALOGUE = {"API_Test_Mistral.py"}
