import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
import nltk
from nltk.corpus import stopwords

nltk.download("stopwords", quiet=True)

st.set_page_config(layout="wide")
st.title("🕵️ BM25 vs TF-IDF vs CountVectorizer")
st.write(
    "Comparez trois méthodes de vectorisation sur un corpus conçu pour révéler leurs différences. "
    "Chaque document a été rédigé pour illustrer un comportement spécifique."
)

# --- Corpus illustratif ---
# Les documents sont volontairement conçus pour révéler les limites de chaque méthode.
DOCS = [
    {
        "label": "📄 A — Pertinent et concis",
        "text": "L'audit opérationnel a identifié des risques financiers majeurs dans le processus de contrôle interne.",
        "note": "Court, dense, tous les mots-clés présents une fois."
    },
    {
        "label": "📄 B — Répétition abusive",
        "text": (
            "risques risques risques risques risques risques risques risques risques risques "
            "audit audit audit audit audit audit financier financier opérationnel opérationnel "
            "— document répétitif sans contenu réel."
        ),
        "note": "Répète les mots-clés sans apporter de sens. CV va le surnoter."
    },
    {
        "label": "📄 C — Long et dilué",
        "text": (
            "La gestion d'entreprise implique de nombreuses dimensions. Les ressources humaines, "
            "la logistique, la relation client, la communication interne et la stratégie marketing "
            "sont autant de leviers de performance. Par ailleurs, dans un contexte plus large, "
            "un audit opérationnel peut révéler des risques financiers ponctuels. "
            "La formation continue des équipes reste néanmoins la priorité absolue de la direction."
        ),
        "note": "Mots-clés noyés dans un long texte hors sujet. BM25 pénalise la longueur."
    },
    {
        "label": "📄 D — Très pertinent et riche",
        "text": (
            "Le rapport d'audit a mis en évidence plusieurs risques opérationnels critiques : "
            "défaillance du contrôle interne, exposition aux risques financiers de contrepartie, "
            "et insuffisance des procédures de validation. Ces risques requièrent une action correctrice immédiate."
        ),
        "note": "Riche, pertinent, mentionne les concepts clés dans leur contexte."
    },
    {
        "label": "📄 E — Hors sujet partiel",
        "text": (
            "Les marchés financiers sont soumis à une volatilité croissante. "
            "Les investisseurs institutionnels diversifient leurs portefeuilles pour limiter leur exposition. "
            "Le secteur bancaire adapte ses stratégies en réponse aux nouvelles réglementations prudentielles."
        ),
        "note": "Partage le terme 'financier' mais le sujet est différent."
    },
    {
        "label": "📄 F — Hors sujet total",
        "text": (
            "La cuisine méditerranéenne est reconnue pour ses bienfaits sur la santé. "
            "L'huile d'olive, les légumineuses et les herbes aromatiques constituent la base d'une alimentation équilibrée."
        ),
        "note": "Aucun mot-clé commun avec la requête."
    },
]

DEFAULT_QUERY = "risques opérationnels audit financier"

# --- Sidebar ---
st.sidebar.header("Configuration BM25")
k1 = st.sidebar.slider("k1 — saturation de fréquence", 1.0, 2.0, 1.5,
                        help="Plus k1 est élevé, plus les répétitions sont récompensées.")
b = st.sidebar.slider("b — normalisation par longueur", 0.0, 1.0, 0.75,
                       help="b=1 pénalise fortement les documents longs, b=0 ne pénalise pas.")

st.sidebar.markdown("---")
st.sidebar.subheader("Corpus")
for doc in DOCS:
    with st.sidebar.expander(doc["label"]):
        st.write(doc["text"])
        st.caption(f"💡 {doc['note']}")

# --- Requête ---
st.header("Requête")
query = st.text_input("", DEFAULT_QUERY)

# --- Prétraitement ---
french_stopwords = set(stopwords.words("french"))

