import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

def connect_to_gspread():
    # Configurer les credentials
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ],
    )
    
    # Se connecter à Google Sheets
    return gspread.authorize(credentials)

def load_gsheet_data():
    # Établir la connexion
    gc = connect_to_gspread()
    
    # Ouvrir le spreadsheet
    sheet_id = st.secrets["sheet_key"]
    sh = gc.open_by_key(sheet_id)
    
    # Récupérer la liste des feuilles
    worksheet_list = sh.worksheets()
    
    # Créer un sélecteur de feuilles
    worksheet_names = [ws.title for ws in worksheet_list]
    selected_worksheet = st.selectbox("Sélectionner une feuille:", worksheet_names)
    
    # Récupérer la feuille sélectionnée
    worksheet = sh.worksheet(selected_worksheet)
    
    # Récupérer les données
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

def main():
    st.title("Données Google Sheets")
    
    try:
        # Charger les données
        df = load_gsheet_data()
        
        # Afficher les dimensions du DataFrame
        st.write(f"Dimensions: {df.shape[0]} lignes × {df.shape[1]} colonnes")
        
        # Afficher les données
        st.write("### Données")
        st.dataframe(df)
        
        # Ajouter des filtres simples si le DataFrame n'est pas vide
        if not df.empty:
            st.write("### Filtres")
            # Permettre la sélection de colonnes pour le filtrage
            col_to_filter = st.selectbox(
                "Filtrer par colonne:",
                df.columns.tolist()
            )
            
            # Créer un filtre basé sur le type de données
            if df[col_to_filter].dtype in ['int64', 'float64']:
                min_val = float(df[col_to_filter].min())
                max_val = float(df[col_to_filter].max())
                filter_val = st.slider(
                    f"Valeur minimale pour {col_to_filter}",
                    min_val, max_val, min_val
                )
                filtered_df = df[df[col_to_filter] >= filter_val]
            else:
                # Pour les colonnes textuelles
                unique_vals = df[col_to_filter].unique().tolist()
                selected_val = st.multiselect(
                    f"Sélectionner les valeurs pour {col_to_filter}",
                    unique_vals,
                    default=unique_vals
                )
                filtered_df = df[df[col_to_filter].isin(selected_val)]
            
            st.write("### Données filtrées")
            st.dataframe(filtered_df)
            
    except Exception as e:
        st.error(f"Une erreur s'est produite: {str(e)}")

if __name__ == "__main__":
    main()