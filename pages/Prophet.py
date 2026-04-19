import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from prophet import Prophet
import matplotlib.pyplot as plt


@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/facebook/prophet/main/examples/example_yosemite_temps.csv"
    df = pd.read_csv(url)
    df['ds'] = pd.to_datetime(df['ds'])
    return df


@st.cache_data
def run_prophet(changepoint_range, periods):
    df = load_data()
    m = Prophet(changepoint_range=changepoint_range)
    m.fit(df[['ds', 'y']])
    future = m.make_future_dataframe(periods=periods)
    forecast = m.predict(future)
    return df, forecast, m


with st.spinner("Chargement des données..."):
    load_data()

st.title("Prévisions avec Prophet : Démonstration avec le dataset de Yosemite")

periods = st.slider("Nombre de périodes à prévoir (jours)", min_value=1, max_value=365, value=30)
changepoint_range = st.slider(
    "Plage des points de changement",
    min_value=0.01, max_value=0.99, value=0.8,
    help="Proportion de l'historique sur laquelle Prophet cherche des inflexions de tendance. "
         "Une valeur élevée rend le modèle plus flexible mais risque le surapprentissage.",
)

with st.spinner("Entraînement du modèle..."):
    df, forecast, m = run_prophet(changepoint_range, periods)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['ds'], y=df['y'],
    name='Données réelles', mode='lines', line=dict(color='blue'),
))
fig.add_trace(go.Scatter(
    x=forecast['ds'], y=forecast['yhat'],
    name='Prévisions', mode='lines', line=dict(color='red'),
))
fig.add_trace(go.Scatter(
    x=forecast['ds'], y=forecast['yhat_upper'],
    name='Intervalle supérieur', line=dict(color='rgba(0,0,255,0)'), fill=None,
))
fig.add_trace(go.Scatter(
    x=forecast['ds'], y=forecast['yhat_lower'],
    name='Intervalle inférieur', line=dict(color='rgba(0,0,255,0)'),
    fill='tonexty', fillcolor='rgba(0,0,255,0.2)',
))
fig.update_layout(
    title="Températures à Yosemite — Prévisions Prophet",
    xaxis_title="Date",
    yaxis_title="Température (°C)",
)
st.plotly_chart(fig)

st.subheader("Composantes du modèle")
fig2 = m.plot_components(forecast)
st.pyplot(fig2)
plt.close(fig2)
