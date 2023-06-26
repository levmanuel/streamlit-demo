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
    value_date = st.date_input('Value Date')
    description = st.text_input(' Description')
    net_amount = st.number_input('Net Amount', value= 300_000 )
    market_value = st.number_input('Fund Market Value', value= 10_000_000 )

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

is_3_sigma = st.checkbox("3 sigmas transactions ?")
if is_3_sigma:
    is_3_sigma_0 = 1.0
    is_3_sigma_1 = 0.0
else:
    is_3_sigma_0 = 0.0
    is_3_sigma_1 = 1.0

is_similar = st.checkbox("Similar transactions ?")
if is_similar:
    is_similar_0 = 1.0
    is_similar_1 = 0.0
else:
    is_similar_0 = 0.0
    is_similar_1 = 1.0


delta =  (value_date - booking_date).days
#df["date_delta_7"] = np.where(np.abs(df["date_delta"])> 7,1,0)
#df["date_delta_30"] = np.where(np.abs(df["date_delta"])> 30,1,0)
#df['fin_semaine'] = df["Booking Date"].apply(lambda x: (x.weekday() >= 5)).astype(int)
#df['fin_mois'] = df['Booking Date'].apply(lambda x: (x.day >= calendar.monthrange(x.year, x.month)[1]-5)).astype(int)
#df['fin_trimestre'] = df['Booking Date'].apply(lambda x: (x.day >= calendar.monthrange(x.year, ((x.month-1)//3+1)*3)[1]-5)).astype(int)
#df['fin_semestre'] = df['Booking Date'].apply(lambda x: (x.day >= calendar.monthrange(x.year, ((x.month-1)//6+1)*6)[1]-5)).astype(int)
#df['fin_annee'] = df['Booking Date'].apply(lambda x: (x.month == 12 and x.day >= 26)).astype(int)
