import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
from functools import wraps
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Cocktail:
    """Data class for cocktail information"""
    name: str
    ingredients: List[str]
    
    def matching_score(self, available_ingredients: Set[str]) -> Tuple[float, List[str], List[str]]:
        """Calculate matching score and ingredient lists"""
        ingredients_set = set(self.ingredients)
        matches = available_ingredients & ingredients_set
        missing = ingredients_set - available_ingredients
        score = (len(matches) / len(ingredients_set)) * 100
        return score, list(matches), list(missing)

def handle_google_errors(func):
    """Decorator to handle Google Sheets API errors"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            st.error(f"Operation failed: {str(e)}")
            return None
    return wrapper

@st.cache_resource
def get_google_client() -> gspread.Client:
    """Initialize and cache Google Sheets client"""
    if "gcp_service_account" not in st.secrets:
        raise ValueError("Google Sheets credentials not configured!")
        
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ],
    )
    return gspread.authorize(credentials)

class GoogleSheetsManager:
    def __init__(self, sheet_key: str):
        self.client = get_google_client()
        self.sheet_key = sheet_key
        
    @handle_google_errors
    def get_worksheet(self, name: str) -> Optional[gspread.Worksheet]:
        """Get worksheet by name"""
        return self.client.open_by_key(self.sheet_key).worksheet(name)

class Bar(GoogleSheetsManager):
    def __init__(self, sheet_key: str):
        super().__init__(sheet_key)
        self.worksheet_name = "ingredients"

    @handle_google_errors
    def get_ingredients(self) -> Set[str]:
        """Get bar ingredients from Google Sheets"""
        worksheet = self.get_worksheet(self.worksheet_name)
        if worksheet:
            # Skip the header row and get all ingredients
            all_values = worksheet.get_all_values()
            # Skip first row (header) and get only first column
            ingredients = [row[0] for row in all_values[1:] if row and row[0]]
            return {ing.lower().strip() for ing in ingredients}
        return set()

    @handle_google_errors
    def add_ingredient(self, ingredient: str) -> bool:
        """Add ingredient to bar"""
        if not ingredient:
            return False
            
        worksheet = self.get_worksheet(self.worksheet_name)
        if not worksheet:
            return False
            
        ingredients = self.get_ingredients()
        if ingredient.lower().strip() not in ingredients:
            worksheet.append_row([ingredient.lower().strip()])
            return True
        return False

    @handle_google_errors
    def remove_ingredient(self, ingredient: str) -> bool:
        """Remove ingredient from bar"""
        worksheet = self.get_worksheet(self.worksheet_name)
        if worksheet:
            try:
                cell = worksheet.find(ingredient.lower().strip())
                if cell:
                    worksheet.delete_row(cell.row)
                    return True
            except gspread.exceptions.CellNotFound:
                pass
        return False

class CocktailManager(GoogleSheetsManager):
    def __init__(self, sheet_key: str):
        super().__init__(sheet_key)
        self.worksheet_name = "cocktails"

    @handle_google_errors
    def get_cocktails(self) -> List[Cocktail]:
        """Get all cocktails from Google Sheets"""
        worksheet = self.get_worksheet(self.worksheet_name)
        if not worksheet:
            return []
            
        # Get all values including headers
        all_values = worksheet.get_all_values()
        if len(all_values) < 2:  # Need at least header row and one cocktail
            return []
            
        # Skip header row
        cocktails = []
        for row in all_values[1:]:
            if len(row) >= 2 and row[0] and row[1]:  # Ensure we have both name and ingredients
                name = row[0].strip()
                # Split ingredients and clean them
                ingredients = [ing.lower().strip() for ing in row[1].split(',')]
                cocktails.append(Cocktail(name=name, ingredients=ingredients))
                
        return cocktails

    @handle_google_errors
    def add_cocktail(self, cocktail: Cocktail) -> bool:
        """Add new cocktail recipe"""
        if not cocktail.name or not cocktail.ingredients:
            return False
            
        worksheet = self.get_worksheet(self.worksheet_name)
        if worksheet:
            row = [
                cocktail.name,
                ', '.join(ing.lower().strip() for ing in cocktail.ingredients)
            ]
            worksheet.append_row(row)
            return True
        return False

    @handle_google_errors
    def remove_cocktail(self, name: str) -> bool:
        """Remove cocktail recipe"""
        worksheet = self.get_worksheet(self.worksheet_name)
        if worksheet:
            try:
                cell = worksheet.find(name)
                if cell:
                    worksheet.delete_row(cell.row)
                    return True
            except gspread.exceptions.CellNotFound:
                pass
        return False

    def find_possible_cocktails(self, available_ingredients: Set[str], threshold: float = 0) -> List[Dict]:
        """Find all possible cocktails with available ingredients"""
        cocktails = self.get_cocktails()
        results = []
        
        for cocktail in cocktails:
            score, present, missing = cocktail.matching_score(available_ingredients)
            if score >= threshold:
                results.append({
                    'nom': cocktail.name,
                    'matching': score,
                    'ingredients_presents': present,
                    'ingredients_manquants': missing,
                    'total_ingredients': len(cocktail.ingredients)
                })
        
        return sorted(results, key=lambda x: x['matching'], reverse=True)

def create_cocktail_dataframe(results: List[Dict]) -> pd.DataFrame:
    """Create a DataFrame from cocktail results"""
    return pd.DataFrame([{
        'Cocktail': r['nom'],
        'Matching (%)': f"{r['matching']:.1f}%",
        'Ingrédients présents': ', '.join(r['ingredients_presents']),
        'Ingrédients manquants': ', '.join(r['ingredients_manquants'])
    } for r in results])

def render_sidebar(bar: Bar):
    """Render sidebar UI"""
    st.sidebar.title("Gestion du Bar")
    
    # Add ingredient
    new_ingredient = st.sidebar.text_input("Nouvel ingrédient:")
    if st.sidebar.button("Ajouter au bar") and new_ingredient:
        if bar.add_ingredient(new_ingredient):
            st.sidebar.success(f"✅ {new_ingredient} ajouté au bar!")
        else:
            st.sidebar.warning("L'ingrédient existe déjà ou une erreur s'est produite.")

    # Current ingredients
    st.sidebar.subheader("Ingrédients disponibles")
    ingredients = bar.get_ingredients()
    ingredients_to_remove = st.sidebar.multiselect(
        "Sélectionner pour supprimer",
        sorted(ingredients)
    )
    
    if st.sidebar.button("Supprimer les ingrédients sélectionnés"):
        success = all(bar.remove_ingredient(ing) for ing in ingredients_to_remove)
        if success:
            st.sidebar.success("✅ Ingrédients supprimés!")
        else:
            st.sidebar.warning("Certains ingrédients n'ont pas pu être supprimés.")
            
    return ingredients

def render_main_content(cocktail_manager: CocktailManager, available_ingredients: Set[str]):
    """Render main content UI"""
    st.subheader("Cocktails possibles avec vos ingrédients")
    
    threshold = st.slider("Seuil minimum de matching (%)", 0, 100, 50)
    results = cocktail_manager.find_possible_cocktails(available_ingredients, threshold)

    if results:
        df = create_cocktail_dataframe(results)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Aucun cocktail ne correspond aux critères actuels.")

    with st.expander("Ajouter un nouveau cocktail"):
        col1, col2 = st.columns(2)
        with col1:
            new_cocktail_name = st.text_input("Nom du cocktail:")
        with col2:
            ingredients_input = st.text_input("Ingrédients (séparés par des virgules):")
        
        if st.button("Ajouter le cocktail") and new_cocktail_name and ingredients_input:
            ingredients_list = [ing.strip().lower() for ing in ingredients_input.split(',')]
            new_cocktail = Cocktail(new_cocktail_name, ingredients_list)
            if cocktail_manager.add_cocktail(new_cocktail):
                st.success(f"✅ {new_cocktail_name} ajouté à la liste des cocktails!")
            else:
                st.warning("Le cocktail n'a pas pu être ajouté.")

def main():
    st.set_page_config(page_title="Mon Bar à Cocktails", page_icon="🍸")
    st.title("🍸 Mon Bar à Cocktails")

    # Check configuration
    if 'secrets' not in st.secrets:
        st.error("La clé du Google Sheet n'est pas configurée!")
        st.stop()

    sheet_key = st.secrets["secrets"]["sheet_key"]
    bar = Bar(sheet_key)
    cocktail_manager = CocktailManager(sheet_key)

    # Render UI
    available_ingredients = render_sidebar(bar)
    render_main_content(cocktail_manager, available_ingredients)

if __name__ == "__main__":
    main()