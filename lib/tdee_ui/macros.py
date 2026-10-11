"""Composant « Macronutriments » : 3 curseurs liés (total = 100 %)."""
import streamlit as st

from lib import tdee as calc
from lib import tdee_textes as T


def _sur_changement(index):
    ss = st.session_state
    courant = tuple(ss[f"pct_{i}"] for i in range(3))
    for i, v in enumerate(calc.rebalance(courant, index, courant[index])):
        ss[f"pct_{i}"] = v


def render_macros(avance):
    """Retourne (pourcentages, kcal par gramme)."""
    ss = st.session_state
    for i in range(3):
        ss.setdefault(f"pct_{i}", calc.MACROS_PCT_DEFAUT[i])
        ss.setdefault(f"kcalg_{i}", float(calc.MACROS_KCAL_DEFAUT[i]))

    st.subheader(T.MACROS_TITRE)
    for i, nom in enumerate(T.MACROS_NOMS):
        st.slider(T.MACROS_PCT.format(nom=nom), 0, 100, key=f"pct_{i}",
                  on_change=_sur_changement, args=(i,))
    if avance:
        for i, nom in enumerate(T.MACROS_NOMS):
            st.number_input(T.MACROS_KCAL_G.format(nom=nom), min_value=1.0,
                            max_value=12.0, step=0.5, key=f"kcalg_{i}")

    pcts = tuple(ss[f"pct_{i}"] for i in range(3))
    kcalg = tuple(calc.borner(ss.get(f"kcalg_{i}"), 1.0, 12.0, calc.MACROS_KCAL_DEFAUT[i])
                  for i in range(3))
    return pcts, kcalg
