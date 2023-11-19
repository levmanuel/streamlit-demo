import folium
import streamlit as st
import pandas as pd
from streamlit_folium import st_folium

# Configuration de la page Streamlit
st.set_page_config(page_title="Voyages en Europe", page_icon="✈️")

st.title("Voyages en Europe ✈️")
st.write("Planificateur de voyage")

# Création d'un DataFrame avec une liste de villes européennes et leurs coordonnées
villes_europe = pd.DataFrame({
    "Ville": ["Paris", "Berlin", "Rome", "Madrid", "Londres"],
    "Coordonnées": [[48.8566, 2.3522], [52.5200, 13.4050], [41.9028, 12.4964], [40.4168, -3.7038], [51.5074, -0.1278]]
})

# Liste déroulante pour choisir une ville
selected_city = st.selectbox("Choisissez une ville :", villes_europe["Ville"])

# Trouver les coordonnées de la ville sélectionnée
city_data = villes_europe[villes_europe["Ville"] == selected_city]
city_coor = city_data.iloc[0]['Coordonnées']

# Création et mise à jour de la carte
m = folium.Map(location=city_coor, zoom_start=5)
for _, city in villes_europe.iterrows():
    folium.Marker(location=city['Coordonnées'], popup=city['Ville'], tooltip=city['Ville']).add_to(m)

# Affichage de la carte dans Streamlit
st_data = st_folium(m, width=700, height=500)

# Affichage du DataFrame
st.write("Liste des villes en Europe :")
st.dataframe(villes_europe)