def preprocess(text):
    return " ".join(
        w.lower() for w in text.split()
        if w.lower() not in french_stopwords and len(w) > 2
    )

texts = [doc["text"] for doc in DOCS]
labels = [doc["label"] for doc in DOCS]
processed_texts = [preprocess(t) for t in texts]
processed_query = preprocess(query)

# --- Calculs ---
count_vec = CountVectorizer()
count_matrix = count_vec.fit_transform(processed_texts)
count_sims = cosine_similarity(count_vec.transform([processed_query]), count_matrix)[0]

tfidf_vec = TfidfVectorizer()
tfidf_matrix = tfidf_vec.fit_transform(processed_texts)
tfidf_sims = cosine_similarity(tfidf_vec.transform([processed_query]), tfidf_matrix)[0]

tokenized_corpus = [doc.split() for doc in processed_texts]
bm25 = BM25Okapi(tokenized_corpus, k1=k1, b=b)
bm25_scores_raw = bm25.get_scores(processed_query.split())
# Normaliser BM25 entre 0 et 1 pour comparer visuellement
bm25_max = bm25_scores_raw.max()
bm25_scores = bm25_scores_raw / bm25_max if bm25_max > 0 else bm25_scores_raw

# --- Graphique comparatif ---
st.header("📊 Scores de pertinence par méthode")
st.caption("BM25 normalisé entre 0 et 1 pour faciliter la comparaison visuelle.")

short_labels = [d["label"].split("—")[0].strip() for d in DOCS]

fig = go.Figure()
fig.add_trace(go.Bar(name="CountVectorizer", x=short_labels, y=count_sims,
                     marker_color="#4C72B0"))
fig.add_trace(go.Bar(name="TF-IDF", x=short_labels, y=tfidf_sims,
                     marker_color="#DD8452"))
fig.add_trace(go.Bar(name="BM25 (normalisé)", x=short_labels, y=bm25_scores,
                     marker_color="#55A868"))
fig.update_layout(
    barmode="group",
    yaxis_title="Score de similarité",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    plot_bgcolor="white",
    yaxis=dict(gridcolor="#f0f0f0", range=[0, 1.1]),
    margin=dict(t=40, b=0),
)
st.plotly_chart(fig, use_container_width=True)

# --- Tableau de scores ---
st.header("📋 Scores détaillés")
df_scores = pd.DataFrame({
    "Document": labels,
    "Note": [d["note"] for d in DOCS],
    "CountVectorizer": [f"{s:.3f}" for s in count_sims],
    "TF-IDF": [f"{s:.3f}" for s in tfidf_sims],
    "BM25 (norm.)": [f"{s:.3f}" for s in bm25_scores],
})
st.dataframe(df_scores, use_container_width=True, hide_index=True)

# --- Observations pédagogiques ---
st.header("💡 Ce que révèle ce corpus")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("#### 🧮 CountVectorizer")
    st.markdown("""
**Comptage brut des occurrences.**

- **Doc B** (répétition) obtient un score élevé car il contient beaucoup d'occurrences des mots-clés.
- Ne distingue pas un document court et pertinent d'un document long et dilué.
- Sensible au *keyword stuffing*.
    """)

with col2:
    st.markdown("#### 📈 TF-IDF")
    st.markdown("""
**Pondère par rareté statistique.**

- Améliore le traitement des mots fréquents (réduit le biais de CV).
- Mais ne normalise pas par la longueur du document.
- **Doc C** (long et dilué) reste surnoté par rapport à **Doc A**.
    """)

with col3:
    st.markdown("#### 🏆 BM25")
    st.markdown("""
**Saturation + normalisation par longueur.**

- **Doc B** est pénalisé : les répétitions au-delà d'un seuil n'apportent plus de score (paramètre k1).
- **Doc C** est pénalisé pour sa longueur (paramètre b).
- **Doc A** et **Doc D** ressortent comme les plus pertinents.
    """)
