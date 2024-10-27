import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from typing import List, Dict, Set

# Configuration des credentials Google Sheets
@st.cache_resource
def get_google_client():
    # Création des credentials à partir des secrets Streamlit
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ],
    )
    return gspread.authorize(credentials)

class Bar:
    def __init__(self, sheet_key: str):
        self.client = get_google_client()
        self.sheet_key = sheet_key
        self.worksheet_name = "ingredients"

    def get_ingredients(self) -> Set[str]:
        """Récupère les ingrédients du bar depuis Google Sheets"""
        try:
            sheet = self.client.open_by_key(self.sheet_key).worksheet(self.worksheet_name)
            ingredients = sheet.col_values(1)  # Première colonne
            return set(ing.lower() for ing in ingredients if ing)
        except Exception as e:
            st.error(f"Erreur lors de la lecture des ingrédients: {str(e)}")
            return set()

    def ajouter_ingredient(self, ingredient: str):
        """Ajoute un ingrédient au bar"""
        if not ingredient:
            return
            
        try:
            sheet = self.client.open_by_key(self.sheet_key).worksheet(self.worksheet_name)
            ingredients = set(ing.lower() for ing in sheet.col_values(1))
            
            if ingredient.lower() not in ingredients:
                sheet.append_row([ingredient.lower()])
                return True
        except Exception as e:
            st.error(f"Erreur lors de l'ajout de l'ingrédient: {str(e)}")
        return False

    def supprimer_ingredient(self, ingredient: str):
        """Supprime un ingrédient du bar"""
        try:
            sheet = self.client.open_by_key(self.sheet_key).worksheet(self.worksheet_name)
            cell = sheet.find(ingredient.lower())
            if cell:
                sheet.delete_row(cell.row)
                return True
        except Exception as e:
            st.error(f"Erreur lors de la suppression de l'ingrédient: {str(e)}")
        return False

class CocktailFinder:
    def __init__(self, sheet_key: str):
        self.client = get_google_client()
        self.sheet_key = sheet_key
        self.worksheet_name = "cocktails"

    def get_cocktails(self) -> Dict[str, List[str]]:
        """Récupère tous les cocktails depuis Google Sheets"""
        try:
            sheet = self.client.open_by_key(self.sheet_key).worksheet(self.worksheet_name)
            data = sheet.get_all_records()
            
            cocktails = {}
            for row in data:
                nom = row['nom']
                ingredients = [ing.strip().lower() for ing in row['ingredients'].split(',')]
                cocktails[nom] = ingredients
                
            return cocktails
        except Exception as e:
            st.error(f"Erreur lors de la lecture des cocktails: {str(e)}")
            return {}

    def ajouter_cocktail(self, nom: str, ingredients: List[str]):
        """Ajoute une nouvelle recette de cocktail"""
        if not nom or not ingredients:
            return False
            
        try:
            sheet = self.client.open_by_key(self.sheet_key).worksheet(self.worksheet_name)
            ingredients_str = ', '.join(ing.lower() for ing in ingredients)
            sheet.append_row([nom, ingredients_str])
            return True
        except Exception as e:
            st.error(f"Erreur lors de l'ajout du cocktail: {str(e)}")
        return False

    def supprimer_cocktail(self, nom: str):
        """Supprime une recette de cocktail"""
        try:
            sheet = self.client.open_by_key(self.sheet_key).worksheet(self.worksheet_name)
            cell = sheet.find(nom)
            if cell:
                sheet.delete_row(cell.row)
                return True
        except Exception as e:
            st.error(f"Erreur lors de la suppression du cocktail: {str(e)}")
        return False

    def trouver_cocktails_possibles(self, ingredients_disponibles: Set[str]) -> List[Dict]:
        """
        Trouve tous les cocktails réalisables avec les ingrédients disponibles
        """
        resultats = []
        cocktails = self.get_cocktails()
        
        for nom_cocktail, ingredients_requis in cocktails.items():
            ingredients_matches = ingredients_disponibles & set(ingredients_requis)
            pct_matching = (len(ingredients_matches) / len(ingredients_requis)) * 100
            
            resultats.append({
                'nom': nom_cocktail,
                'matching': pct_matching,
                'ingredients_presents': list(ingredients_matches),
                'ingredients_manquants': list(set(ingredients_requis) - ingredients_matches),
                'total_ingredients': len(ingredients_requis)
            })
        
        return sorted(resultats, key=lambda x: x['matching'], reverse=True)

