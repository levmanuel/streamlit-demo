import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("📄 Données Google Sheet")
st.write("Cette page affiche les données d'une feuille Google Sheets et permet d'ajouter une nouvelle ligne.")

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

# Initialiser le dataframe dans session_state si pas déjà présent
if "df" not in st.session_state:
    st.session_state.df = conn.read(worksheet="Feuille 1")

# Bouton de mise à jour
if st.button("🔄 Mettre à jour les données"):
    # Lecture directe des données mises à jour depuis Google Sheets
    st.session_state.df = conn.read(worksheet="Feuille 1", ttl=0)
    st.success("Tableau mis à jour depuis la Google Sheet ✅")
    # Ne pas utiliser st.experimental_rerun() ici

# Afficher les données
st.write("Data from Google Sheets:")
st.dataframe(st.session_state.df)

# Ajouter une ligne via un formulaire
with st.form("add_row_form"):
    name = st.text_input("Nom")
    pet = st.text_input("Animal")
    submitted = st.form_submit_button("Ajouter")

if submitted:
    new_row = pd.DataFrame([{"name": name, "pet": pet}])
    st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
    conn.update(worksheet="Feuille 1", data=st.session_state.df)
    st.success("Ligne ajoutée avec succès ✅")