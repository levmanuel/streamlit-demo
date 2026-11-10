"""Règles et IA du jeu de cartes coopératif « The Game » (version solo).

Logique pure, sans Streamlit : la page `pages/The_Game.py` ne fait que
l'affichage. Une partie est un `dict` simple pour rester sérialisable dans
`st.session_state`.

Règles appliquées :
- 4 piles : 2 ascendantes (départ 1) et 2 descendantes (départ 100) ;
- 98 cartes (2 à 99), main de `TAILLE_MAIN` cartes ;
- pile ascendante : carte plus grande, ou exactement 10 de moins (« saut ») ;
- pile descendante : carte plus petite, ou exactement 10 de plus ;
- au moins 2 cartes par tour (1 seule quand la pioche est vide) ;
- on ne repioche qu'à la fin du tour.
"""

import random

TAILLE_MAIN = 8
CARTE_MIN, CARTE_MAX = 1, 100
SAUT = 10

EN_COURS, GAGNEE, PERDUE = "en_cours", "gagnee", "perdue"

# Au-delà du minimum obligatoire, l'IA ne pose une carte que si elle « coûte »
# au plus ce nombre de valeurs sur la pile (sinon elle préfère repiocher).
SEUIL_IA = 1


def nouvelle_partie(rng=None, taille_main=TAILLE_MAIN):
    """Crée une partie mélangée. `rng` (random.Random) rend le tirage reproductible."""
    rng = rng or random.Random()
    pioche = list(range(CARTE_MIN + 1, CARTE_MAX))
    rng.shuffle(pioche)
    main = sorted(pioche.pop() for _ in range(taille_main))
    return {
        "piles": [
            {"nom": "Ascendante 1", "ascendante": True, "cartes": [CARTE_MIN]},
            {"nom": "Ascendante 2", "ascendante": True, "cartes": [CARTE_MIN]},
            {"nom": "Descendante 1", "ascendante": False, "cartes": [CARTE_MAX]},
            {"nom": "Descendante 2", "ascendante": False, "cartes": [CARTE_MAX]},
        ],
        "pioche": pioche,
        "main": main,
        "taille_main": taille_main,
        "coups_ce_tour": [],  # [(carte, index_pile)] — permet d'annuler
        "tour": 1,
    }


def est_saut(carte, pile):
    """Vrai si la carte fait reculer la pile de exactement 10."""
    sommet = pile["cartes"][-1]
    return carte == (sommet - SAUT if pile["ascendante"] else sommet + SAUT)


def coup_valide(carte, pile):
    sommet = pile["cartes"][-1]
    if est_saut(carte, pile):
        return True
    return carte > sommet if pile["ascendante"] else carte < sommet


def cout(carte, pile):
    """Nombre de valeurs « consommées » sur la pile (négatif pour un saut)."""
    sommet = pile["cartes"][-1]
    return carte - sommet if pile["ascendante"] else sommet - carte


def coups_possibles(partie):
    """Liste des (carte, index_pile) jouables."""
    return [
        (carte, i)
        for carte in partie["main"]
        for i, pile in enumerate(partie["piles"])
        if coup_valide(carte, pile)
    ]


def min_coups(partie):
    return 2 if partie["pioche"] else 1


def peut_finir_tour(partie):
    return len(partie["coups_ce_tour"]) >= min_coups(partie)


def cartes_restantes(partie):
    return len(partie["pioche"]) + len(partie["main"])


def jouer(partie, carte, index_pile):
    pile = partie["piles"][index_pile]
    if carte not in partie["main"] or not coup_valide(carte, pile):
        raise ValueError(f"Coup invalide : {carte} sur {pile['nom']}")
    partie["main"].remove(carte)
    pile["cartes"].append(carte)
    partie["coups_ce_tour"].append((carte, index_pile))


def annuler(partie):
    """Reprend la dernière carte posée ce tour. Retourne False s'il n'y a rien à annuler."""
    if not partie["coups_ce_tour"]:
        return False
    carte, index_pile = partie["coups_ce_tour"].pop()
    partie["piles"][index_pile]["cartes"].pop()
    partie["main"].append(carte)
    partie["main"].sort()
    return True


def fin_tour(partie):
    """Termine le tour et complète la main depuis la pioche."""
    if not peut_finir_tour(partie):
        raise ValueError("Pas assez de cartes jouées ce tour")
    while partie["pioche"] and len(partie["main"]) < partie["taille_main"]:
        partie["main"].append(partie["pioche"].pop())
    partie["main"].sort()
    partie["coups_ce_tour"] = []
    partie["tour"] += 1


def statut(partie):
    if cartes_restantes(partie) == 0:
        return GAGNEE
    if not peut_finir_tour(partie) and not coups_possibles(partie):
        return PERDUE
    return EN_COURS


def appreciation(restantes):
    """Barème officieux du jeu selon le nombre de cartes non posées."""
    if restantes == 0:
        return "Victoire parfaite"
    if restantes < 10:
        return "Excellent résultat"
    if restantes < 20:
        return "Belle partie"
    return "Le jeu a gagné cette fois"


def _valeur_ia(partie, carte, index_pile):
    """Coût d'un coup pour l'IA : valeurs consommées, moins un bonus si le coup
    prépare un saut avec une autre carte de la main."""
    pile = partie["piles"][index_pile]
    valeur = cout(carte, pile)
    cible = carte - SAUT if pile["ascendante"] else carte + SAUT
    if cible in partie["main"]:
        valeur -= SAUT / 2
    return valeur


def coup_ia(partie, seuil=SEUIL_IA):
    """Décision de l'IA : ("jouer", carte, index_pile), ("fin",) ou None si bloquée.

    Heuristique gloutonne : poser la carte qui consomme le moins de valeurs
    (un saut de 10 en regagne) ; une fois le minimum atteint, ne continuer que
    pour les coups peu coûteux, sinon repiocher.
    """
    coups = coups_possibles(partie)
    if not coups:
        return ("fin",) if peut_finir_tour(partie) else None
    valeur, carte, index_pile = min(
        (_valeur_ia(partie, c, i), c, i) for c, i in coups
    )
    if peut_finir_tour(partie) and valeur > seuil and partie["pioche"]:
        return ("fin",)
    return ("jouer", carte, index_pile)


def jouer_ia(partie, seuil=SEUIL_IA):
    """Applique une décision de l'IA. Retourne l'action effectuée (ou None)."""
    action = coup_ia(partie, seuil)
    if action is None:
        return None
    if action[0] == "jouer":
        jouer(partie, action[1], action[2])
    else:
        fin_tour(partie)
    return action
