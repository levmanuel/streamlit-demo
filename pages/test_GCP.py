import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

def connect_to_gspread():
    try:
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ],
        )
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"Erreur de connexion: {str(e)}")
        return None

def load_gsheet_data():
    # Établir la connexion
    gc = connect_to_gspread()
    if gc is None:
        return None
        
    try:
        # Ouvrir le spreadsheet
        sheet_key = st.secrets["secrets"]["sheet_key"]
        sh = gc.open_by_key(sheet_key)
        
        # Récupérer la première feuille par défaut
        worksheet = sh.sheet1  # Utilisation de sheet1 au lieu de get_worksheet(0)
        
        # Récupérer les données
        values = worksheet.get_all_values()  # Utiliser get_all_values() au lieu de get_all_records()
        
        if not values:
            st.warning("La feuille est vide")
            return None
            
        # La première ligne contient les en-têtes
        headers = values[0]
        data = values[1:]
        
        # Créer le DataFrame
        df = pd.DataFrame(data, columns=headers)
        return df
        
    except gspread.exceptions.SpreadsheetNotFound:
        st.error("Feuille de calcul non trouvée. Vérifiez la clé du document.")
        return None
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")
        return None

def main():
    st.title("Données Google Sheets")
    
    # Charger les données
    df = load_gsheet_data()
    
    if df is not None:
        # Afficher les dimensions du DataFrame
        st.write(f"Dimensions: {df.shape[0]} lignes × {df.shape[1]} colonnes")
        
        # Afficher les données brutes
        st.write("### Données brutes")
        st.write(df)  # Utiliser st.write au lieu de st.dataframe pour le débogage
        
        # Ajouter des filtres simples si le DataFrame n'est pas vide
        if not df.empty:
            st.write("### Filtres")
            col_to_filter = st.selectbox(
                "Filtrer par colonne:",
                df.columns.tolist()
            )
            
            try:
                # Créer un filtre basé sur le type de données
                if pd.to_numeric(df[col_to_filter], errors='coerce').notnull().all():
                    # Colonne numérique
                    min_val = float(df[col_to_filter].astype(float).min())
                    max_val = float(df[col_to_filter].astype(float).max())
                    filter_val = st.slider(
                        f"Valeur minimale pour {col_to_filter}",
                        min_val, max_val, min_val
                    )
                    filtered_df = df[df[col_to_filter].astype(float) >= filter_val]
                else:
                    # Colonne textuelle
                    unique_vals = df[col_to_filter].unique().tolist()
                    selected_val = st.multiselect(
                        f"Sélectionner les valeurs pour {col_to_filter}",
                        unique_vals,
                        default=unique_vals[:1]  # Sélectionner la première valeur par défaut
                    )
                    filtered_df = df[df[col_to_filter].isin(selected_val)]
                
                st.write("### Données filtrées")
                st.write(filtered_df)
                
            except Exception as e:
                st.error(f"Erreur lors du filtrage: {str(e)}")

if __name__ == "__main__":
    main()