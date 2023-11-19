import folium
import streamlit as st
import pandas as pd
from streamlit_folium import st_folium

# Configuration de la page Streamlit
st.set_page_config(page_title="Voyages en Europe", page_icon="✈️")

st.title("Voyages en Europe ✈️")
st.write("Planificateur de voyage")

# Chargement des données des villes
villes_europe = pd.read_csv("villes_europe.csv")

# Initialisation de la liste des villes sélectionnées
selected_cities = []

# Widget pour ajouter des villes
with st.form(key='city_form'):
    city = st.selectbox("Ajoutez une ville :", villes_europe["Ville"])
    submit_button = st.form_submit_button(label='Ajouter cette ville')

if submit_button:
    selected_cities.append(city)

# Affichage de la liste des villes sélectionnées
st.write("Villes sélectionnées :", ', '.join(selected_cities))

# Création de la carte
m = folium.Map(location=[48.8566, 2.3522], zoom_start=4) # Paris comme point de départ

# Ajout des marqueurs et tracé des lignes
for i, city in enumerate(selected_cities):
    city_coord = villes_europe[villes_europe["Ville"] == city].iloc[0]['Coordonnées']
    folium.Marker(city_coord, popup=city, tooltip=city).add_to(m)
    if i > 0:
        previous_city_coord = villes_europe[villes_europe["Ville"] == selected_cities[i-1]].iloc[0]['Coordonnées']
        folium.PolyLine([previous_city_coord, city_coord], color="red", weight=2.5, opacity=1).add_to(m)

# Affichage de la carte dans Streamlit
st_data = st_folium(m, width=700, height=500)
