import pytest

from lib.isin import isin_check


@pytest.mark.parametrize("code", ["US0378331005", "FR0000120271", "GB0002634946", " us0378331005 "])
def test_codes_valides(code):
    assert isin_check(code) == (True, None)


def test_cle_invalide():
    ok, msg = isin_check("US0378331006")
    assert not ok and "clé" in msg


@pytest.mark.parametrize("code", ["", "US037833100", "US03783310055", "120378331005", "US037833100X", "US03783-1005"])
def test_format_invalide(code):
    ok, msg = isin_check(code)
    assert not ok and msg
