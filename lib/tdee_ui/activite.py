"""Composants « Activité » et « Objectif »."""
import streamlit as st

from lib import tdee as calc
from lib import tdee_textes as T


def _fmt_niveau(key):
    nom, desc = T.ACTIVITE_NIVEAUX[key]
    return f"{nom} — {desc}"


def render_activite(avance):
    """Retourne (niveau, multiplicateur, part EAT en %, part TEF en %)."""
    ss = st.session_state
    ss.setdefault("activite", calc.ACTIVITE_DEFAUT)
    for lvl in calc.ACTIVITY_LEVELS:
        ss.setdefault(f"mult_{lvl['key']}", lvl["mult"])
    ss.setdefault("tef", calc.TEF_DEFAUT)

    st.subheader(T.ACTIVITE)
    st.radio(T.ACTIVITE, [l["key"] for l in calc.ACTIVITY_LEVELS],
             format_func=_fmt_niveau, key="activite", label_visibility="collapsed")

    if avance:
        for lvl in calc.ACTIVITY_LEVELS:
            nom = T.ACTIVITE_NIVEAUX[lvl["key"]][0]
            st.number_input(T.MULTIPLICATEUR.format(niveau=nom), min_value=1.0,
                            max_value=3.0, step=0.025, format="%.3f",
                            key=f"mult_{lvl['key']}")
        st.number_input(T.TEF_PART, min_value=0.0, max_value=30.0, step=0.5, key="tef")

    niveau = next(l for l in calc.ACTIVITY_LEVELS if l["key"] == ss.activite)
    mult = calc.borner(ss.get(f"mult_{niveau['key']}"), 1.0, 3.0, niveau["mult"])
    tef = calc.borner(ss.get("tef"), 0.0, 30.0, calc.TEF_DEFAUT)
    return niveau["key"], mult, niveau["eat"], tef


def _reset_ajustement():
    """Changer d'objectif remet le curseur à sa valeur par défaut."""
    cle = st.session_state.objectif
    st.session_state[f"ajust_{cle}"] = calc.ajustement_defaut(cle)


def render_objectif():
    """Retourne (clé de l'objectif, ajustement quotidien en kcal)."""
    ss = st.session_state
    ss.setdefault("objectif", calc.OBJECTIF_DEFAUT)
    for cle in calc.GOALS:
        ss.setdefault(f"ajust_{cle}", calc.ajustement_defaut(cle))

    st.subheader(T.OBJECTIF)
    st.radio(T.OBJECTIF, list(calc.GOALS), key="objectif", label_visibility="collapsed",
             format_func=lambda k: f"{T.OBJECTIFS[k][0]} — {T.OBJECTIFS[k][1]}",
             on_change=_reset_ajustement)

    cle = ss.objectif
    g = calc.GOALS[cle]
    if g["min"] == g["max"]:  # maintien : pas de curseur
        return cle, 0
    # Plage unique par objectif : le curseur est propre à l'objectif choisi.
    ajust = st.slider(T.AJUSTEMENT, g["min"], g["max"], step=10, key=f"ajust_{cle}")
    return cle, ajust
