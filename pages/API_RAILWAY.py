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

    # Quelques exemples de champs
    mean_radius = st.number_input("mean_radius", value=14.2)
    mean_texture = st.number_input("mean_texture", value=20.5)
    mean_perimeter = st.number_input("mean_perimeter", value=92.5)
    mean_area = st.number_input("mean_area", value=600.0)
    mean_smoothness = st.number_input("mean_smoothness", value=0.1)
    worst_fractal_dimension = st.number_input("worst_fractal_dimension", value=0.08)

    submitted = st.form_submit_button("Envoyer la prédiction")
    if submitted:
        # Construire les données à envoyer
        input_data = {
            "mean_radius": mean_radius,
            "mean_texture": mean_texture,
            "mean_perimeter": mean_perimeter,
            "mean_area": mean_area,
            "mean_smoothness": mean_smoothness,
            "mean_compactness": 0.15,
            "mean_concavity": 0.12,
            "mean_concave_points": 0.08,
            "mean_symmetry": 0.2,
            "mean_fractal_dimension": 0.06,
            "radius_error": 0.5,
            "texture_error": 1.0,
            "perimeter_error": 3.0,
            "area_error": 40.0,
            "smoothness_error": 0.005,
            "compactness_error": 0.02,
            "concavity_error": 0.015,
            "concave_points_error": 0.01,
            "symmetry_error": 0.02,
            "fractal_dimension_error": 0.003,
            "worst_radius": 17.0,
            "worst_texture": 27.0,
            "worst_perimeter": 115.0,
            "worst_area": 950.0,
            "worst_smoothness": 0.13,
            "worst_compactness": 0.3,
            "worst_concavity": 0.2,
            "worst_concave_points": 0.15,
            "worst_symmetry": 0.28,
            "worst_fractal_dimension": worst_fractal_dimension
        }

        try:
            r = requests.post(f"{API_URL}/predict", headers=headers, json=input_data, timeout=15)
            st.success("Réponse :")
            st.json(r.json())
        except Exception as e:
            st.error(f"Erreur : {e}")