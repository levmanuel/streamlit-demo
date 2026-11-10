import time

import streamlit as st

from lib import the_game as g

st.set_page_config(page_title="The Game", page_icon="🎮", layout="centered")

# Couleurs lisibles en thème clair comme en thème sombre (texte hérité du thème).
st.markdown(
    """
    <style>
        .tg-pile { text-align: center; padding: 4px 0 8px; }
        .tg-pile .tg-sens { font-size: 0.8rem; font-weight: 600; letter-spacing: .04em;
                            text-transform: uppercase; }
        .tg-pile .tg-sommet { font-size: 3rem; font-weight: 700; line-height: 1.1;
                              font-variant-numeric: tabular-nums; }
        .tg-pile .tg-histo { font-size: 0.8rem; opacity: .6; min-height: 1.2em;
                             font-variant-numeric: tabular-nums; }
        .tg-asc .tg-sens, .tg-asc .tg-sommet { color: #1f9d55; }
        .tg-desc .tg-sens, .tg-desc .tg-sommet { color: #e0533d; }
        .tg-nouveau .tg-sommet { text-decoration: underline; text-underline-offset: 6px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- État -------------------------------------------------------------------
def nouvelle_partie():
    st.session_state.tg_partie = g.nouvelle_partie()
    st.session_state.tg_selection = None
    st.session_state.tg_comptee = False


if "tg_partie" not in st.session_state:
    nouvelle_partie()
st.session_state.setdefault("tg_selection", None)
st.session_state.setdefault("tg_comptee", False)
st.session_state.setdefault("tg_stats", {"parties": 0, "victoires": 0, "meilleur": None})

partie = st.session_state.tg_partie


# --- Actions (callbacks : exécutées avant le rendu, sans st.rerun) -----------
def selectionner(carte):
    actuelle = st.session_state.tg_selection
    st.session_state.tg_selection = None if actuelle == carte else carte


def poser(index_pile):
    carte = st.session_state.tg_selection
    if carte in partie["main"] and g.coup_valide(carte, partie["piles"][index_pile]):
        g.jouer(partie, carte, index_pile)
    st.session_state.tg_selection = None


def annuler():
    g.annuler(partie)
    st.session_state.tg_selection = None


def finir_tour():
    if g.peut_finir_tour(partie):
        g.fin_tour(partie)
    st.session_state.tg_selection = None


# --- En-tête ----------------------------------------------------------------
st.title("🎮 The Game")
st.caption(
    "Jeu coopératif en solo : posez les 98 cartes sur quatre piles avant d'être bloqué."
)

with st.expander("📖 Règles"):
    st.markdown(
        f"""
- **Piles ascendantes** (départ 1) : posez une carte **plus grande** que le sommet.
- **Piles descendantes** (départ 100) : posez une carte **plus petite**.
- **Le saut de 10** : une carte valant *exactement 10 de moins* (pile ascendante)
  ou *10 de plus* (pile descendante) peut être posée — c'est le seul moyen de
  faire reculer une pile.
- Chaque tour, posez **au moins 2 cartes** (1 seule quand la pioche est vide),
  puis terminez le tour pour compléter votre main à {g.TAILLE_MAIN} cartes.
- La partie est **gagnée** si toutes les cartes sont posées, **perdue** si vous
  ne pouvez plus jouer le minimum requis. Moins de 10 cartes restantes est déjà
  un excellent résultat.
"""
    )

col_auto, col_vitesse, col_new = st.columns([2, 3, 2])
auto = col_auto.toggle("🤖 Auto-play (IA)", key="tg_auto")
if auto:
    col_vitesse.slider("Délai entre deux coups (s)", 0.1, 2.0, 0.5, 0.1, key="tg_vitesse")
col_new.button("🔄 Nouvelle partie", on_click=nouvelle_partie, use_container_width=True)

# --- Tour de l'IA -----------------------------------------------------------
if auto and g.statut(partie) == g.EN_COURS:
    g.jouer_ia(partie)
    st.session_state.tg_selection = None

etat = g.statut(partie)
selection = st.session_state.tg_selection
if selection not in partie["main"]:
    selection = st.session_state.tg_selection = None
restantes = g.cartes_restantes(partie)
nb_coups, minimum = len(partie["coups_ce_tour"]), g.min_coups(partie)
dernier = partie["coups_ce_tour"][-1][1] if partie["coups_ce_tour"] else None

# --- Indicateurs ------------------------------------------------------------
m1, m2, m3, m4 = st.columns(4)
m1.metric("Tour", partie["tour"])
m2.metric("Pioche", len(partie["pioche"]))
m3.metric("Cartes restantes", restantes)
m4.metric("Posées ce tour", f"{nb_coups} / {minimum} min")
st.progress((98 - restantes) / 98, text=f"{98 - restantes} cartes posées sur 98")

# --- Piles ------------------------------------------------------------------
cols = st.columns(4)
for i, (col, pile) in enumerate(zip(cols, partie["piles"])):
    with col.container(border=True):
        sens = "↗ Ascendante" if pile["ascendante"] else "↘ Descendante"
        classes = "tg-asc" if pile["ascendante"] else "tg-desc"
        if i == dernier:
            classes += " tg-nouveau"
        histo = " · ".join(str(c) for c in pile["cartes"][-4:-1]) or "&nbsp;"
        st.markdown(
            f"<div class='tg-pile {classes}'>"
            f"<div class='tg-sens'>{sens}</div>"
            f"<div class='tg-sommet'>{pile['cartes'][-1]}</div>"
            f"<div class='tg-histo'>{histo}</div></div>",
            unsafe_allow_html=True,
        )
        if etat == g.EN_COURS:
            jouable = not auto and selection is not None and g.coup_valide(selection, pile)
            if jouable:
                ecart = g.cout(selection, pile)
                label = "⏪ Saut −10" if g.est_saut(selection, pile) else f"Poser (+{ecart})"
            else:
                label = "Poser"
            st.button(
                label,
                key=f"tg_pile_{i}",
                disabled=not jouable,
                type="primary" if jouable and g.est_saut(selection, pile) else "secondary",
                on_click=poser,
                args=(i,),
                help="Écart consommé sur la pile" if jouable else None,
                use_container_width=True,
            )

# --- Fin de partie ----------------------------------------------------------
if etat != g.EN_COURS:
    stats = st.session_state.tg_stats
    if not st.session_state.tg_comptee:
        stats["parties"] += 1
        stats["victoires"] += etat == g.GAGNEE
        if stats["meilleur"] is None or restantes < stats["meilleur"]:
            stats["meilleur"] = restantes
        st.session_state.tg_comptee = True
        if etat == g.GAGNEE:
            st.balloons()
    if etat == g.GAGNEE:
        st.success(f"🎉 {g.appreciation(0)} — les 98 cartes sont posées en {partie['tour']} tours !")
    else:
        st.error(
            f"💀 Plus aucun coup possible — **{restantes} cartes restantes**. "
            f"{g.appreciation(restantes)}."
        )
        if partie["main"]:
            st.caption("Main restante : " + " · ".join(map(str, partie["main"])))

# --- Main du joueur ---------------------------------------------------------
else:
    # En auto-play, la main reste visible (lecture seule) pour suivre l'IA.
    st.subheader("Main de l'IA" if auto else "Votre main")
    jouables = set() if auto else {carte for carte, _ in g.coups_possibles(partie)}
    if partie["main"]:
        for col, carte in zip(st.columns(g.TAILLE_MAIN), partie["main"]):
            col.button(
                str(carte),
                key=f"tg_carte_{carte}",
                type="primary" if carte == selection else "secondary",
                disabled=carte not in jouables,
                on_click=selectionner,
                args=(carte,),
                use_container_width=True,
            )
    else:
        st.caption("Main vide — terminez le tour pour repiocher.")

    if auto:
        st.caption("L'IA pose la carte la moins coûteuse et privilégie les sauts de 10.")
    elif selection is None:
        if not jouables:
            st.info("Aucune carte jouable : terminez le tour pour repiocher.")
        elif nb_coups < minimum:
            st.caption(f"Choisissez une carte, puis une pile (encore {minimum - nb_coups} à poser).")
        else:
            st.caption("Minimum atteint : continuez à poser ou terminez le tour.")
    else:
        st.caption(f"Carte **{selection}** sélectionnée — choisissez une pile ci-dessus.")

    c1, c2 = st.columns(2)
    c1.button(
        "↩️ Annuler la dernière carte",
        disabled=auto or nb_coups == 0,
        on_click=annuler,
        use_container_width=True,
    )
    c2.button(
        "✅ Fin de tour" + (" (repiocher)" if partie["pioche"] else ""),
        type="primary",
        disabled=auto or not g.peut_finir_tour(partie),
        on_click=finir_tour,
        use_container_width=True,
    )

# --- Statistiques de session ------------------------------------------------
stats = st.session_state.tg_stats
if stats["parties"]:
    st.divider()
    s1, s2, s3 = st.columns(3)
    s1.metric("Parties terminées", stats["parties"])
    s2.metric("Victoires", stats["victoires"])
    s3.metric("Meilleur score (cartes restantes)", stats["meilleur"])

# --- Boucle auto-play : on affiche l'état, on attend, puis on relance --------
if auto and etat == g.EN_COURS:
    time.sleep(st.session_state.get("tg_vitesse", 0.5))
    st.rerun()
