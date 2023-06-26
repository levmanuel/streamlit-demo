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

####Function

def assign_value(row):
    date = row['Value Date']
    amount = row['net_amount_fx']
    client = row['Client Name']
    opposite_amount_exists = df[(df['Value Date'] == date) & (df['net_amount_fx'] == -amount) & (df['Client Name'] == client)].shape[0] > 0
    if opposite_amount_exists:
        return 1
    else:
        return 0
df['is_opp_transaction'] = df.apply(assign_value, axis=1)

df_mean = df.groupby(['Client Name', 'Swift Classification'])['net_amount_fx_abs'].mean().reset_index()
df_std = df.groupby(['Client Name', 'Swift Classification'])['net_amount_fx_abs'].std().reset_index()
df_mean_std = pd.merge(df_mean, df_std, on=['Client Name', 'Swift Classification'], suffixes=('_mean', '_std'))
# Montant aberrant
df = pd.merge(df, df_mean_std, on=['Client Name', 'Swift Classification'], how='left')
df['is_3_sigma'] = np.where(abs(df['net_amount_fx_abs'] - df['net_amount_fx_abs_mean']) > 3 * df['net_amount_fx_abs_std'], 1, 0)

df["date_delta"] =  (df["Value Date"] - df["Booking Date"]).dt.days
df["date_delta_7"] = np.where(np.abs(df["date_delta"])> 7,1,0)
df["date_delta_30"] = np.where(np.abs(df["date_delta"])> 30,1,0)
df['fin_semaine'] = df["Booking Date"].apply(lambda x: (x.weekday() >= 5)).astype(int)
df['fin_mois'] = df['Booking Date'].apply(lambda x: (x.day >= calendar.monthrange(x.year, x.month)[1]-5)).astype(int)
df['fin_trimestre'] = df['Booking Date'].apply(lambda x: (x.day >= calendar.monthrange(x.year, ((x.month-1)//3+1)*3)[1]-5)).astype(int)
df['fin_semestre'] = df['Booking Date'].apply(lambda x: (x.day >= calendar.monthrange(x.year, ((x.month-1)//6+1)*6)[1]-5)).astype(int)
df['fin_annee'] = df['Booking Date'].apply(lambda x: (x.month == 12 and x.day >= 26)).astype(int)

def detect_similar_transactions(df):
    # Tri du dataframe par date
    df = df.sort_values(by=['Booking Date', 'Client Name'])
    df['Similar Transaction Last Day'] = 0
    # Boucle sur les transactions à partir de la deuxième pour détecter les transactions similaires de la veille
    for i in range(1, len(df)):
        if df.loc[i, 'Booking Date'] - df.loc[i-1, 'Booking Date'] == pd.Timedelta(days=1):
            if df.loc[i, 'net_amount_fx_abs'] == df.loc[i-1, 'net_amount_fx_abs']:
                df.loc[i, 'Similar Transaction Last Day'] = 1
    return df

df = detect_similar_transactions(df).sort_index()

df = df.join(pd.get_dummies(df["is_opp_transaction"], prefix="is_opp_transaction"))
df = df.join(pd.get_dummies(df["is_3_sigma"], prefix="is_3_sigma"))
df = df.join(pd.get_dummies(df["date_delta_7"], prefix="date_delta_7"))
df = df.join(pd.get_dummies(df["date_delta_30"], prefix="date_delta_30"))
df = df.join(pd.get_dummies(df["fin_semaine"], prefix="fin_semaine"))
df = df.join(pd.get_dummies(df["fin_mois"], prefix="fin_mois"))
df = df.join(pd.get_dummies(df["fin_trimestre"], prefix="fin_trimestre"))
df = df.join(pd.get_dummies(df["fin_semestre"], prefix="fin_semestre"))
df = df.join(pd.get_dummies(df["fin_annee"], prefix="fin_annee"))
df = df.join(pd.get_dummies(df["Similar Transaction Last Day"], prefix="is_similar"))

df = df.drop(columns=['Client Name', 'Currency', 'Booking Date', 'Value Date', 'Description',
       'net_amount', 'Swift Classification', 'FX_Rate',
       'net_amount_fx_abs', 'Market value', 'amount_bin',
       'is_opp_transaction', 'net_amount_fx_abs_mean', 'net_amount_fx_abs_std',
       'is_3_sigma', 'date_delta', 'date_delta_7', 'date_delta_30',
       'fin_semaine', 'fin_mois', 'fin_trimestre', 'fin_semestre', 'fin_annee',
       'Similar Transaction Last Day'])
