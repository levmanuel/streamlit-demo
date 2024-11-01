import streamlit as st
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score
import mlflow

# Chargement du dataset Breast Cancer
data = load_breast_cancer()
X = pd.DataFrame(data.data, columns=data.feature_names)
y = pd.Series(data.target, name="target")

# Titre de l'application
st.title("Modèle de Classification du Cancer du Sein - Suivi avec MLflow")

# Fraction de test pour le dataset
test_size = st.slider("Sélectionner la taille de l'ensemble de test", 0.1, 0.5, 0.2)

st.write(X.head(10))

# Bouton pour exécuter l'entraînement
if st.button("Entraîner le modèle"):
    # Division du dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    # Initialisation de MLflow
    mlflow.set_experiment("Breast_Cancer_Classification")

    with mlflow.start_run():
        # Création et entraînement du modèle de classification
        model = LogisticRegression(max_iter=10000)
        model.fit(X_train, y_train)

        # Prédiction sur l'ensemble de test
        y_pred = model.predict(X_test)

        # Calcul des métriques
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)

        # Enregistrement des métriques et paramètres dans MLflow
        mlflow.log_param("test_size", test_size)
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)

        # Enregistrement du modèle
        mlflow.sklearn.log_model(model, "logistic_regression_model")

        # Affichage des résultats dans Streamlit
        st.write("**Précision (Accuracy)** :", accuracy)
        st.write("**Précision (Precision)** :", precision)
        st.write("**Rappel (Recall)** :", recall)
        st.success("Entraînement terminé et suivi enregistré dans MLflow !")

    # Affichage des prédictions vs Réalité
    st.write("### Prédictions vs Réalité")
    results_df = pd.DataFrame({"Réalité": y_test, "Prédiction": y_pred})
    st.write(results_df.head(10))
    st.write("Tableau des 10 premières prédictions pour vérifier les résultats.")