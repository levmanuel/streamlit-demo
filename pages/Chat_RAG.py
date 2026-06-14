import json

import numpy as np
import requests
import streamlit as st

st.set_page_config(
    page_title="Chat RAG — Portfolio",
    page_icon="💬",
    layout="wide",
)

MISTRAL_API_KEY = st.secrets["api"]["MISTRAL_API_KEY"]
MISTRAL_CHAT_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_EMBED_URL = "https://api.mistral.ai/v1/embeddings"
CHAT_MODEL = "mistral-large-latest"
EMBED_MODEL = "mistral-embed"

KNOWLEDGE_BASE = [
    {
        "id": "intro",
        "text": (
            "Ce portfolio Streamlit, développé par levmanuel, est un portfolio interactif "
            "de démos Machine Learning, Data Science et outils métier. "
            "Il est déployé sur levmanuel-demo.streamlit.app. "
            "Il contient 14 pages organisées en 5 catégories : "
            "Machine Learning & IA, NLP & Recherche, Vision par ordinateur, Finance & Audit, Outils & APIs."
        ),
    },
    {
        "id": "shap",
        "text": (
            "Page SHAP (Machine Learning & IA) : Explicabilité ML globale et locale sur le dataset California Housing. "
            "Utilise un Random Forest Regressor de scikit-learn. "
            "Affiche des graphiques SHAP : bar chart (importance globale), waterfall plot (contribution locale), "
            "summary plot, dependence plot. "
            "Démontre @st.cache_data et @st.cache_resource pour la performance. "
            "Bibliothèques : scikit-learn, shap 0.44, matplotlib, seaborn."
        ),
    },
    {
        "id": "prophet",
        "text": (
            "Page Prophet (Machine Learning & IA) : Prévision de séries temporelles sur les températures de Yosemite. "
            "Utilise Facebook Prophet 1.3 pour la décomposition tendance/saisonnalité et les prévisions. "
            "L'utilisateur peut ajuster l'horizon de prévision via un slider. "
            "Affiche les composantes de la série temporelle et les intervalles de confiance. "
            "Bibliothèques : prophet, plotly, matplotlib, pandas."
        ),
    },
    {
        "id": "mlflow",
        "text": (
            "Page MLflow Classifier (Machine Learning & IA) : Classification du cancer du sein "
            "avec tuning d'hyperparamètres (GridSearchCV) et tracking MLflow. "
            "Utilise le dataset Breast Cancer de scikit-learn et Logistic Regression. "
            "Affiche les métriques (accuracy, precision, recall, F1) et les résultats de la grille de recherche. "
            "Permet de télécharger les résultats via st.download_button. "
            "Bibliothèques : scikit-learn, mlflow 2.17, matplotlib."
        ),
    },
    {
        "id": "leaf_detect",
        "text": (
            "Page Leaf Detection (Machine Learning & IA) : Classification d'espèces de plantes "
            "via un modèle TensorFlow/Keras MobileNet pré-entraîné. "
            "L'utilisateur uploade une photo de plante et le modèle prédit l'espèce avec le nom en français. "
            "Le modèle (latest_checkpoint.h5, 27.5 MB) est chargé depuis le dossier models/. "
            "Utilise Pillow pour le preprocessing et OpenCV pour l'analyse d'image. "
            "Bibliothèques : tensorflow 2.16, tf-keras, Pillow, OpenCV."
        ),
    },
    {
        "id": "reco",
        "text": (
            "Page Reco (Machine Learning & IA) : Évaluation de recommandations d'audit par LLM Mistral. "
            "L'utilisateur saisit une recommandation d'audit dans un text_area. "
            "Le LLM Mistral (mistral-large-latest) évalue la recommandation sur plusieurs critères "
            "et renvoie un scoring structuré en JSON. "
            "Utilise l'API Mistral AI avec la clé stockée dans st.secrets. "
            "Bibliothèques : requests, json."
        ),
    },
    {
        "id": "bm25",
        "text": (
            "Page BM25 vs TF-IDF vs CV (NLP & Recherche) : Comparaison interactive des trois méthodes "
            "de vectorisation de texte. "
            "BM25 (Best Match 25, algorithme de ranking probabiliste), "
            "TF-IDF (Term Frequency-Inverse Document Frequency), "
            "et CountVectorizer (sac de mots). "
            "L'utilisateur peut saisir un corpus et une requête pour comparer les scores de similarité. "
            "Bibliothèques : rank-bm25, scikit-learn (TfidfVectorizer, CountVectorizer), nltk, plotly."
        ),
    },
    {
        "id": "gale_shapley",
        "text": (
            "Page Gale-Shapley (NLP & Recherche) : Implémentation de l'algorithme de matching stable "
            "pour l'attribution équipes/joueurs. "
            "L'utilisateur configure les équipes et joueurs ainsi que leurs préférences. "
            "L'algorithme trouve un matching stable où aucune paire ne préférerait mutuellement changer. "
            "Complexité O(n²). Permet d'exporter les résultats en CSV via st.download_button. "
            "Bibliothèques : pandas."
        ),
    },
    {
        "id": "checkbox",
        "text": (
            "Page Checkbox Detection (Vision par ordinateur) : Détection robuste de cases à cocher "
            "dans des documents scannés. "
            "Pipeline multi-méthodes : détection des contours (Canny + Gaussian blur), "
            "template matching (cv2.matchTemplate), clustering DBSCAN pour dédoublonner les détections, "
            "et filtrage par IoU (Intersection over Union). "
            "L'utilisateur peut uploader une image ou utiliser l'image de test. "
            "Bibliothèques : OpenCV, scikit-learn (DBSCAN), NumPy, Pillow."
        ),
    },
    {
        "id": "lcr",
        "text": (
            "Page Simulation LCR (Finance & Audit) : Simulation du Liquidity Coverage Ratio (LCR) "
            "selon les normes Bâle III. "
            "Le LCR mesure la résilience à court terme d'une banque face aux stress de liquidité. "
            "L'utilisateur peut ajuster les paramètres de stress testing sur 30 jours (sliders). "
            "Affiche l'évolution du LCR avec des métriques colorées selon le seuil réglementaire (100%). "
            "Bibliothèques : pandas, plotly, scipy."
        ),
    },
    {
        "id": "isin",
        "text": (
            "Page ISIN Check (Finance & Audit) : Validateur de codes ISIN "
            "(International Securities Identification Number). "
            "Implémente l'algorithme de Luhn adapté aux codes ISIN (12 caractères alphanumériques). "
            "L'utilisateur saisit un code ISIN et l'application vérifie sa validité et décompose "
            "ses composantes (pays, code national, chiffre de contrôle). "
            "Bibliothèques : standard Python uniquement."
        ),
    },
    {
        "id": "gsheet",
        "text": (
            "Page GSheet (Finance & Audit) : Affichage du cours de l'action Tesla (TSLA) sur 90 jours "
            "depuis Google Sheets via la formule GOOGLEFINANCE. "
            "Utilise st.connection avec GSheetsConnection pour se connecter à Google Sheets. "
            "Affiche les données dans un st.dataframe interactif avec des colonnes formatées "
            "(DateColumn, NumberColumn). Affiche des métriques clés (prix actuel, variation). "
            "Bibliothèques : st-gsheets-connection, pandas."
        ),
    },
    {
        "id": "meteo",
        "text": (
            "Page Open-Meteo API (Outils & APIs) : Exploration de l'API météo publique et gratuite Open-Meteo. "
            "Affiche les conditions météo actuelles, les prévisions sur 7 jours et l'historique sur 30 jours. "
            "Interface avec onglets (st.tabs) et sélection de ville (st.selectbox). "
            "Utilise des graphiques Plotly pour la température et st.bar_chart pour précipitations/vent. "
            "L'API Open-Meteo est publique, sans clé d'authentification. "
            "Bibliothèques : requests, plotly, pandas."
        ),
    },
    {
        "id": "game",
        "text": (
            "Page The Game (Outils & APIs) : Implémentation du jeu de cartes The Game "
            "(jeu coopératif où l'on pose des cartes numérotées sur 4 piles selon des règles strictes). "
            "Mode joueur interactif et mode auto-play avec une IA greedy "
            "(heuristique de minimisation des écarts). "
            "Utilise st.session_state pour gérer l'état du jeu entre les reruns. "
            "Utilise st.rerun() pour le mode auto-play et du CSS personnalisé pour le style des cartes. "
            "Bibliothèques : streamlit uniquement."
        ),
    },
    {
        "id": "cocktail",
        "text": (
            "Page Cocktail (Outils & APIs) : Suggestions de recettes de cocktails selon les ingrédients disponibles. "
            "L'utilisateur sélectionne ses ingrédients disponibles (multiselect) et l'application filtre "
            "les recettes réalisables. Base de données de recettes stockée en JSON local (cocktails.json). "
            "Inventaire personnel persistant dans mon_bar.json. "
            "Bibliothèques : streamlit, json."
        ),
    },
    {
        "id": "stack",
        "text": (
            "Stack technique du portfolio : "
            "Framework : Streamlit ≥ 1.32. "
            "Machine Learning : scikit-learn, TensorFlow ≥ 2.16, tf-keras, Prophet 1.3, SHAP 0.44. "
            "NLP : rank-bm25, NLTK. "
            "Vision : OpenCV (headless), Pillow. "
            "Expérimentation : MLflow 2.17. "
            "Visualisation : Plotly, Matplotlib, Seaborn 0.13. "
            "Data : pandas 2.3.3, NumPy 1.26.4. "
            "APIs externes : Mistral AI, Open-Meteo (publique, sans clé), Google Sheets (GOOGLEFINANCE). "
            "Environnement : Python 3.11, devcontainer Codespaces."
        ),
    },
    {
        "id": "config",
        "text": (
            "Configuration et déploiement du portfolio : "
            "Déployé sur Streamlit Cloud à l'adresse levmanuel-demo.streamlit.app. "
            "Le dépôt source est github.com/levmanuel/streamlit-demo. "
            "Pour lancer en local : pip install -r requirements.txt && streamlit run home.py. "
            "Les credentials sont stockés dans .streamlit/secrets.toml (non commité). "
            "Secrets requis : [api] MISTRAL_API_KEY pour la page Reco et la page Chat RAG ; "
            "[connections.gsheets] spreadsheet et type pour la page GSheet."
        ),
    },
]

