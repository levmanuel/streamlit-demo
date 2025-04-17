import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

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
df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")

# Afficher les données
col = st.columns([0.3, 0.7]) # Donner un peu plus de largeur au graphique
with col[0]:
    st.subheader("Données Google Sheet")
    st.dataframe(df, use_container_width=True)
with col[1]:
    st.subheader("Chart")
    fig, ax = plt.subplots(figsize=(10, 6)) # Légèrement plus grand
    sns.lineplot(data=df, x="Date", y="Close", ax=ax, marker='.', markersize=5, color='dodgerblue')
    # Formatage de l'axe des x
    ax.xaxis.set_major_locator(plt.MaxNLocator(10))  # Limiter le nombre de ticks
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: pd.to_datetime(x).strftime('%Y-%m-%d')))
    plt.xticks(rotation=90)  # Rotation des labels pour éviter le chevauchement
    plt.xlabel("Date")

    st.pyplot(plt)








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