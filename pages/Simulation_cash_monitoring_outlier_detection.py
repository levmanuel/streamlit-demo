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


# Champ 'is_opp_transaction_0' et 'is_opp_transaction_1'
is_opp_transaction_0 = st.checkbox("is_opp_transaction_0")
is_opp_transaction_1 = st.checkbox("is_opp_transaction_1")

# Champ 'is_3_sigma_0' et 'is_3_sigma_1'
is_3_sigma_0 = st.checkbox("is_3_sigma_0")
is_3_sigma_1 = st.checkbox("is_3_sigma_1")

# Champ 'date_delta_7_0' et 'date_delta_7_1'
date_delta_7_0 = st.checkbox("date_delta_7_0")
date_delta_7_1 = st.checkbox("date_delta_7_1")

# Champ 'date_delta_30_0' et 'date_delta_30_1'
date_delta_30_0 = st.checkbox("date_delta_30_0")
date_delta_30_1 = st.checkbox("date_delta_30_1")

# Champ 'fin_semaine_0' et 'fin_semaine_1'
fin_semaine_0 = st.checkbox("fin_semaine_0")
fin_semaine_1 = st.checkbox("fin_semaine_1")

# Champ 'fin_mois_0' et 'fin_mois_1'
fin_mois_0 = st.checkbox("fin_mois_0")
fin_mois_1 = st.checkbox("fin_mois_1")

# Champ 'fin_trimestre_0' et 'fin_trimestre_1'
fin_trimestre_0 = st.checkbox("fin_trimestre_0")
fin_trimestre_1 = st.checkbox("fin_trimestre_1")

# Champ 'fin_semestre_0' et 'fin_semestre_1'
fin_semestre_0 = st.checkbox("fin_semestre_0")
fin_semestre_1 = st.checkbox("fin_semestre_1")

# Champ 'fin_annee_0' et 'fin_annee_1'
fin_annee_0 = st.checkbox("fin_annee_0")
fin_annee_1 = st.checkbox("fin_annee_1")

# Champ 'is_similar_0' et 'is_similar_1'
is_similar_0 = st.checkbox("is_similar_0")
is_similar_1 = st.checkbox("is_similar_1")

# Champ 'has_bad_word'
has_bad_word = st.checkbox("has_bad_word")

# Champ: deal_type_0, deal_type_1, deal_type_2, deal_type_3, deal_type_4, deal_type_5
deal_types = ['deal_type_0', 'deal_type_1', 'deal_type_2', 'deal_type_3', 'deal_type_4', 'deal_type_5']
selected_deal_type = st.selectbox("Select Deal Type", deal_types)
