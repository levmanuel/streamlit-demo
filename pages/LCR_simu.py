import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="LCR Simulation Demo", page_icon="📈")

st.title("LCR Simulation Tool")
st.write("Selon cette norme, l’encours d’actifs liquides de haute qualité doit au moins être égal aux sorties nettes de trésorerie pendant les 30 jours qui suivent la date d’arrêté du calcul du ratio.")

st.latex(r'''
     LCR  = \frac{HQLA}{outflows-min(0,75outflows, inflows)}
     ''')

factor_hqla = st.slider('HQLA Factor %', -100, 100, 0)
factor_out = st.slider('Outflows Factor %', -100, 100, 0)
factor_in = st.slider('Inflows Factor %', -100, 100, 0)

df = pd.DataFrame({
"Name": ["HQLA","Outflow","Inflow", "LCR"],
"start": [20, 45, 25, 0],
"updated": [20, 45, 25, 0],
"delta": [0, 0, 0, 0],
"delta_pct": [0, 0, 0, 0]})

df.iloc[0, 2] = (1+factor_hqla/100) * df.iloc[0, 1]
df.iloc[1, 2] = (1+factor_out/100) * df.iloc[1, 1]
df.iloc[2, 2] = (1+factor_in/100) * df.iloc[2, 1]
df.iloc[3, 1] = 100*df.iloc[0, 1] / (df.iloc[1, 1] - min( 0.75*df.iloc[1, 1] ,df.iloc[2, 1]))
df.iloc[3, 2] = round(100*df.iloc[0, 2] / (df.iloc[1, 2] - min( 0.75*df.iloc[1, 1] ,df.iloc[2, 2])),2)

df.iloc[0, 3] = round(df.iloc[0, 2] - df.iloc[0, 1], 2)
df.iloc[0, 4] = round(df.iloc[0, 2] / df.iloc[0, 1] - 1,2)

df.iloc[1, 3] = df.iloc[1, 2] - df.iloc[1, 1]
df.iloc[1, 4] = df.iloc[1, 2] / df.iloc[1, 1] - 1

df.iloc[2, 3] = df.iloc[2, 2] - df.iloc[2, 1]
df.iloc[2, 4] = df.iloc[2, 2] / df.iloc[2, 1] - 1

df.iloc[3, 3] = df.iloc[3, 2] - df.iloc[3, 1]
df.iloc[3, 4] = df.iloc[3, 2] / df.iloc[3, 1] - 1

#st.dataframe(df)

nof = pd.DataFrame({
"Name": ["Outflow", "75cpt_Outflow", "Inflow", "Min(0.75 OF, IF)", "Net_Ouflow"],
"start": [45, 0.75*45, 25, min(0.75*45, 25), 20],
"updated": [45, 0.75*45, 25, min(0.75*45, 25), 20]})

nof.iloc[0, 2] = (1+factor_out/100) * nof.iloc[0, 1]
nof.iloc[1, 2] = 0.75*((1+factor_out/100) * nof.iloc[0, 1])
nof.iloc[2, 2] = (1+factor_in/100) * nof.iloc[2, 1]
nof.iloc[3, 2] = min(nof.iloc[1, 2] , nof.iloc[2, 2])
nof.iloc[4, 2] = nof.iloc[0, 2] - nof.iloc[3, 2]

col1, col2 = st.columns(2)
col1.write("LCR calculation detail")
col1.dataframe(df)
col2.write("Net Outflow calculation detail")
col2.dataframe(nof)

if nof.iloc[1, 2] > nof.iloc[2, 2]:
    st.write("case: Inflows NOT capped")
else:
     st.write("WARNING CASE: Inflows capped")


st.title("Simulation of LCR in case of change of x pct of Outflows during 30 days")

OF_factor = st.slider('Outflow rate increase', 0, 100, 1)

days = []
lcr_list = []
outflows_list = []


for i in range(0,30):
     if i == 0:
          outflows = round((1+OF_factor/100)*df.iloc[1, 2],1)
     else:
          outflows = round((1+OF_factor/100)*outflows_list[-1],1)

     outflows_list.append(outflows)
     lcr = round(100*df.iloc[0, 2] / (outflows - min( 0.75*outflows ,df.iloc[2, 2])),1)
     lcr_list.append(lcr)
     days.append(i+1)

chart_data = pd.DataFrame(data=lcr_list, index=days, columns=['LCR'])

st.bar_chart(chart_data)
