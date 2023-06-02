# Importation des bibliothèques nécessaires
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Depositary Control Data Science Project", page_icon="🐶")

st.title("Depositary Control Data Science Project")

def app():
    # Création des champs d'entrée
    st.title('Entrées de données')

    booking_date = st.date_input('Booking Date')
    st.write("Vous avez sélectionné la date de réservation: ", booking_date)

    value_date = st.date_input('Value Date')
    st.write("Vous avez sélectionné la date de valeur: ", value_date)

    description = st.text_input('Description')
    st.write("Vous avez entré la description: ", description)

    net_amount = st.number_input('Net Amount', value=0.00)
    st.write("Vous avez entré le montant net: ", net_amount)

    market_value = st.number_input('Market Value', value=0.00)
    st.write("Vous avez entré la valeur du marché: ", market_value)

    if st.button('Submit'):
        st.write("Données soumises avec succès")

if __name__ == "__main__":
    app()
