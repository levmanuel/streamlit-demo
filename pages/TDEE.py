import streamlit as st

from lib import tdee as calc
from lib import tdee_textes as T
from lib.tdee_ui.activite import render_activite, render_objectif
from lib.tdee_ui.profil import render_profil

st.title(T.TITRE)
st.write(T.INTRO)

avance = st.toggle(T.MODE_AVANCE, key="avance")

col_reglages, col_resultats = st.columns(2, gap="large")

with col_reglages:
    profil = render_profil()
    niveau, mult, eat_pct, tef_pct = render_activite(avance)
    objectif_key, ajustement = render_objectif()

with col_resultats:
    bmr_value = calc.bmr(profil["sexe"], profil["poids"], profil["taille"],
                         profil["age"], profil["equation"])
    tdee_value = calc.tdee(bmr_value, mult)
    objectif_value = calc.objectif(tdee_value, ajustement)
    st.metric("BMR", f"{calc.fmt_fr(bmr_value)} kcal/jour")
    st.metric("TDEE", f"{calc.fmt_fr(tdee_value)} kcal/jour")
    st.metric("Objectif", f"{calc.fmt_fr(objectif_value)} kcal/jour")

st.caption(T.AVERTISSEMENT)
