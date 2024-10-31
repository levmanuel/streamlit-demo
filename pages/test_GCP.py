import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import gspread

def load_gsheet():
    # Configurer les credentials
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ],
    )
    
    # Créer une connexion avec Google Sheets
    gc = gspread.authorize(credentials)
    
    # Ouvrir le spreadsheet par son ID
    sheet_id = st.secrets["sheet_id"]
    sh = gc.open_by_key(sheet_id)
    
    # Sélectionner la première feuille
    worksheet = sh.get_worksheet(0)
    
    # Récupérer toutes les données
    data = worksheet.get_all_records()
    
    # Convertir en DataFrame pandas
    df = pd.DataFrame(data)
    return df

def main():
    st.title("Visualisation Google Sheets")
    
    try:
        # Charger les données
        df = load_gsheet()
        
        # Afficher les données
        st.write("### Aperçu des données")
        st.dataframe(df)
        
        # Ajouter des métriques basiques
        st.write("### Statistiques")
        st.write(f"Nombre total de lignes: {len(df)}")
        
        # Si vous avez des colonnes numériques, vous pouvez afficher des statistiques
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) > 0:
            st.write("Statistiques descriptives:")
            st.write(df[numeric_cols].describe())
        
    except Exception as e:
        st.error(f"Une erreur s'est produite: {str(e)}")

if __name__ == "__main__":
    main()