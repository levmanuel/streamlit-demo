# Streamlit Demo

Portfolio interactif multi-pages construit avec Streamlit, regroupant des démos de machine learning, data science et outils utilitaires.

## Démos disponibles

| Page | Description |
|------|-------------|
| **SHAP** | Explicabilité ML sur le dataset California Housing (explications globales & locales) |
| **Cocktail** | Suggestions de recettes de cocktails selon les ingrédients disponibles |
| **Prophet** | Prévision de séries temporelles sur des données de température (Yosemite) |
| **MLflow Classifier** | Classification avec tuning d'hyperparamètres et suivi via MLflow |
| **The Game** | Jeu de cartes interactif |
| **OpenCV / DBSCAN** | Traitement d'image : détection de contours et template matching |
| **Gale-Shapley** | Algorithme de matching stable équipes / joueurs |
| **BM25 vs TF-IDF vs CV** | Comparaison de techniques de vectorisation NLP |
| **Leaf Detection** | Classification d'espèces de plantes via un modèle TensorFlow |
| **ISIN Check** | Validateur de codes ISIN |
| **API Railway** | Interface client pour l'API Railway |
| **Reco** | Système de recommandation via l'API Mistral |
| **GSheet** | Intégration Google Sheets |
| **Simulation LCR** | Simulation du ratio de liquidité à court terme (LCR) |

## Stack technique

- **Framework** : Streamlit 1.28
- **ML** : scikit-learn, TensorFlow 2.16+, Prophet 1.3, SHAP 0.44.1
- **NLP** : rank_bm25, NLTK
- **Vision** : OpenCV, Pillow
- **Expérimentation** : MLflow 2.17
- **Visualisation** : Plotly, Matplotlib, Seaborn
- **Data** : pandas 2.3.3, NumPy 1.26.4

## Installation

```bash
pip install -r requirements.txt
streamlit run home.py
```

L'application est accessible à `http://localhost:8501`.

## Configuration optionnelle

- **Google Sheets** (`gsheet.py`) : credentials API Google Sheets requis
- **Mistral AI** (`reco.py`) : clé API à placer dans `.streamlit/secrets.toml`

```toml
# .streamlit/secrets.toml
MISTRAL_API_KEY = "votre_clé_ici"
```
