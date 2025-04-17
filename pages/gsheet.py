import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime, timedelta

st.title("📄 Données Google Sheet")
st.write("Cette page affiche les données d'une feuille Google Sheets.")
st.markdown('`GOOGLEFINANCE("TSLA"; "price";TODAY()-90;TODAY())`')
# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

# Initialiser le dataframe dans session_state si pas déjà présent
if "df" not in st.session_state:
    st.session_state.df = conn.read(worksheet="Feuille 1")
# Bouton de mise à jour
if st.button("🔄 Mettre à jour les données"):
    st.session_state.df = conn.read(worksheet="Feuille 1", ttl=0)
    st.success("Tableau mis à jour depuis la Google Sheet ✅")
# Nettoyage de données : conversion des dates
df = st.session_state.df.copy()

# Afficher les données
col = st.columns([0.3, 0.7]) # Donner un peu plus de largeur au graphique
with col[0]:
    st.subheader("Données Google Sheet")
    st.dataframe(df, use_container_width=True)
with col[1]:
    st.subheader("Chart")
          # 1. Create the interactive Plotly line chart
    fig_plotly = px.line(
        df,
        x='Date',           # Column for X-axis (should be datetime)
        y='Close',          # Column for Y-axis (should be numeric)
        title="Évolution du Prix de Clôture", # Chart title
        markers=True,       # Show markers on data points (like marker='.')
        labels={            # Customize axis labels shown to user
            "Date": "Date",
            "Close": "Prix de Clôture ($)"
            }
        # template="plotly_white" # Optional: Apply a visual theme
    )

    # 2. Customize hover information (shows details when mouse is over points)
    fig_plotly.update_traces(
        hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>Prix</b>: %{y:$.2f}<extra></extra>"
        # %{x|%Y-%m-%d} formats the date in hover
        # %{y:$.2f} formats the price as currency
        # <extra></extra> removes the trace name box
    )

    # 3. Update layout (optional refinements)
    fig_plotly.update_layout(
        xaxis_title="Date", # Set explicit axis titles
        yaxis_title="Prix de Clôture ($)",
        hovermode="x unified", # Show hover for closest X value across traces (if multiple lines)
        margin=dict(l=30, r=30, t=50, b=30) # Adjust plot margins
    )
    # Plotly handles date tick formatting and rotation automatically quite well.
    # If needed, customize x-axis further with fig_plotly.update_xaxes(...)

    # 4. Display the Plotly chart in Streamlit
    st.plotly_chart(fig_plotly, use_container_width=True)








# # Ajouter une ligne via un formulaire
# with st.form("add_row_form"):
#     name = st.text_input("Nom")
#     pet = st.text_input("Animal")
#     submitted = st.form_submit_button("Ajouter")

# if submitted:
#     new_row = pd.DataFrame([{"name": name, "pet": pet}])
#     st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
#     conn.update(worksheet="Feuille 1", data=st.session_state.df)
#     st.success("Ligne ajoutée avec succès ✅")