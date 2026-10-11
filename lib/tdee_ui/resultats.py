"""Composants d'affichage des résultats (R1 à R6)."""
import plotly.graph_objects as go
import streamlit as st

from lib import tdee as calc
from lib import tdee_textes as T

_F = calc.fmt_fr


def render_indicateurs(bmr_v, tdee_v, objectif_v, ajustement):
    st.metric(f"{T.R_TDEE} ({T.R_UNITE})", _F(tdee_v), border=True)
    c1, c2 = st.columns(2)
    c1.metric(f"{T.R_BMR} ({T.R_UNITE})", _F(bmr_v))
    c2.metric(f"{T.R_OBJECTIF} ({T.R_UNITE})", _F(objectif_v))
    st.write(T.R_VARIATION.format(texte=calc.rythme_texte(ajustement)))


def render_repartition(bmr_v, tdee_v, tef_pct, eat_pct):
    parts = calc.repartition(bmr_v, tdee_v, tef_pct, eat_pct)
    st.subheader(T.R_REPARTITION)

    fig = go.Figure()
    for cle, pct in parts.items():
        fig.add_bar(y=[""], x=[pct], orientation="h", name=T.R_PARTS_COURT[cle],
                    text=[f"{_F(pct)} %"], textposition="inside",
                    hovertemplate=f"{T.R_PARTS[cle]} : {_F(pct, 1)} %<extra></extra>")
    fig.update_layout(barmode="stack", height=130, margin=dict(l=0, r=0, t=0, b=0),
                      xaxis=dict(visible=False, range=[0, 100]), legend=dict(orientation="h", traceorder="normal"))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    lignes = [f"| {T.R_COL_PART} | {T.R_COL_PCT} | {T.R_COL_KCAL} |", "|---|--:|--:|"]
    for cle, pct in parts.items():
        lignes.append(f"| {T.R_PARTS_COURT[cle]} | {_F(pct)}\u00a0% | {_F(tdee_v * pct / 100)} |")
    st.markdown("\n".join(lignes))


def render_macros_resultats(objectif_v, pcts, kcalg):
    st.subheader(T.R_MACROS)
    total = sum(pcts)
    if total != 100:
        st.warning(T.R_ALERTE_MACROS.format(total=total))
    for nom, pct, m in zip(T.MACROS_NOMS, pcts, calc.macros(objectif_v, pcts, kcalg)):
        st.write(T.R_GRAMMES.format(nom=nom, grammes=_F(m["grammes"]),
                                    kcal=_F(m["kcal"]), pct=_F(pct)))
        st.progress(min(max(pct, 0), 100) / 100)


def _signe(x):
    return "−" if x < 0 else "+"


def render_formule(profil, mult, bmr_v, tdee_v, objectif_v, ajustement):
    st.subheader(T.R_FORMULE)
    w, h, a = _F(profil["poids"], 1), _F(profil["taille"], 0), profil["age"]
    if profil["equation"] == "harris":
        c = (88.362, 13.397, 4.799, 5.677) if profil["sexe"] == "homme" else (447.593, 9.247, 3.098, 4.330)
        l1 = T.F_BMR_HARRIS.format(c0=_F(c[0], 3), c1=_F(c[1], 3), c2=_F(c[2], 3),
                                   c3=_F(c[3], 3), w=w, h=h, a=a, bmr=_F(bmr_v, 1))
    else:
        const = 5 if profil["sexe"] == "homme" else -161
        l1 = T.F_BMR_MIFFLIN.format(w=w, h=h, a=a, signe=_signe(const), c=abs(const),
                                    bmr=_F(bmr_v, 1))
    l2 = T.F_TDEE.format(bmr=_F(bmr_v, 1), mult=_F(mult, 3).rstrip("0").rstrip(","),
                         tdee=_F(tdee_v, 1))
    l3 = T.F_OBJECTIF.format(tdee=_F(tdee_v, 1), signe=_signe(ajustement),
                             ajust=_F(abs(ajustement)), objectif=_F(objectif_v, 1))
    st.code("\n".join([l1, l2, l3]), language=None)
