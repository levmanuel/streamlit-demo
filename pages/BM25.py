import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

st.set_page_config(layout="wide")
st.title("🕵️♂️ Analyse Comparative de Méthodes de Vectorisation Texte")

# Configuration avancée
st.sidebar.header("Configuration")
max_features = st.sidebar.slider("Nombre maximal de features", 10, 1000, 200)
analyzer = st.sidebar.selectbox("Analyzer", ["word", "char", "char_wb"])
k1 = st.sidebar.slider("Paramètre BM25 k1", 1.0, 2.0, 1.5)
b = st.sidebar.slider("Paramètre BM25 b", 0.0, 1.0, 0.75)

# Exemples de phrases plus complexes
DEFAULT_TEXT = """L'apprentissage profond révolutionne l'analyse des données médicales.
Les modèles de langage à grande échelle posent des défis éthiques importants.
Le réchauffement climatique entraîne des phénomènes météorologiques extrêmes.
L'économie circulaire promet une croissance durable mais nécessite des investissements initiaux.
Les cyberattaques sophistiquées ciblent les infrastructures critiques mondialement."""

# Interface utilisateur
st.header("Entrée des données")

def plot_heatmap(matrix, features, title):
    plt.figure(figsize=(12, 8))
    sns.heatmap(matrix[:5], annot=True, fmt=".2f", cmap="YlGnBu",
                xticklabels=features, yticklabels=[f"Doc {i+1}" for i in range(len(matrix[:5]))])
    plt.title(title)
    st.pyplot(plt)

sample_texts = st.text_area("Phrases d'exemple (une par ligne)", DEFAULT_TEXT, height=150)
query = st.text_input("Requête de recherche", "modèles climatiques éthiques données")

# Prétraitement
texts = [text.strip() for text in sample_texts.split("\n") if text.strip()]
french_stopwords = stopwords.words('french')

def preprocess(text):
    return ' '.join([word.lower() for word in text.split() 
                    if word.lower() not in french_stopwords and len(word) > 2])

# Calculs des similarités
if texts:
    processed_texts = [preprocess(text) for text in texts]
    processed_query = preprocess(query)
    
    # Vectorisation
    count_vec = CountVectorizer(max_features=max_features, analyzer=analyzer)
    count_matrix = count_vec.fit_transform(processed_texts)
    
    tfidf_vec = TfidfVectorizer(max_features=max_features, analyzer=analyzer)
    tfidf_matrix = tfidf_vec.fit_transform(processed_texts)
    
    # BM25
    tokenized_corpus = [doc.split() for doc in processed_texts]
    bm25 = BM25Okapi(tokenized_corpus, k1=k1, b=b)
    tokenized_query = processed_query.split()
    
    # Scores avancés
    count_sims = cosine_similarity(count_vec.transform([processed_query]), count_matrix)
    tfidf_sims = cosine_similarity(tfidf_vec.transform([processed_query]), tfidf_matrix)
    bm25_scores = bm25.get_scores(tokenized_query)
    top_n_docs = bm25.get_top_n(tokenized_query, texts, n=3)

    # Affichage des résultats
    st.header("🔍 Résultats détaillés")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("CountVectorizer")
        st.write("Similarité cosinus avec la requête:")
        st.bar_chart(pd.DataFrame({
            'Textes': [f"Doc {i+1}" for i in range(len(texts))],
            'Similarité': count_sims[0]
        }).set_index('Textes'))
    
    with col2:
        st.subheader("TF-IDF")
        st.write("Similarité cosinus avec la requête:")
        st.bar_chart(pd.DataFrame({
            'Textes': [f"Doc {i+1}" for i in range(len(texts))],
            'Similarité': tfidf_sims[0]
        }).set_index('Textes'))
    
    with col3:
        st.subheader("BM25")
        st.write("Scores bruts BM25:")
        st.bar_chart(pd.DataFrame({
            'Textes': [f"Doc {i+1}" for i in range(len(texts))],
            'Score': bm25_scores
        }).set_index('Textes'))
    
    # Top documents BM25
    st.subheader("📌 Top 3 des documents pertinents (BM25)")
    for i, doc in enumerate(top_n_docs):
        st.markdown(f"{i+1}. {doc}")
    
    # Explications techniques
    st.header("📚 Explications des métriques")
    
    st.markdown("""
    **Métriques utilisées :**
    1. **Similarité Cosinus** : Mesure la similarité directionnelle entre vecteurs
    2. **Scores BM25** : Algorithme probabiliste optimisé pour la recherche documentaire
    3. **Top N Documents** : Sélection des documents les plus pertinents selon BM25

    **Différences clés :**
    - 🧮 **CountVectorizer** : Comptage brut des occurrences
    - 📈 **TF-IDF** : Pondération par importance statistique
    - 🏆 **BM25** : 
        - Pénalise les documents longs (paramètre b)
        - Non-linearité dans les fréquences (paramètre k1)
        - Optimisé pour le ranking de résultats
    """)

else:
    st.warning("⚠️ Veuillez entrer au moins une phrase valide!")

