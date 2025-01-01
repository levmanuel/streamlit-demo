import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from prophet import Prophet

# Charger le dataset de Yosemite
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/facebook/prophet/main/examples/example_yosemite_temps.csv"
    df = pd.read_csv(url)
    df['ds'] = pd.to_datetime(df['ds'])
    return df

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
fig.add_trace(go.Scatter(x=df['ds'], y=df['y'], name='Données réelles'))
fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name='Prévisions'))
fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], name='Intervalle de confiance supérieur', mode='lines', line=dict(color='rgba(0, 0, 255, 0.2)', dash='dash')))
fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], name='Intervalle de confiance inférieur', mode='lines', line=dict(color='rgba(0, 0, 255, 0.2)', dash='dash')))
fig.update_layout(title="Prévisions pour {}".format('y'), xaxis_title="Date", yaxis_title='y')
st.plotly_chart(fig)

# Composantes du modèle
fig2 = m.plot_components(forecast)
st.plotly_chart(fig2)