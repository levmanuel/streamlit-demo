"""Composant « Profil » : sexe, unités, âge, poids, taille, équation."""
import streamlit as st

from lib import tdee as calc
from lib import tdee_textes as T


def _init():
    ss = st.session_state
    ss.setdefault("sexe", "homme")
    ss.setdefault("unites", "metrique")
    ss.setdefault("equation", "mifflin")
    ss.setdefault("age", calc.DEFAUTS["age"])
    # Valeurs internes : toujours en kg et en cm.
    ss.setdefault("poids_kg", calc.DEFAUTS["poids"])
    ss.setdefault("taille_cm", calc.DEFAUTS["taille"])
    _afficher_depuis_interne()


def _afficher_depuis_interne():
    """Remplit les champs d'unité à partir des valeurs internes (kg, cm)."""
    ss = st.session_state
    ss.poids_m = ss.poids_kg
    ss.poids_lb = round(calc.kg_to_lb(ss.poids_kg), 1)
    ss.taille_m = ss.taille_cm
    ss.taille_ft, ss.taille_in = calc.cm_to_ft_in(ss.taille_cm)


def _sur_changement_unites():
    _afficher_depuis_interne()


def _sur_poids(cle):
    ss = st.session_state
    v = ss.get(cle)
    if v is None:  # champ vidé : on garde la dernière valeur valide
        return
    kg = calc.lb_to_kg(v) if cle == "poids_lb" else v
    ss.poids_kg = calc.borner(kg, *calc.LIMITES["poids"], calc.DEFAUTS["poids"])


def _sur_taille():
    ss = st.session_state
    if ss.unites == "metrique":
        v = ss.get("taille_m")
    else:
        ft, inch = ss.get("taille_ft"), ss.get("taille_in")
        v = None if ft is None and inch is None else calc.ft_in_to_cm(ft or 0, inch or 0)
    if v is None:
        return
    ss.taille_cm = calc.borner(v, *calc.LIMITES["taille"], calc.DEFAUTS["taille"])


def render_profil():
    """Affiche le profil et retourne les valeurs bornées (kg, cm)."""
    _init()
    ss = st.session_state
    st.subheader(T.PROFIL)

    c1, c2 = st.columns(2)
    c1.radio(T.SEXE, list(T.SEXES), format_func=T.SEXES.get, key="sexe", horizontal=True)
    c2.radio(
        T.UNITES, list(T.UNITES_OPTIONS), format_func=T.UNITES_OPTIONS.get,
        key="unites", on_change=_sur_changement_unites,
    )

    lo, hi = calc.LIMITES["age"]
    st.number_input(T.AGE, min_value=lo, max_value=hi, step=1, key="age")

    if ss.unites == "metrique":
        lo, hi = calc.LIMITES["poids"]
        st.number_input(
            T.POIDS_KG, min_value=float(lo), max_value=float(hi), step=0.5,
            format="%.1f", key="poids_m", on_change=_sur_poids, args=("poids_m",),
        )
        lo, hi = calc.LIMITES["taille"]
        st.number_input(
            T.TAILLE_CM, min_value=float(lo), max_value=float(hi), step=1.0,
            format="%.0f", key="taille_m", on_change=_sur_taille,
        )
    else:
        lo, hi = (round(calc.kg_to_lb(x)) for x in calc.LIMITES["poids"])
        st.number_input(
            T.POIDS_LB, min_value=float(lo), max_value=float(hi), step=1.0,
            format="%.1f", key="poids_lb", on_change=_sur_poids, args=("poids_lb",),
        )
        f1, f2 = st.columns(2)
        f1.number_input(T.TAILLE_FT, min_value=3, max_value=7, step=1,
                        key="taille_ft", on_change=_sur_taille)
        f2.number_input(T.TAILLE_IN, min_value=0, max_value=11, step=1,
                        key="taille_in", on_change=_sur_taille)

    st.radio(T.EQUATION, list(T.EQUATIONS), format_func=T.EQUATIONS.get, key="equation")

    return {
        "sexe": ss.sexe,
        "equation": ss.equation,
        "age": int(calc.borner(ss.get("age"), *calc.LIMITES["age"], calc.DEFAUTS["age"])),
        "poids": calc.borner(ss.poids_kg, *calc.LIMITES["poids"], calc.DEFAUTS["poids"]),
        "taille": calc.borner(ss.taille_cm, *calc.LIMITES["taille"], calc.DEFAUTS["taille"]),
    }