SYSTEM_PROMPT = (
    "Tu es un assistant expert sur ce portfolio Streamlit de Data Science et ML. "
    "Tu réponds en français, de façon précise et concise. "
    "Tu t'appuies uniquement sur le contexte fourni pour répondre aux questions sur les pages du portfolio. "
    "Si tu ne trouves pas la réponse dans le contexte, dis-le clairement. "
    "Ne fabrique pas d'informations."
)


def get_embedding(text: str) -> list[float]:
    resp = requests.post(
        MISTRAL_EMBED_URL,
        headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
        json={"model": EMBED_MODEL, "input": [text]},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["data"][0]["embedding"]


@st.cache_resource(show_spinner="Construction de l'index de connaissance…")
def build_index() -> np.ndarray:
    embeddings = [get_embedding(chunk["text"]) for chunk in KNOWLEDGE_BASE]
    return np.array(embeddings)


def retrieve(query: str, index: np.ndarray, k: int = 3) -> list[str]:
    q_emb = np.array(get_embedding(query))
    norms = np.linalg.norm(index, axis=1) * np.linalg.norm(q_emb)
    scores = index @ q_emb / np.where(norms == 0, 1e-10, norms)
    top_k = np.argsort(scores)[::-1][:k]
    return [KNOWLEDGE_BASE[i]["text"] for i in top_k]


def stream_mistral(messages: list[dict]):
    """Générateur de tokens compatible avec st.write_stream."""
    resp = requests.post(
        MISTRAL_CHAT_URL,
        headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
        json={"model": CHAT_MODEL, "messages": messages, "stream": True},
        stream=True,
        timeout=60,
    )
    resp.raise_for_status()
    for line in resp.iter_lines():
        if line and line.startswith(b"data: ") and line != b"data: [DONE]":
            data = json.loads(line[6:])
            token = data["choices"][0]["delta"].get("content", "")
            if token:
                yield token


# ── Page ─────────────────────────────────────────────────────────

st.title("💬 Chat — Assistant Portfolio")
st.caption(
    "Posez vos questions sur ce portfolio : pages, techniques, bibliothèques, configuration… "
    "Les réponses sont générées par **Mistral** en streaming, avec récupération RAG sur la documentation."
)

with st.expander("Comment ça fonctionne ?"):
    st.markdown(
        """
**Pipeline RAG :**
1. **Indexation** — au démarrage, chaque page du portfolio est encodée en vecteur via l'**API Mistral Embeddings** (`mistral-embed`) — mis en cache avec `@st.cache_resource`.
2. **Récupération** — votre question est encodée, puis les 3 chunks les plus proches sont trouvés par **similarité cosinus** (numpy).
3. **Génération streamée** — le contexte récupéré est injecté dans le prompt système, et la réponse est générée par **Mistral** (`mistral-large-latest`) en streaming SSE, affichée token par token via `st.write_stream`.

**Features Streamlit démontrées :** `st.chat_input`, `st.chat_message`, `st.write_stream`, `@st.cache_resource`, `st.session_state`.
        """
    )

index = build_index()

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ex : Comment fonctionne la page SHAP ?"):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    context_chunks = retrieve(prompt, index, k=3)
    context = "\n\n".join(f"---\n{c}" for c in context_chunks)

    api_messages = [
        {
            "role": "system",
            "content": f"{SYSTEM_PROMPT}\n\nContexte récupéré :\n{context}",
        }
    ] + [{"role": m["role"], "content": m["content"]} for m in st.session_state["messages"]]

    with st.chat_message("assistant"):
        response = st.write_stream(stream_mistral(api_messages))

    st.session_state["messages"].append({"role": "assistant", "content": response})
