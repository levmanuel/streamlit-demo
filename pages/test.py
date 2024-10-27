import streamlit as st

# Afficher le type de st.secrets pour vérifier qu'il est un dictionnaire
st.write(type(st.secrets))

# Vérifier le contenu de st.secrets
st.write(st.secrets)

# Accéder aux informations d'identification
gcp_credentials = st.secrets["gcp_service_account"]
sheet_key = st.secrets["secrets"]["sheet_key"]

st.write(type(gcp_credentials))  # Vérifiez si c'est bien un dictionnaire
st.write(gcp_credentials)