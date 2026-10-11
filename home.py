import streamlit as st

from lib.catalogue import DEMOS

st.set_page_config(
    page_title="Portfolio ML — levmanuel",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 Portfolio Data Science & ML")
st.write("Bienvenue sur mon portfolio interactif. Chaque page explore une technique ou un outil différent.")

st.divider()

cols = st.columns(2)
for i, section in enumerate(DEMOS):
    with cols[i % 2]:
        st.subheader(f"{section['icon']} {section['category']}")
        for name, _fichier, desc in section["items"]:
            st.markdown(f"**{name}** — {desc}")
        st.write("")

st.divider()
st.caption("Source : [github.com/levmanuel/streamlit-demo](https://github.com/levmanuel/streamlit-demo) · Déployé sur [levmanuel-demo.streamlit.app](https://levmanuel-demo.streamlit.app)")
