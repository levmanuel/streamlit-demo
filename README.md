# Streamlit Demo

Portfolio interactif de démos Machine Learning, Data Science et outils métier, déployé sur Streamlit Cloud.

🚀 **[levmanuel-demo.streamlit.app](https://levmanuel-demo.streamlit.app)**

---

## Démos

### Machine Learning & IA

| Page | Description |
|------|-------------|
| **SHAP** | Explicabilité ML (globale & locale) sur le dataset California Housing avec Random Forest |
| **Prophet** | Prévision de séries temporelles sur les températures de Yosemite |
| **MLflow Classifier** | Classification cancer du sein avec tuning d'hyperparamètres et tracking MLflow |
| **Leaf Detection** | Classification d'espèces de plantes via un modèle TensorFlow (MobileNet) |
| **Reco** | Évaluation de recommandations d'audit par LLM (Mistral) avec scoring structuré |

### NLP & Recherche

| Page | Description |
|------|-------------|
| **BM25 vs TF-IDF vs CV** | Comparaison interactive des trois méthodes de vectorisation sur corpus illustratif |
| **Gale-Shapley** | Algorithme de matching stable équipes / joueurs |

### Vision & Traitement d'image

| Page | Description |
|------|-------------|
| **Checkbox Detection** | Détection robuste de cases à cocher par contours + template matching (DBSCAN + IoU) |

### Finance & Audit

| Page | Description |
|------|-------------|
| **Simulation LCR** | Simulation du Liquidity Coverage Ratio (Bâle III) avec stress testing sur 30 jours |
| **ISIN Check** | Validateur de codes ISIN (algorithme de Luhn adapté) |
| **GSheet** | Cours TSLA sur 90 jours depuis Google Sheets (`GOOGLEFINANCE`) |

### Outils & APIs

| Page | Description |
|------|-------------|
| **Open-Meteo API** | Exploration d'une API météo publique : conditions actuelles, prévisions, historique |
| **The Game** | Implémentation du jeu de cartes The Game avec mode auto-play (IA) et mode joueur |
| **Cocktail** | Suggestions de recettes de cocktails selon les ingrédients disponibles |

---

## Stack technique

| Catégorie | Librairies |
|-----------|------------|
| Framework | Streamlit ≥ 1.32 |
| ML | scikit-learn, TensorFlow ≥ 2.16, tf-keras, Prophet 1.3, SHAP 0.44 |
| NLP | rank-bm25, NLTK |
| Vision | OpenCV (headless), Pillow |
| Expérimentation | MLflow 2.17 |
| Visualisation | Plotly, Matplotlib, Seaborn 0.13 |
| Data | pandas 2.3.3, NumPy 1.26.4 |
| APIs | Mistral AI, Open-Meteo, Google Sheets |

---

## Lancer en local

```bash
pip install -r requirements.txt
streamlit run home.py
```

L'application démarre sur `http://localhost:8501`.

## Configuration

Certaines pages nécessitent des credentials dans `.streamlit/secrets.toml` :

```toml
# Mistral AI — page Reco
[api]
MISTRAL_API_KEY = "votre_clé_mistral"

# Google Sheets — page GSheet
[connections.gsheets]
spreadsheet = "https://docs.google.com/spreadsheets/d/..."
type = "st.connections.ExperimentalBaseConnection"
```
