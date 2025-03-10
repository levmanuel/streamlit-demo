import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from rank_bm25 import BM25Okapi

st.title("Comparaison des méthodes de vectorisation de texte")

# Configuration
st.sidebar.header("Paramètres")
max_features = st.sidebar.slider("Nombre maximal de features", 10, 1000, 100)
analyzer = st.sidebar.selectbox("Analyzer", ["word", "char", "char_wb"])

# Input des données
st.header("Entrez vos données")
sample_texts = st.text_area("Phrases d'exemple (une par ligne)", 
                           "Le chat dort sur le tapis\nLe chien court dans le jardin\nUn oiseau chante dans l'arbre")
query = st.text_input("Requête de recherche", "chat chien jardin")

texts = [text.strip() for text in sample_texts.split("\n") if text.strip()]

# Fonctions de traitement
def plot_heatmap(matrix, features, title):
    plt.figure(figsize=(12, 6))
    sns.heatmap(matrix, annot=True, fmt=".2f", cmap="Blues", 
                xticklabels=features, yticklabels=texts)
    plt.title(title)
    st.pyplot(plt)

def get_bm25_scores(corpus, query):
    tokenized_corpus = [doc.split(" ") for doc in corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = query.split(" ")
    doc_scores = bm25.get_scores(tokenized_query)
    return doc_scores

# Calcul des représentations vectorielles
if texts:
    # CountVectorizer
    count_vec = CountVectorizer(max_features=max_features, analyzer=analyzer)
    count_matrix = count_vec.fit_transform(texts).toarray()
    
    # TF-IDF
    tfidf_vec = TfidfVectorizer(max_features=max_features, analyzer=analyzer)
    tfidf_matrix = tfidf_vec.fit_transform(texts).toarray()
    
    # BM25
    bm25_scores = get_bm25_scores(texts, query)
    
    # Affichage des résultats
    st.header("Résultats")
    
    with st.expander("CountVectorizer"):
        st.write("Matrice de comptage:")
        plot_heatmap(count_matrix, count_vec.get_feature_names_out(), "CountVectorizer")
    
    with st.expander("TF-IDF"):
        st.write("Matrice TF-IDF:")
        plot_heatmap(tfidf_matrix, tfidf_vec.get_feature_names_out(), "TF-IDF")
    
    with st.expander("BM25"):
        st.write("Scores BM25 pour la requête:")
        fig, ax = plt.subplots()
        ax.barh(range(len(bm25_scores)), bm25_scores)
        ax.set_yticks(range(len(texts)))
        ax.set_yticklabels(texts)
        ax.set_title("Scores BM25")
        st.pyplot(fig)
    
    # Comparaison des méthodes
    st.header("Comparaison des scores pour la requête")
    
    comparison_df = pd.DataFrame({
        "Texte": texts,
        "CountVectorizer": [np.sum(count_vec.transform([t]).toarray()) for t in texts],
        "TF-IDF": [np.sum(tfidf_vec.transform([t]).toarray()) for t in texts],
        "BM25": bm25_scores
    })
    
    st.dataframe(comparison_df.style.highlight_max(color='lightgreen', axis=0))
    
    # Explication des différences
    st.header("Explication des différences")
    st.markdown("""
    - **CountVectorizer** : Compte simple des occurrences de mots
    - **TF-IDF** : Pondère les mots par leur fréquence inverse dans le corpus
    - **BM25** : Algorithme de classement plus sophistiqué qui prend en compte :
        - Longueur des documents
        - Fréquence des termes
        - Pondération non linéaire
    """)

else:
    st.warning("Veuillez entrer au moins une phrase d'exemple")