# Importation des bibliothèques nécessaires
import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta
import calendar
from dateutil.relativedelta import relativedelta
import re
import seaborn as sns
import random
import matplotlib.pyplot as plt
from collections import Counter
from tqdm import tqdm
import string
import file_upload as X
import models
import pickle
from sklearn.neighbors import KNeighborsClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import IsolationForest
import shap

st.set_page_config(page_title="Cash Monitoring Outlier Detection", page_icon="🐶", layout="wide")
st.title("Depositary Control Data Science Project")

col1, col2 = st.columns(2)
with col1:
    st.write("Transaction Input")
    booking_date = st.date_input('Booking Date')
    value_date = st.date_input('Value Date')
    description = st.text_input('Description', value="110-Ext.Ref: Our Ref: INT002667762PRC Transfer of EUR 676.90 in favour of FUND INVESTMENTS - FEES MONEY-210119")
    is_anomaly_in_custer = st.checkbox("Anomaly in Cluster ?")
    net_amount = st.slider('Transaction Amount', 0, 30_000_000, 100_000, step=100_000)
    market_value = st.slider('Fund Market Value', 0, 300_000_000, 10_000_000, step=100_000)
    date_delta =  (value_date - booking_date).days
    date_delta_7 = np.where(np.abs(date_delta)> 7,1,0)
    date_delta_30 = np.where(np.abs(date_delta)> 30,1,0)
    fin_semaine = booking_date.weekday() >= 5
    last_day = calendar.monthrange(booking_date.year, booking_date.month)[1]
    fin_mois = booking_date.day >= last_day - 5
    last_day_of_quarter = booking_date + relativedelta(day=31, months=((booking_date.month-1)//3+1)*3)
    fin_trimestre = booking_date.day >= last_day_of_quarter.day - 5
    semester_end_month = ((booking_date.month - 1) // 6 + 1) * 6
    last_day_semester = calendar.monthrange(booking_date.year, semester_end_month)[1]
    fin_semestre = booking_date.day >= last_day_semester - 5
    fin_annee = booking_date.month == 12 and booking_date.day >= 26

    st.write("Transaction Caracteristics")
    is_opp_transaction = st.checkbox("Opposite Transaction ?")
    is_3_sigma = st.checkbox("3 sigmas transactions ?")
    is_similar = st.checkbox("Similar transactions ?")

with col2:
    st.write("Transaction Summary")
    data_dict = {
        'Booking Date': [booking_date], 'Value Date': [value_date], 'Description': [description],
        'net_amount': [net_amount], 
        'market_value': [market_value]}
    
    df = pd.DataFrame(data_dict)
    nav_pct = 100 * df["net_amount"] / df["market_value"]
    nav_pct = nav_pct.values[0]
    df["nav_pct"] = nav_pct
    st.dataframe(df.transpose(),  width = 800)

    st.write("Date features")
    data_date_dict = {
        'date_delta' : [date_delta],
        'date_delta_7' : [date_delta_7], 'date_delta_30' : [date_delta_30],
        'fin_semaine' : [fin_semaine], 'fin_mois':[fin_mois], 'fin_trimestre': [fin_trimestre],
        'fin_semestre': [fin_semestre], 'fin_annee': [fin_annee] }
    
    df_date = pd.DataFrame(data_date_dict)
    st.dataframe(df_date.transpose(),  width = 800)

    st.write("NLP")
    label = X.extract_alpha_sequences(description)
    bad_words = X.has_bad_words(label)
    CV_pred = models.C_V_charge.transform([label])
    predictions_cluster = models.kmeans_charge.predict(CV_pred)
    data_dict_nlp = {
        'label' : [label], 'Cluster': [predictions_cluster], 'Bad Words ?': [bad_words], 'Anomaly': [is_anomaly_in_custer]}

    df_nlp = pd.DataFrame(data_dict_nlp)
    st.dataframe(df_nlp.transpose(), width = 800)

if is_opp_transaction == False:
    is_opp_transaction_0 = 1.0
    is_opp_transaction_1 = 0.0
else:
    is_opp_transaction_0 = 0.0
    is_opp_transaction_1 = 1.0

if is_3_sigma ==  False:
    is_3_sigma_0 = 1.0
    is_3_sigma_1 = 0.0
else:
    is_3_sigma_0 = 0.0
    is_3_sigma_1 = 1.0

if is_similar == False:
    is_similar_0 = 1.0
    is_similar_1 = 0.0
else:
    is_similar_0 = 0.0
    is_similar_1 = 1.0

if date_delta_7 == False:
    date_delta_7_0 = 1.0
    date_delta_7_1 = 0.0
else:
    date_delta_7_0 = 0.0
    date_delta_7_1 = 1.0

if date_delta_30 == False:
    date_delta_30_0 = 1.0
    date_delta_30_1 = 0.0
else:
    date_delta_30_0 = 0.0
    date_delta_30_1 = 1.0

if fin_semaine == False:
    fin_semaine_0 = 1.0
    fin_semaine_1 = 0.0
else:
    fin_semaine_0 = 0.0
    fin_semaine_1 = 1.0

if fin_mois == False:
    fin_mois_0 = 1.0
    fin_mois_1 = 0.0
else:
    fin_mois_0 = 0.0
    fin_mois_1 = 1.0

if fin_trimestre == False:
    fin_trimestre_0 = 1.0
    fin_trimestre_1 = 0.0
else:
    fin_trimestre_0 = 0.0
    fin_trimestre_1 = 1.0

if fin_semestre == False:
    fin_semestre_0 = 1.0
    fin_semestre_1 = 0.0
else:
    fin_semestre_0 = 0.0
    fin_semestre_1 = 1.0

if fin_annee == False:
    fin_annee_0 = 1.0
    fin_annee_1 = 0.0
else:
    fin_annee_0 = 0.0
    fin_annee_1 = 1.0      

if predictions_cluster == 0:
    deal_type_0 = 1.0
    deal_type_1 = 0.0
    deal_type_2 = 0.0
    deal_type_3 = 0.0
    deal_type_4 = 0.0
    deal_type_5 = 0.0
elif predictions_cluster == 1:
    deal_type_0 = 0.0
    deal_type_1 = 1.0
    deal_type_2 = 0.0
    deal_type_3 = 0.0
    deal_type_4 = 0.0
    deal_type_5 = 0.0
elif predictions_cluster == 2:
    deal_type_0 = 0.0
    deal_type_1 = 0.0
    deal_type_2 = 1.0
    deal_type_3 = 0.0
    deal_type_4 = 0.0
    deal_type_5 = 0.0
elif predictions_cluster == 3:
    deal_type_0 = 0.0
    deal_type_1 = 0.0
    deal_type_2 = 0.0
    deal_type_3 = 1.0
    deal_type_4 = 0.0
    deal_type_5 = 0.0
elif predictions_cluster == 4:
    deal_type_0 = 0.0
    deal_type_1 = 0.0
    deal_type_2 = 0.0
    deal_type_3 = 0.0
    deal_type_4 = 1.0
    deal_type_5 = 0.0
elif predictions_cluster == 5:
    deal_type_0 = 0.0
    deal_type_1 = 0.0
    deal_type_2 = 0.0
    deal_type_3 = 0.0
    deal_type_4 = 0.0
    deal_type_5 = 1.0

if is_anomaly_in_custer:
    anomaly_in_custer = 1
else:
    anomaly_in_custer = 0

test = {'net_amount_fx': net_amount,
 'nav_pct': nav_pct,
 'is_opp_transaction_0': is_opp_transaction_0,
 'is_opp_transaction_1': is_opp_transaction_1,
 'is_3_sigma_0': is_3_sigma_0,
 'is_3_sigma_1': is_3_sigma_1,
 'date_delta_7_0': date_delta_7_0,
 'date_delta_7_1': date_delta_7_1,
 'date_delta_30_0': date_delta_30_0,
 'date_delta_30_1': date_delta_30_1,
 'fin_semaine_0': fin_semaine_0,
 'fin_semaine_0': fin_semaine_1,
 'fin_mois_0': fin_mois_0,
 'fin_mois_1': fin_mois_1,
 'fin_trimestre_0': fin_trimestre_0,
 'fin_trimestre_1': fin_trimestre_1,
 'fin_semestre_0': fin_semestre_0,
 'fin_semestre_1': fin_semestre_1,
 'fin_annee_0': fin_annee_0,
 'fin_annee_1': fin_annee_1,
 'is_similar_0': is_similar_0,
 'is_similar_1': is_similar_1,
 'has_bad_word': bad_words,
 'anomaly_predict_cluster': anomaly_in_custer ,
 'deal_type_0': deal_type_0,
 'deal_type_1': deal_type_1,
 'deal_type_2': deal_type_2,
 'deal_type_3': deal_type_3,
 'deal_type_4': deal_type_4,
 'deal_type_5': deal_type_5}

X_test = pd.DataFrame(test, index=[0])
col = ["net_amount_fx", "nav_pct"]
X_test[col] = models.scaler_charge.transform(X_test[col].values.reshape(-1,2))

st.divider() 

# st.write(X_test.to_dict())

anomaly = models.clf_charge.predict(X_test)

with st.sidebar:
    st.header(':blue[Conclusions] ')
    if anomaly == -1:
        st.write(-1 , "Transaction is an anomaly :scream:")
    else:
        st.write(1 , "Transaction is normal :sunglasses: ")

    def score_func(X):
        return models.clf_charge.decision_function(X)

    # Créer l'explainer SHAP
    explainer = shap.KernelExplainer(score_func, X_test)

    # Calculer les valeurs SHAP
    shap_values = explainer.shap_values(X_test)

    # Visualiser les valeurs SHAP
    shap.summary_plot(shap_values, X_test)