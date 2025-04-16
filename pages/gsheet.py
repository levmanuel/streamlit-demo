import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("📄 Données Google Sheet")
st.write("Cette page affiche les données d'une feuille Google Sheets et permet d'ajouter une nouvelle ligne.")
# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read()

st.write("Data from Google Sheets:")
if st.button("🔄 Mettre à jour les données"):
    df = conn.read()
    st.success("Tableau mis à jour avec succès ✅")
    st.dataframe(df)

# Ajouter une ligne via un formulaire
with st.form("add_row_form"):
    name = st.text_input("Nom")
    pet = st.text_input("Animal")
    submitted = st.form_submit_button("Ajouter")

    if submitted:
        new_row = pd.DataFrame([{"name": name, "pet": pet}])
        df = pd.concat([df, new_row], ignore_index=True)
        conn.update(worksheet="Feuille 1", data=df)
        st.success("Ligne ajoutée avec succès ✅")