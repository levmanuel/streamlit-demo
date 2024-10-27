import streamlit as st
import json
from pathlib import Path
import pandas as pd

class Bar:
    def __init__(self):
        self.ingredients = set()
        self.fichier_bar = Path("mon_bar.json")
        self.charger_bar()

    def charger_bar(self):
        """Charge les ingrédients du bar depuis le fichier JSON"""
        if self.fichier_bar.exists():
            with open(self.fichier_bar, 'r', encoding='utf-8') as f:
                self.ingredients = set(json.load(f))
        else:
            self.ingredients = set(["vodka", "orange(jus)", 'coca', 'menthe', 'martini', 'rhum'])
            self.sauvegarder_bar()

    def sauvegarder_bar(self):
        """Sauvegarde les ingrédients du bar dans le fichier JSON"""
        with open(self.fichier_bar, 'w', encoding='utf-8') as f:
            json.dump(list(self.ingredients), f, ensure_ascii=False, indent=2)

    def ajouter_ingredient(self, ingredient):
        """Ajoute un ingrédient au bar"""
        self.ingredients.add(ingredient.lower())
        self.sauvegarder_bar()

    def supprimer_ingredient(self, ingredient):
        """Supprime un ingrédient du bar"""
        self.ingredients.discard(ingredient.lower())
        self.sauvegarder_bar()

class CocktailFinder:
    def __init__(self):
        self.fichier_cocktails = Path("cocktails.json")
        self.charger_cocktails()

    def charger_cocktails(self):
        """Charge les recettes de cocktails depuis le fichier JSON"""
        if self.fichier_cocktails.exists():
            with open(self.fichier_cocktails, 'r', encoding='utf-8') as f:
                self.cocktails = json.load(f)
        else:
            self.cocktails = {
                'Vodka Orange': ["vodka", "orange(jus)"],
                'Vodka Martini': ["vodka", "martini"],
                'Mojito': ['menthe', 'rhum', 'sucre'],
                'Acapulco': ['tequila', 'rhum', 'ananas', 'pamplemouse'],
                'American Beauty': ['cognac', 'vermouth', 'orange', 'grenadine', 'creme menthe blanche', 'porto'],
                'Americano': ['vermouth rouge', 'campari', 'eau gazeuze'],
                'Bacardi': ['rhum doux', 'jus de citron', 'grenadine (sirop)'],
                'Bahamas': ['rhum doux', 'Southern Confort', 'jus de citron', 'banane (creme)'],
                'Bellini': ['pêche', 'champagne'],
                'Bloody Mary': ['vodka', 'jus de tomate', 'sauce worcestershire', 'tabasco', 'sel de céleri', 'branche de céleri'],
                'Blue Lagon': ['vodka', 'curaçao bleu', 'citron (jus)'],
                'Between the sheets': ['cognac', 'rhum', 'cointreau', 'orange(jus)']
            }
            self.sauvegarder_cocktails()

    def sauvegarder_cocktails(self):
        """Sauvegarde les recettes de cocktails dans le fichier JSON"""
        with open(self.fichier_cocktails, 'w', encoding='utf-8') as f:
            json.dump(self.cocktails, f, ensure_ascii=False, indent=2)

    def ajouter_cocktail(self, nom, ingredients):
        """Ajoute une nouvelle recette de cocktail"""
        self.cocktails[nom] = [ing.lower() for ing in ingredients]
        self.sauvegarder_cocktails()

    def supprimer_cocktail(self, nom):
        """Supprime une recette de cocktail"""
        if nom in self.cocktails:
            del self.cocktails[nom]
            self.sauvegarder_cocktails()

    def trouver_cocktails_possibles(self, ingredients_disponibles):
        """
        Trouve tous les cocktails réalisables avec les ingrédients disponibles
        et retourne les résultats triés par pourcentage de matching.
        """
        resultats = []
        ingredients_disponibles = set(ing.lower() for ing in ingredients_disponibles)
        
        for nom_cocktail, ingredients_requis in self.cocktails.items():
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

    # Initialisation des classes
    bar = Bar()
    finder = CocktailFinder()

    # Sidebar pour la gestion du bar
    st.sidebar.title("Gestion du Bar")
    
    # Ajout d'ingrédient
    nouvel_ingredient = st.sidebar.text_input("Nouvel ingrédient:")
    if st.sidebar.button("Ajouter au bar"):
        if nouvel_ingredient:
            bar.ajouter_ingredient(nouvel_ingredient)
            st.sidebar.success(f"✅ {nouvel_ingredient} ajouté au bar!")

    # Liste des ingrédients actuels
    st.sidebar.subheader("Ingrédients disponibles")
    ingredients_a_supprimer = st.sidebar.multiselect(
        "Sélectionner pour supprimer",
        sorted(bar.ingredients)
    )
    if st.sidebar.button("Supprimer les ingrédients sélectionnés"):
        for ing in ingredients_a_supprimer:
            bar.supprimer_ingredient(ing)
        st.sidebar.success("✅ Ingrédients supprimés!")

    # Interface principale
    st.subheader("Cocktails possibles avec vos ingrédients")
    
    # Slider pour le seuil de matching
    seuil = st.slider("Seuil minimum de matching (%)", 0, 100, 50)

    # Trouver les cocktails possibles
    resultats = finder.trouver_cocktails_possibles(bar.ingredients)

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
    st.subheader("Ajouter un nouveau cocktail")
    col1, col2 = st.columns(2)
    with col1:
        nouveau_cocktail = st.text_input("Nom du cocktail:")
    with col2:
        ingredients = st.text_input("Ingrédients (séparés par des virgules):")
    
    if st.button("Ajouter le cocktail"):
        if nouveau_cocktail and ingredients:
            ingredients_liste = [ing.strip() for ing in ingredients.split(',')]
            finder.ajouter_cocktail(nouveau_cocktail, ingredients_liste)
            st.success(f"✅ {nouveau_cocktail} ajouté à la liste des cocktails!")

if __name__ == "__main__":
    main()