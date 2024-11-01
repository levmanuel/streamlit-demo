import streamlit as st
import pandas as pd
from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import mlflow

# Chargement du dataset Boston
boston = load_boston()
X = pd.DataFrame(boston.data, columns=boston.feature_names)
y = pd.Series(boston.target, name="MEDV")  # MEDV : Median value of owner-occupied homes

# Titre de l'application
st.title("Modèle de Régression des Prix de Maison - Suivi avec MLflow")

# Fraction de test pour le dataset
test_size = st.slider("Sélectionner la taille de l'ensemble de test", 0.1, 0.5, 0.2)

# Bouton pour exécuter l'entraînement
if st.button("Entraîner le modèle"):
    # Division du dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    # Initialisation de MLflow
    mlflow.set_experiment("Boston_House_Price_Prediction")
    
    with mlflow.start_run():
        # Création et entraînement du modèle de régression linéaire
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Prédiction sur l'ensemble de test
        y_pred = model.predict(X_test)

        # Calcul des métriques
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        # Enregistrement des métriques et paramètres dans MLflow
        mlflow.log_param("test_size", test_size)
        mlflow.log_metric("MSE", mse)
        mlflow.log_metric("R2", r2)

        # Affichage des résultats
        st.write("**Erreur quadratique moyenne (MSE)** :", mse)
        st.write("**Coefficient de détermination (R²)** :", r2)

        # Enregistrement du modèle
        mlflow.sklearn.log_model(model, "linear_regression_model")

        st.success("Entraînement terminé et suivi enregistré dans MLflow !")

    # Affichage des prédictions
    st.write("### Prédictions vs Réalité")
    results_df = pd.DataFrame({"Réalité": y_test, "Prédiction": y_pred})
    st.write(results_df.head(10))
    st.line_chart(results_df)