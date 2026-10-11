"""Calculs du TDEE (dépense énergétique journalière) — fonctions pures.

Aucune dépendance à Streamlit : tout est testable seul. Poids en kg, taille
en cm, âge en années. Aucun arrondi intermédiaire : on arrondit à l'affichage.
"""
import math

# --- Constantes -----------------------------------------------------------

LIMITES = {"age": (15, 100), "poids": (30, 300), "taille": (120, 230)}
DEFAUTS = {"age": 30, "poids": 80.0, "taille": 178.0}

KCAL_PAR_KG = 7700  # le prototype retient 7 700 kcal/kg (≈ 3 500 kcal/lb)
TEF_DEFAUT = 10.0

# Niveaux d'activité : multiplicateur par défaut et part EAT (% du TDEE).
ACTIVITY_LEVELS = [
    {"key": "sedentaire", "mult": 1.2, "eat": 2},
    {"key": "leger", "mult": 1.375, "eat": 8},
    {"key": "modere", "mult": 1.55, "eat": 15},
    {"key": "tres_actif", "mult": 1.725, "eat": 22},
    {"key": "extreme", "mult": 1.9, "eat": 28},
]
ACTIVITE_DEFAUT = "modere"

# Objectifs : plage d'ajustement quotidien (kcal) et rythme typique.
GOALS = {
    "perte_agressive": {"min": -750, "max": -500, "defaut": -600},
    "perte": {"min": -500, "max": -300, "defaut": -400},
    "maintien": {"min": 0, "max": 0, "defaut": 0},
    "gain_maigre": {"min": 200, "max": 300, "defaut": 250},
    "prise_agressive": {"min": 400, "max": 600, "defaut": 500},
}
OBJECTIF_DEFAUT = "perte"

MACROS_PCT_DEFAUT = (30, 40, 30)  # protéines, glucides, lipides
MACROS_KCAL_DEFAUT = (4, 4, 9)


# --- Robustesse -----------------------------------------------------------

def borner(valeur, mini, maxi, defaut):
    """Convertit en float et borne ; vide / NaN / non numérique → défaut."""
    try:
        v = float(valeur)
    except (TypeError, ValueError):
        return defaut
    if not math.isfinite(v):
        return defaut
    return min(max(v, mini), maxi)


# --- BMR, TDEE, objectif ---------------------------------------------------

def bmr(sexe, poids, taille, age, equation="mifflin"):
    """BMR en kcal/jour. sexe : 'homme' | 'femme' ; equation : 'mifflin' | 'harris'."""
    homme = sexe == "homme"
    if equation == "harris":
        if homme:
            return 88.362 + 13.397 * poids + 4.799 * taille - 5.677 * age
        return 447.593 + 9.247 * poids + 3.098 * taille - 4.330 * age
    return 10 * poids + 6.25 * taille - 5 * age + (5 if homme else -161)


def tdee(bmr_value, multiplicateur):
    return bmr_value * multiplicateur


def objectif(tdee_value, ajustement):
    return tdee_value + ajustement


def variation_hebdo(ajustement):
    """Variation de poids estimée en kg/semaine (signée)."""
    return ajustement * 7 / KCAL_PAR_KG


def ajustement_defaut(goal_key):
    return GOALS[goal_key]["defaut"]


def rythme_texte(ajustement):
    if ajustement == 0:
        return "poids stable"
    return f"{fmt_fr(variation_hebdo(ajustement), 2, signe=True)} kg par semaine"


# --- Macronutriments -------------------------------------------------------

def macros(objectif_kcal, pourcentages, kcal_par_g):
    """Retourne [{'grammes', 'kcal'}] pour (protéines, glucides, lipides)."""
    out = []
    for pct, kcal_g in zip(pourcentages, kcal_par_g):
        kcal = objectif_kcal * pct / 100
        out.append({"kcal": kcal, "grammes": kcal / kcal_g if kcal_g > 0 else 0.0})
    return out


def rebalance(pourcentages, index, nouvelle_valeur):
    """Fixe la macro `index` à `nouvelle_valeur` et répartit le reste sur les
    deux autres au prorata de leurs valeurs (à parts égales si elles sont nulles).
    Le total vaut toujours 100."""
    nouvelle_valeur = int(min(max(round(nouvelle_valeur), 0), 100))
    autres = [i for i in range(3) if i != index]
    reste = 100 - nouvelle_valeur
    somme = sum(pourcentages[i] for i in autres)
    out = [0, 0, 0]
    out[index] = nouvelle_valeur
    if somme > 0:
        premier = int(round(reste * pourcentages[autres[0]] / somme))
    else:
        premier = reste // 2 + reste % 2
    out[autres[0]] = premier
    out[autres[1]] = reste - premier
    return tuple(out)


# --- Répartition du TDEE (illustrative) ------------------------------------

def repartition(bmr_value, tdee_value, tef_pct, eat_pct):
    """Parts BMR / TEF / EAT / NEAT en % du TDEE, normalisées à 100."""
    if tdee_value <= 0:
        return {"bmr": 0.0, "tef": 0.0, "eat": 0.0, "neat": 0.0}
    bmr_p = bmr_value / tdee_value * 100
    neat = max(0.0, 100 - bmr_p - tef_pct - eat_pct)
    parts = {"bmr": bmr_p, "tef": float(tef_pct), "eat": float(eat_pct), "neat": neat}
    total = sum(parts.values())
    return {k: v * 100 / total for k, v in parts.items()}


# --- Unités ------------------------------------------------------------------

KG_PAR_LB = 0.45359237
CM_PAR_IN = 2.54


def kg_to_lb(kg):
    return kg / KG_PAR_LB


def lb_to_kg(lb):
    return lb * KG_PAR_LB


def ft_in_to_cm(ft, inch):
    return (ft * 12 + inch) * CM_PAR_IN


def cm_to_ft_in(cm):
    total = int(round(cm / CM_PAR_IN))
    return total // 12, total % 12


# --- Formatage français ------------------------------------------------------

def fmt_fr(valeur, decimales=0, signe=False):
    """1767.5 → '1 768' (espace insécable) ; -0.45 → '−0,45'."""
    if valeur is None or not math.isfinite(valeur):
        return "—"
    s = f"{abs(valeur):,.{decimales}f}".replace(",", " ").replace(".", ",")
    if round(valeur, decimales) < 0:
        return "−" + s
    return ("+" + s) if signe else s
