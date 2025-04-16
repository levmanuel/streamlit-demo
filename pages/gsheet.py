import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("📄 Données Google Sheet")
st.write(
    "Cette page affiche les données d'une feuille Google Sheets et permet d'ajouter une nouvelle ligne."
)
# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read()

st.write("Data from Google Sheets:")
st.dataframe(df)

# Ajouter une ligne via un formulaire
with st.form("add_row_form"):
    name = st.text_input("Nom")
    pet = st.text_input("Animal")
    submitted = st.form_submit_button("Ajouter")

    if submitted:
        # Ajouter la nouvelle ligne
        new_row = pd.DataFrame([{"name": name, "pet": pet}])
        updated_df = pd.concat([df, new_row], ignore_index=True)

        # Écrire les données mises à jour dans la feuille
        conn.update(worksheet="Feuille 1", data=updated_df)

        st.success("Ligne ajoutée avec succès ✅")