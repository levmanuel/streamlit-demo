import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from prophet import Prophet
import matplotlib.pyplot as plt

# Charger le dataset de Yosemite
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/facebook/prophet/main/examples/example_yosemite_temps.csv"
    df = pd.read_csv(url)
    df['ds'] = pd.to_datetime(df['ds'])
    return df

# Ajout d'un spinner pour indiquer le chargement des données
with st.spinner("Chargement des données..."):
    df = load_data()

# Interface utilisateur
st.title("Prévisions avec Prophet : Démonstration avec le dataset de Yosemite")

# Configuration des paramètres du modèle
periods = st.slider("Nombre de périodes à prévoir", min_value=1, max_value=365, value=30)
changepoint_range = st.slider("Plage des points de changement", min_value=0.01, max_value=0.99, value=0.8)

# Entraînement du modèle
m = Prophet(changepoint_range=changepoint_range)
m.fit(df[['ds', 'y']])
future = m.make_future_dataframe(periods=periods)
forecast = m.predict(future)

# Visualisation des résultats
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['ds'], y=df['y'], name='Données réelles', mode='lines', line=dict(color='blue')))
fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name='Prévisions', mode='lines', line=dict(color='red')))

# Ajout de l'intervalle de confiance
fig.add_trace(go.Scatter(
    x=forecast['ds'], y=forecast['yhat_upper'], name='Intervalle de confiance supérieur',
    line=dict(color='rgba(0, 0, 255, 0)'), fill=None
))
fig.add_trace(go.Scatter(
    x=forecast['ds'], y=forecast['yhat_lower'], name='Intervalle de confiance inférieur',
    line=dict(color='rgba(0, 0, 255, 0)'), fill='tonexty',
    fillcolor='rgba(0, 0, 255, 0.2)'
))

fig.update_layout(title="Prévisions pour y", xaxis_title="Date", yaxis_title='y')
st.plotly_chart(fig)

# Correction : récupération correcte de la figure Prophet
fig2 = m.plot_components(forecast)
st.pyplot(fig2)  # Affiche correctement les composantes