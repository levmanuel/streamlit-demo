import streamlit as st

from lib import tdee as calc
from lib import tdee_textes as T
from lib.tdee_ui.profil import render_profil

st.title(T.TITRE)
st.write(T.INTRO)

col_reglages, col_resultats = st.columns(2, gap="large")

with col_reglages:
    profil = render_profil()

with col_resultats:
    bmr_value = calc.bmr(profil["sexe"], profil["poids"], profil["taille"],
                         profil["age"], profil["equation"])
    st.metric("BMR", f"{calc.fmt_fr(bmr_value)} kcal/jour")

st.caption(T.AVERTISSEMENT)
