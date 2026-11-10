import random

import pytest

from lib import the_game as g


def partie(seed=0):
    return g.nouvelle_partie(random.Random(seed))


def test_nouvelle_partie_distribue_98_cartes_uniques():
    p = partie()
    assert len(p["main"]) == g.TAILLE_MAIN
    assert sorted(p["main"] + p["pioche"]) == list(range(2, 100))
    assert [pile["cartes"] for pile in p["piles"]] == [[1], [1], [100], [100]]


def test_regles_de_pose_et_saut_de_dix():
    asc = {"ascendante": True, "cartes": [1, 40]}
    desc = {"ascendante": False, "cartes": [100, 40]}
    assert g.coup_valide(41, asc) and not g.coup_valide(39, asc)
    assert g.coup_valide(30, asc) and g.est_saut(30, asc)
    assert g.coup_valide(39, desc) and not g.coup_valide(41, desc)
    assert g.coup_valide(50, desc) and g.est_saut(50, desc)
    assert g.cout(30, asc) == -10 and g.cout(45, asc) == 5


def test_on_ne_repioche_qu_en_fin_de_tour_apres_deux_cartes():
    p = partie()
    a, b = p["main"][0], p["main"][1]
    g.jouer(p, a, 0)
    assert len(p["main"]) == g.TAILLE_MAIN - 1
    assert not g.peut_finir_tour(p)
    with pytest.raises(ValueError):
        g.fin_tour(p)
    g.jouer(p, b, 0)
    g.fin_tour(p)
    assert len(p["main"]) == g.TAILLE_MAIN
    assert p["tour"] == 2 and p["coups_ce_tour"] == []


def test_coup_invalide_refuse():
    p = partie()
    p["piles"][0]["cartes"].append(99)
    carte = next(c for c in p["main"] if c != 89)
    with pytest.raises(ValueError):
        g.jouer(p, carte, 0)


def test_annuler_restaure_la_main_et_la_pile():
    p = partie()
    avant = (list(p["main"]), [list(x["cartes"]) for x in p["piles"]])
    g.jouer(p, p["main"][3], 1)
    assert g.annuler(p)
    assert (p["main"], [x["cartes"] for x in p["piles"]]) == avant
    assert not g.annuler(p)


def test_une_seule_carte_suffit_quand_la_pioche_est_vide():
    p = partie()
    p["pioche"] = []
    assert g.min_coups(p) == 1


def test_statut_perdu_gagne():
    p = partie()
    for pile in p["piles"]:
        pile["cartes"].append(99 if pile["ascendante"] else 2)
    p["main"] = [50, 51]
    assert g.statut(p) == g.PERDUE
    assert g.coup_ia(p) is None
    p["main"], p["pioche"] = [], []
    assert g.statut(p) == g.GAGNEE


def test_bloque_apres_le_minimum_n_est_pas_une_defaite():
    p = partie()
    p["coups_ce_tour"] = [(10, 0), (11, 0)]
    for pile in p["piles"]:
        pile["cartes"].append(99 if pile["ascendante"] else 2)
    p["main"] = [50]
    assert g.statut(p) == g.EN_COURS
    assert g.coup_ia(p) == ("fin",)


def test_ia_privilegie_le_saut():
    p = partie()
    p["piles"][0]["cartes"].append(40)
    p["main"] = [30, 41, 60]
    assert g.coup_ia(p) == ("jouer", 30, 0)


def test_ia_termine_toujours_la_partie_sans_coup_illegal():
    for seed in range(50):
        p = partie(seed)
        for _ in range(500):
            if g.statut(p) != g.EN_COURS:
                break
            assert g.jouer_ia(p) is not None
        assert g.statut(p) in (g.GAGNEE, g.PERDUE)
        poses = sum(len(x["cartes"]) - 1 for x in p["piles"])
        assert poses + g.cartes_restantes(p) == 98
