import math

import pytest

from lib import lcr as c


def test_stresser():
    assert c.stresser(20, 0) == 20
    assert c.stresser(20, 50) == 30
    assert c.stresser(20, -100) == 0


def test_valeurs_par_defaut_de_la_page():
    # HQLA 20, Outflows 45, Inflows 25 : inflows non cappés (plafond 33,75)
    assert c.net_outflows(45, 25) == 20
    assert c.lcr(20, 45, 25) == 100.0


def test_inflows_cappes():
    assert c.inflows_cappes(40, 100) == 30
    assert c.net_outflows(40, 100) == 10


def test_lcr_infini_si_sorties_nettes_nulles():
    assert math.isinf(c.lcr(10, 0, 0))


def test_simulation():
    jours, outflows, lcrs = c.simulation(20, 45, 25, 10, jours=3)
    assert jours == [1, 2, 3]
    assert outflows == [49.5, 54.45, 59.9]
    assert lcrs[0] == pytest.approx(100 * 20 / (49.5 - 25), abs=0.1)
    assert lcrs[0] > lcrs[1] > lcrs[2]


def test_simulation_sans_hausse_est_constante():
    _, outflows, lcrs = c.simulation(20, 45, 25, 0, jours=5)
    assert set(outflows) == {45} and set(lcrs) == {100.0}
