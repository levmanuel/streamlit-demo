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
import statics

st.set_page_config(page_title="Cash Monitoring Outlier Detection", page_icon="🐶")
st.title("Depositary Control Data Science Project")

col1, col2 = st.columns(2)
with col1:
    st.write("Transaction Input")
    booking_date = st.date_input('Booking Date')
    value_date = st.date_input('Value Date')
    description = st.text_input('Description', value="110-Ext.Ref: Our Ref: userXXX-ZZZ INT002667762PRC Transfer of EUR 676.90 in favour of FUND INVESTMENTS - FEES MONEY-210119")
    net_amount = st.number_input('Net Amount', value= 300_000 )
    market_value = st.number_input('Fund Market Value', value= 10_000_000 )
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

    if is_opp_transaction:
        is_opp_transaction_0 = 1.0
        is_opp_transaction_1 = 0.0
    else:
        is_opp_transaction_0 = 0.0
        is_opp_transaction_1 = 1.0


    if is_3_sigma:
        is_3_sigma_0 = 1.0
        is_3_sigma_1 = 0.0
    else:
        is_3_sigma_0 = 0.0
        is_3_sigma_1 = 1.0


    if is_similar:
        is_similar_0 = 1.0
        is_similar_1 = 0.0
    else:
        is_similar_0 = 0.0
        is_similar_1 = 1.0

with col2:
    st.write("Transaction Summary")
    data_dict = {
        'Booking Date': [booking_date], 'Value Date': [value_date], 'Description': [description],
        'net_amount': [net_amount], 
        'market_value': [market_value], 'date_delta' : [date_delta],
        'date_delta_7' : [date_delta_7], 'date_delta_30' : [date_delta_30],
        'fin_semaine' : [fin_semaine], 'fin_mois':[fin_mois], 'fin_trimestre': [fin_trimestre],
        'fin_semestre': [fin_semestre], 'fin_annee': [fin_annee]}
    
    df = pd.DataFrame(data_dict)
    df["NAV_pct"] = 100 * df["net_amount"] / df["market_value"]
    st.dataframe(df.transpose())


    st.write("NLP")
    data_dict_nlp = {
        'Description': [description], 'label' : [label]}


    df_nlp = pd.DataFrame(data_dict_nlp)
    st.dataframe(df_nlp.transpose())




### NLP part
exlusion_list = ["ref", "our", "for", "ext", "prc", "wgs", "useri", "caceis", "luxembourg", "bank",
                "kqj", "yen", "cswnew", "roc", "isaebebbxxx", "luxe", "belgium", "bsuilull", "bran" "bra","buq",
                "scr", "userint", "rua", "qwe", "xrd", "nos", "brussels", "branc", "xxx", "isaebebb", "cbf",
                "isaefr","xxxxx", "bom", "nonref", "notprovided", "acou", "ajs", "clb", "cbb", "hev", "int"]

ccy = ['eur', 'usd', 'jpy', 'bgn', 'czk', 'dkk', 'gbp', 'huf', 'pln', 'ron', 'sek', 'chf', 'isk', 'nok', 'try', 'aud',
 'brl', 'cad', 'cny', 'hkd', 'idr', 'ils', 'inr', 'krw', 'mxn', 'myr', 'nzd', 'php', 'sgd', 'thb', 'zar', 'rub', 'cnh', 'twd']
regex = r'\b(?:' + '|'.join(ccy) + r')\b|\b(?:' + '|'.join(ccy) + r'){2,}\b'

def extract_alpha_sequences(string, max_word=None):
    if max_word == None:
        matches = re.findall(r'[A-Za-z]+', string.lower())
        matches = [i for i in matches if (len(i)> 2 and i not in exlusion_list)]
        matches = ' '.join(matches)
        matches = re.sub(regex, '[CCY]', matches)
        return matches
    else:
        matches = re.findall(r'[A-Za-z]+', string.lower())
        matches = [i for i in matches if (len(i)> 2 and i not in exlusion_list)][:max_word]
        matches = ' '.join(matches)
        matches = re.sub(regex, '[CCY]', matches)
        return matches



def has_bad_words(string):
  for i in string.split():
    if i in bad_words:
        return 1
    else:
        return 0

label = extract_alpha_sequences(description,15)
st.write(label)
st.write(has_bad_words(label))
