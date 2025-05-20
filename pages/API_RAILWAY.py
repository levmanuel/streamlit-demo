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
    mean_compactness = st.number_input("mean_compactness", value=0.15)
    mean_concavity = st.number_input("mean_concavity", value=0.12)
    mean_concave_points = st.number_input("mean_concave_points", value=0.08)
    mean_symmetry = st.number_input("mean_symmetry", value=0.2)
    mean_fractal_dimension = st.number_input("mean_fractal_dimension", value=0.06)
    radius_error = st.number_input("radius_error", value=0.5)
    texture_error = st.number_input("texture_error", value=1.0)
    perimeter_error = st.number_input("perimeter_error", value=3.0)
    area_error = st.number_input("area_error", value=40.0)
    smoothness_error = st.number_input("smoothness_error", value=0.005)
    compactness_error = st.number_input("compactness_error", value=0.02)
    concavity_error = st.number_input("concavity_error", value=0.015)
    concave_points_error = st.number_input("concave_points_error", value=0.01)
    symmetry_error = st.number_input("symmetry_error", value=0.02)
    fractal_dimension_error = st.number_input("fractal_dimension_error", value=0.003)
    worst_radius = st.number_input("worst_radius", value=17.0)
    worst_texture = st.number_input("worst_texture", value=27.0)
    worst_perimeter = st.number_input("worst_perimeter", value=115.0)
    worst_area = st.number_input("worst_area", value=950.0)
    worst_smoothness = st.number_input("worst_smoothness", value=0.13)
    worst_compactness = st.number_input("worst_compactness", value=0.3)
    worst_concavity = st.number_input("worst_concavity", value=0.2)
    worst_concave_points = st.number_input("worst_concave_points", value=0.15)
    worst_symmetry = st.number_input("worst_symmetry", value=0.28)
    worst_fractal_dimension = st.number_input("worst_fractal_dimension", value=0.08)

    submitted = st.form_submit_button("Envoyer la prédiction")
    if submitted:
        input_data = {
            "mean radius": mean_radius,
            "mean texture": mean_texture,
            "mean perimeter": mean_perimeter,
            "mean area": mean_area,
            "mean smoothness": mean_smoothness,
            "mean compactness": mean_compactness,
            "mean concavity": mean_concavity,
            "mean concave_points": mean_concave_points,
            "mean symmetry": mean_symmetry,
            "mean fractal_dimension": mean_fractal_dimension,
            "radius error": radius_error,
            "texture error": texture_error,
            "perimeter error": perimeter_error,
            "area error": area_error,
            "smoothness error": smoothness_error,
            "compactness error": compactness_error,
            "concavity error": concavity_error,
            "concave points error": concave_points_error,
            "symmetry error": symmetry_error,
            "fractal dimension error": fractal_dimension_error,
            "worst radius": worst_radius,
            "worst texture": worst_texture,
            "worst perimeter": worst_perimeter,
            "worst area": worst_area,
            "worst smoothness": worst_smoothness,
            "worst compactness": worst_compactness,
            "worst concavity": worst_concavity,
            "worst concave points": worst_concave_points,
            "worst symmetry": worst_symmetry,
            "worst fractal dimension": worst_fractal_dimension
        }

        try:
            r = requests.post(f"{API_URL}/predict", headers=headers, json=input_data, timeout=15)
            st.success("Réponse :")
            st.json(r.json())
        except Exception as e:
            st.error(f"Erreur : {e}")