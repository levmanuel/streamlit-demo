import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("📄 Données Google Sheet")
st.write("Cette page affiche les données d'une feuille Google Sheets.")
st.markdown('`GOOGLEFINANCE("TSLA"; "price";TODAY()-90;TODAY())`')

conn = st.connection("gsheets", type=GSheetsConnection)

if "df" not in st.session_state:
    try:
        st.session_state.df = conn.read(worksheet="Feuille 1", ttl=600)
    except Exception as e:
        st.error(f"Impossible de charger la Google Sheet : {e}")
        st.stop()

if st.button("🔄 Mettre à jour les données"):
    try:
        st.session_state.df = conn.read(worksheet="Feuille 1", ttl=0)
        st.success("Tableau mis à jour depuis la Google Sheet ✅")
    except Exception as e:
        st.error(f"Erreur lors de la mise à jour : {e}")

col = st.columns([0.4, 0.6])
with col[0]:
    st.subheader("Données Google Sheet")
    st.dataframe(st.session_state.df, use_container_width=True)
with col[1]:
    st.subheader("Chart")
    st.line_chart(st.session_state.df, x="Date", y="Close")
