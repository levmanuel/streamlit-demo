"""Le catalogue de l'accueil doit rester synchronisé avec le dossier pages/."""
from pathlib import Path

from lib.catalogue import DEMOS, PAGES_HORS_CATALOGUE

PAGES = Path(__file__).resolve().parent.parent / "pages"


def _fichiers_catalogue():
    return [f for section in DEMOS for _titre, f, _desc in section["items"]]


def test_chaque_entree_a_sa_page():
    for fichier in _fichiers_catalogue():
        assert (PAGES / fichier).is_file(), f"page manquante : {fichier}"


def test_chaque_page_est_listee():
    presentes = {p.name for p in PAGES.glob("*.py")}
    assert presentes == set(_fichiers_catalogue()) | PAGES_HORS_CATALOGUE


def test_pas_de_doublon():
    fichiers = _fichiers_catalogue()
    assert len(fichiers) == len(set(fichiers))
