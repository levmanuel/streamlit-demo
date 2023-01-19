#- conso 100km en % selon le type de route
## cout de recharge
#- cout de recharge à la maison
## planification de voyage

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Model 3 SR+ Overview", page_icon="🚗")

st.title("Model 3 SR+ Overview")
st.markdown(""" [Lien vers le site Tesla Model 3](https://www.tesla.com/fr_fr/model3)

[Lien vers le manuel utilisateur](https://www.tesla.com/ownersmanual/model3/fr_lu/)
""")

st.title("Consommation")

df = pd.DataFrame({
"Columns": ["pct initiale de la batterie","Route","Temperature"],
"100": [20, 45, 25],
"90": [20, 45, 25],
"50": [0, 0, 0],
"10": [0, 0, 0]})

st.dataframe(df)

st.title("Temps de recharge")
st.title("Coût de recharge")
st.title("Planification")

#test
