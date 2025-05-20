import streamlit as st
import requests
import pandas as pd

# Configuration
st.set_page_config(page_title="RAILWAY API", layout="wide")

st.title("🔬 RAILWAY API Client")

# API URL
API_URL = st.text_input("🌐 API Base URL", "https://web-production-72fc.up.railway.app").strip("/")
API_KEY = st.text_input("🔑 API Key", "0000", type="password")

headers = {"x-api-key": API_KEY}


# --- Endpoint: / (root)
st.header("📡 GET /")
if st.button("Ping Root"):
    try:
        r = requests.get(f"{API_URL}/", timeout=10)
        st.json(r.json())
    except Exception as e:
        st.error(f"Erreur : {e}")

# --- Endpoint: /auth
st.header("🔐 GET /auth")
if st.button("Test Auth"):
    try:
        r = requests.get(f"{API_URL}/auth", headers=headers, timeout=10)
        st.json(r.json())
    except Exception as e:
        st.error(f"Erreur : {e}")

# --- Endpoint: /load_data
st.header("📂 GET /load_data")
if st.button("Charger les données CSV (head)"):
    try:
        r = requests.get(f"{API_URL}/load_data", headers=headers, timeout=10)
        df = pd.DataFrame(r.json())
        st.dataframe(df)
    except Exception as e:
        st.error(f"Erreur : {e}")

# --- Endpoint: /predict
st.header("🤖 POST /predict")

with st.form("predict_form"):
    st.write("**Saisissez les variables d'entrée**")

    sepal_length = st.sidebar.number_input("Longueur du sépale", min_value=0.0, max_value=10.0, value=5.1)
    sepal_width = st.sidebar.number_input("Largeur du sépale", min_value=0.0, max_value=10.0, value=3.5)
    petal_length = st.sidebar.number_input("Longueur du pétale", min_value=0.0, max_value=10.0, value=1.4)
    petal_width = st.sidebar.number_input("Largeur du pétale", min_value=0.0, max_value=10.0, value=0.2)

    submitted = st.form_submit_button("Envoyer la prédiction")
    if submitted:
        data = {"features": [[sepal_length, sepal_width, petal_length, petal_width]]}
        try:
            r = requests.post(f"{API_URL}/predict", headers=headers, json=data, timeout=15)
            st.success("Réponse :")
            st.json(r.json())
        except Exception as e:
            st.error(f"Erreur : {e}")