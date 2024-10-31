import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# Vérifier que les secrets sont configurés
if 'gcp_service_account' not in st.secrets:
    st.error("Les credentials Google Sheets ne sont pas configurés!")
    st.stop()
if 'secrets' not in st.secrets:
    st.error("La clé du Google Sheet n'est pas configurée!")
    st.stop()

# Fonction pour charger les données de Google Sheets
def load_data_from_gsheet():
    # Charger les credentials depuis st.secrets
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
    
    # Ouvrir le Google Sheet
    client = gspread.authorize(creds)
    sheet = client.open_by_key(st.secrets["secrets"]["sheet_id"])
    worksheet = sheet.get_worksheet(0)  # Première feuille du Google Sheet
    
    # Charger les données dans un DataFrame
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    return df

# Titre de la page
st.title("Affichage des données d'un Google Sheet dans Streamlit")

# Charger les données
df = load_data_from_gsheet()

# Afficher les données dans Streamlit
st.write(df)