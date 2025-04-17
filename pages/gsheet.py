import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px


st.title("📄 Données Google Sheet")
st.write("Cette page affiche les données d'une feuille Google Sheets.")
st.markdown('`GOOGLEFINANCE("TSLA"; "price";TODAY()-90;TODAY())`')
# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

# Initialiser le dataframe dans session_state si pas déjà présent
if "df" not in st.session_state:
    st.session_state.df = conn.read(worksheet="Feuille 1")
# Bouton de mise à jour
if st.button("🔄 Mettre à jour les données"):
    st.session_state.df = conn.read(worksheet="Feuille 1", ttl=0)
    st.success("Tableau mis à jour depuis la Google Sheet ✅")

df = st.session_state.df.copy()

# Afficher les données
col = st.columns([0.3, 0.7]) # Donner un peu plus de largeur au graphique
with col[0]:
    st.subheader("Données Google Sheet")
    st.dataframe(df, use_container_width=True)
with col[1]:
    st.subheader("Chart")
    st.plotly_chart(px.line(df, x="Date", y="Close", title="Prix de l'action Tesla"))



# # Ajouter une ligne via un formulaire
# with st.form("add_row_form"):
#     name = st.text_input("Nom")
#     pet = st.text_input("Animal")
#     submitted = st.form_submit_button("Ajouter")

# if submitted:
#     new_row = pd.DataFrame([{"name": name, "pet": pet}])
#     st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
#     conn.update(worksheet="Feuille 1", data=st.session_state.df)
#     st.success("Ligne ajoutée avec succès ✅")