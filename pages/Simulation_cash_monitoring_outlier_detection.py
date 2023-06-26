# Importation des bibliothèques nécessaires
import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta

st.set_page_config(page_title="cas Monitoring Outlier Detection", page_icon="🐶")
st.title("Depositary Control Data Science Project")

col1, col2 = st.columns(2)
with col1:
    
    st.write("Transaction Input")
    booking_date = st.date_input('Booking Date')
    #st.write("Vous avez sélectionné la date de réservation: ", booking_date)

    value_date = st.date_input('Value Date')
    #st.write("Vous avez sélectionné la date de valeur: ", value_date)

    description = st.text_input(' Description')
    #st.write("Vous avez entré la description: ", description)

    net_amount = st.number_input('Net Amount', value= 300_000 )
    #st.write("Vous avez entré le montant net: ", net_amount)

    market_value = st.number_input('Fund Market Value', value= 10_000_000 )
    #st.write("Vous avez entré la valeur du marché: ", market_value)


with col2:
    st.write("Transaction Summary")
    data_dict = {'Booking Date': [booking_date], 'Value Date': [value_date], 
                 'Description': [description], 'net_amount': [net_amount], "market_value": [market_value]}
    df = pd.DataFrame(data_dict)
    df["NAV_pct"] = 100 * df["net_amount"] / df["market_value"]
    st.dataframe(df.transpose())

if st.button('Submit'):
    st.write("Données soumises avec succès")

is_opp_transaction = st.checkbox("Opposite Transaction ?")
if is_opp_transaction:
    is_opp_transaction_0 = 1.0
    is_opp_transaction_1 = 0.0
else:
    is_opp_transaction_0 = 0.0
    is_opp_transaction_1 = 1.0

is_3_sigma_0 = st.checkbox("3 sigmas transactions ?")
if is_3_sigma:
    is_3_sigma_0 = 1.0
    is_3_sigma_1 = 0.0
else:
    is_3_sigma_0 = 0.0
    is_3_sigma_1 = 1.0
