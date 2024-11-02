import streamlit as st
import pandas as pd
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score
import mlflow
import matplotlib.pyplot as plt
import pickle  # Pour la sérialisation du modèle

# Chargement du dataset Breast Cancer
data = load_breast_cancer()
X = pd.DataFrame(data.data, columns=data.feature_names)
y = pd.Series(data.target, name="target")

# Titre de l'application
st.title("Modèle de Classification du Cancer du Sein - Suivi avec MLflow et Fine-Tuning des Hyperparamètres")

# Fraction de test pour le dataset
test_size = st.slider("Sélectionner la taille de l'ensemble de test", 0.1, 0.5, 0.2)

st.write(X.head(10))

# Bouton pour exécuter l'entraînement avec recherche d'hyperparamètres
if st.button("Entraîner le modèle avec Fine-Tuning"):
    # Division du dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    # Initialisation de MLflow
    mlflow.set_experiment("Breast_Cancer_Classification_with_Hyperparameter_Tuning")

    # Définir la grille des hyperparamètres pour Logistic Regression
    param_grid = {
        'C': np.logspace(-3, 3, 7),
        'solver': ['liblinear']
    }

    # Configuration de la recherche par grille avec validation croisée
    grid_search = GridSearchCV(LogisticRegression(max_iter=10000), param_grid, cv=5, scoring='accuracy')
    grid_search.fit(X_train, y_train)

    # Enregistrement des meilleures métriques dans MLflow
    with mlflow.start_run():
        best_model = grid_search.best_estimator_
        y_pred = best_model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)

        # Enregistrement des meilleurs hyperparamètres et métriques
        mlflow.log_param("test_size", test_size)
        mlflow.log_params(grid_search.best_params_)
        mlflow.log_metric("best_accuracy", accuracy)
        mlflow.log_metric("best_precision", precision)
        mlflow.log_metric("best_recall", recall)

        # Enregistrement du modèle
        mlflow.sklearn.log_model(best_model, "best_logistic_regression_model")

        # Affichage des meilleurs résultats
        st.write("**Meilleur Accuracy** :", accuracy)
        st.write("**Meilleur Precision** :", precision)
        st.write("**Meilleur Recall** :", recall)
        st.write("**Meilleurs Paramètres** :", grid_search.best_params_)
        st.success("Entraînement terminé avec fine-tuning et suivi enregistré dans MLflow !")

    # Visualisation des résultats de la recherche d'hyperparamètres
    results = pd.DataFrame(grid_search.cv_results_)
    plt.figure(figsize=(10, 6))
    plt.plot(results['param_C'], results['mean_test_score'], marker='o')
    plt.xscale('log')
    plt.xlabel('Paramètre de régularisation C (log scale)')
    plt.ylabel('Accuracy moyenne')
    plt.title('Impact de la régularisation sur l’accuracy')
    st.pyplot(plt)

    # Sérialisation du modèle avec pickle
    model_data = pickle.dumps(best_model)

    # Bouton de téléchargement
    st.download_button(
        label="Télécharger le modèle",
        data=model_data,
        file_name="best_logistic_regression_model.pkl",
        mime="application/octet-stream"
    )