def main():
    st.set_page_config(page_title="Mon Bar à Cocktails", page_icon="🍸")
    st.title("🍸 Mon Bar à Cocktails")

    # st.text(st.secrets["gcp_service_account"])

    # Vérifier que les secrets sont configurés
    if 'gcp_service_account' not in st.secrets:
        st.error("Les credentials Google Sheets ne sont pas configurés!")
        st.stop()
    if 'secrets' not in st.secrets:
        st.error("La clé du Google Sheet n'est pas configurée!")
        st.stop()

    # Initialisation des classes
    sheet_key = st.secrets["secrets"]["sheet_key"]

    bar = Bar(sheet_key)
    finder = CocktailFinder(sheet_key)

    # Sidebar pour la gestion du bar
    st.sidebar.title("Gestion du Bar")
    
    # Ajout d'ingrédient
    nouvel_ingredient = st.sidebar.text_input("Nouvel ingrédient:")
    if st.sidebar.button("Ajouter au bar"):
        if nouvel_ingredient:
            if bar.ajouter_ingredient(nouvel_ingredient):
                st.sidebar.success(f"✅ {nouvel_ingredient} ajouté au bar!")
            else:
                st.sidebar.warning("L'ingrédient existe déjà ou une erreur s'est produite.")

    # Liste des ingrédients actuels
    st.sidebar.subheader("Ingrédients disponibles")
    ingredients = bar.get_ingredients()
    ingredients_a_supprimer = st.sidebar.multiselect(
        "Sélectionner pour supprimer",
        sorted(ingredients)
    )
    if st.sidebar.button("Supprimer les ingrédients sélectionnés"):
        success = True
        for ing in ingredients_a_supprimer:
            if not bar.supprimer_ingredient(ing):
                success = False
        if success:
            st.sidebar.success("✅ Ingrédients supprimés!")
        else:
            st.sidebar.warning("Certains ingrédients n'ont pas pu être supprimés.")

    # Interface principale
    st.subheader("Cocktails possibles avec vos ingrédients")
    
    # Slider pour le seuil de matching
    seuil = st.slider("Seuil minimum de matching (%)", 0, 100, 50)

    # Trouver les cocktails possibles
    resultats = finder.trouver_cocktails_possibles(ingredients)

    # Afficher les résultats dans un DataFrame
    cocktails_df = []
    for r in resultats:
        if r['matching'] >= seuil:
            cocktails_df.append({
                'Cocktail': r['nom'],
                'Matching (%)': f"{r['matching']:.1f}%",
                'Ingrédients présents': ', '.join(r['ingredients_presents']),
                'Ingrédients manquants': ', '.join(r['ingredients_manquants'])
            })

    if cocktails_df:
        df = pd.DataFrame(cocktails_df)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Aucun cocktail ne correspond aux critères actuels.")

    # Section pour ajouter un nouveau cocktail
    with st.expander("Ajouter un nouveau cocktail"):
        col1, col2 = st.columns(2)
        with col1:
            nouveau_cocktail = st.text_input("Nom du cocktail:")
        with col2:
            ingredients = st.text_input("Ingrédients (séparés par des virgules):")
        
        if st.button("Ajouter le cocktail"):
            if nouveau_cocktail and ingredients:
                ingredients_liste = [ing.strip() for ing in ingredients.split(',')]
                if finder.ajouter_cocktail(nouveau_cocktail, ingredients_liste):
                    st.success(f"✅ {nouveau_cocktail} ajouté à la liste des cocktails!")
                else:
                    st.warning("Le cocktail n'a pas pu être ajouté.")

if __name__ == "__main__":
    main()