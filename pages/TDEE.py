import streamlit as st

from lib import tdee as calc
from lib import tdee_textes as T
from lib.tdee_ui.activite import render_activite, render_objectif
from lib.tdee_ui.macros import render_macros
from lib.tdee_ui.profil import render_profil
from lib.tdee_ui.resultats import (render_formule, render_indicateurs,
                                   render_macros_resultats, render_repartition)

st.title(T.TITRE)
st.write(T.INTRO)

avance = st.toggle(T.MODE_AVANCE, key="avance")

col_reglages, col_resultats = st.columns(2, gap="large")

with col_reglages:
    profil = render_profil()
    niveau, mult, eat_pct, tef_pct = render_activite(avance)
    objectif_key, ajustement = render_objectif()
    macros_pct, macros_kcalg = render_macros(avance)

with col_resultats:
    bmr_value = calc.bmr(profil["sexe"], profil["poids"], profil["taille"],
                         profil["age"], profil["equation"])
    tdee_value = calc.tdee(bmr_value, mult)
    objectif_value = calc.objectif(tdee_value, ajustement)
    render_indicateurs(bmr_value, tdee_value, objectif_value, ajustement)
    render_repartition(bmr_value, tdee_value, tef_pct, eat_pct)
    render_macros_resultats(objectif_value, macros_pct, macros_kcalg)
    render_formule(profil, mult, bmr_value, tdee_value, objectif_value, ajustement)

st.caption(T.AVERTISSEMENT)
