"""Tests unitaires du calculateur TDEE (jeux de test T1 à T7 + robustesse)."""
import math

import pytest

from lib import tdee as t


def r(x):
    return int(round(x))


# --- T1 à T5 : BMR, TDEE, objectif ---------------------------------------

def test_t1_bmr_mifflin_homme():
    assert t.bmr("homme", 80, 178, 30, "mifflin") == pytest.approx(1767.5)
    assert r(t.bmr("homme", 80, 178, 30, "mifflin")) == 1768


def test_t2_tdee_moderement_actif():
    b = t.bmr("homme", 80, 178, 30, "mifflin")
    assert t.tdee(b, 1.55) == pytest.approx(2739.625)
    assert r(t.tdee(b, 1.55)) == 2740


def test_t3_objectif_et_variation():
    d = t.tdee(t.bmr("homme", 80, 178, 30, "mifflin"), 1.55)
    assert t.objectif(d, -500) == pytest.approx(2239.625)
    assert r(t.objectif(d, -500)) == 2240
    assert round(t.variation_hebdo(-500), 2) == -0.45


def test_t4_femme_sedentaire():
    b = t.bmr("femme", 60, 165, 28, "mifflin")
    assert b == pytest.approx(1330.25)
    assert r(t.tdee(b, 1.2)) == 1596


def test_t5_harris_benedict():
    b = t.bmr("homme", 80, 178, 30, "harris")
    assert b == pytest.approx(1844.034, abs=1e-3)
    assert r(b) == 1844
    assert r(t.tdee(b, 1.55)) == 2858


def test_harris_benedict_femme():
    b = t.bmr("femme", 60, 165, 28, "harris")
    assert b == pytest.approx(447.593 + 9.247 * 60 + 3.098 * 165 - 4.330 * 28)


# --- T6 : macros ----------------------------------------------------------

def test_t6_macros():
    g = t.macros(2200, (30, 40, 30), (4, 4, 9))
    assert [r(x["grammes"]) for x in g] == [165, 220, 73]
    assert [r(x["kcal"]) for x in g] == [660, 880, 660]


def test_macros_kcal_par_gramme_nul_ne_plante_pas():
    g = t.macros(2200, (30, 40, 30), (0, 4, 9))
    assert g[0]["grammes"] == 0


# --- T7 : maintien --------------------------------------------------------

def test_t7_maintien():
    goal = t.GOALS["maintien"]
    assert goal["min"] == goal["max"] == 0
    assert t.objectif(2740, t.ajustement_defaut("maintien")) == 2740
    assert t.variation_hebdo(0) == 0
    assert t.rythme_texte(0) == "poids stable"


def test_objectifs_plages_et_defauts():
    assert t.GOALS["perte"]["min"] == -500 and t.GOALS["perte"]["max"] == -300
    assert t.ajustement_defaut("perte") == -400
    for key, g in t.GOALS.items():
        assert g["min"] <= t.ajustement_defaut(key) <= g["max"]


# --- Répartition ----------------------------------------------------------

def test_repartition_totalise_100_et_positive():
    b = t.bmr("homme", 80, 178, 30, "mifflin")
    for lvl in t.ACTIVITY_LEVELS:
        rep = t.repartition(b, t.tdee(b, lvl["mult"]), 10, lvl["eat"])
        assert sum(rep.values()) == pytest.approx(100)
        assert all(v >= 0 for v in rep.values())


def test_repartition_neat_jamais_negatif():
    # BMR très proche du TDEE + TEF + EAT élevés : le reste serait négatif.
    rep = t.repartition(1000, 1050, 30, 28)
    assert rep["neat"] == 0
    assert sum(rep.values()) == pytest.approx(100)


def test_repartition_tdee_nul():
    rep = t.repartition(0, 0, 10, 15)
    assert all(math.isfinite(v) for v in rep.values())


# --- Macros liées ---------------------------------------------------------

def test_rebalance_total_100():
    for idx in range(3):
        for val in (0, 17, 55, 100):
            out = t.rebalance((30, 40, 30), idx, val)
            assert sum(out) == 100
            assert out[idx] == val
            assert all(0 <= x <= 100 for x in out)


def test_rebalance_proportionnel():
    assert t.rebalance((30, 40, 30), 0, 40) == (40, 34, 26)  # 60 restant réparti au prorata 40:30
    assert t.rebalance((100, 0, 0), 0, 40) == (40, 30, 30)  # partage égal si 0 restant


# --- Robustesse -----------------------------------------------------------

@pytest.mark.parametrize("val", [None, "", float("nan"), "abc"])
def test_bornes_valeurs_invalides(val):
    assert t.borner(val, 30, 300, 80) == 80


def test_bornes_hors_plage():
    assert t.borner(5, 30, 300, 80) == 30
    assert t.borner(9999, 30, 300, 80) == 300


# --- Unités ---------------------------------------------------------------

def test_conversions_unites():
    assert t.kg_to_lb(80) == pytest.approx(176.37, abs=0.01)
    assert t.lb_to_kg(t.kg_to_lb(80)) == pytest.approx(80)
    assert t.ft_in_to_cm(5, 10) == pytest.approx(177.8)
    ft, inch = t.cm_to_ft_in(178)
    assert (ft, inch) == (5, 10)
    assert t.cm_to_ft_in(182.9)[1] < 12  # pas de "5 ft 12 in"


# --- Formatage FR ---------------------------------------------------------

def test_format_fr():
    assert t.fmt_fr(1767.5) == "1 768"
    assert t.fmt_fr(2739.625) == "2 740"
    assert t.fmt_fr(-0.4545, 2) == "−0,45"
    assert t.fmt_fr(0.5, 2, signe=True) == "+0,50"
    assert t.fmt_fr(float("nan")) == "—"
