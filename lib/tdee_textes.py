"""Tous les textes du calculateur TDEE, regroupés pour faciliter une traduction."""

TITRE = "Calculateur TDEE"
INTRO = (
    "Estimez votre dépense énergétique journalière totale (TDEE), votre objectif "
    "calorique et vos macronutriments. Tous les calculs sont faits dans votre "
    "navigateur : aucune donnée n'est enregistrée."
)
AVERTISSEMENT = (
    "Ces valeurs sont des estimations, avec une marge d'erreur d'environ 10 % par "
    "rapport aux valeurs mesurées. Elles ne remplacent pas un avis médical."
)
MODE_AVANCE = "Mode avancé (modifier les coefficients)"

# --- Profil ---
PROFIL = "Profil"
SEXE = "Sexe"
SEXES = {"homme": "Homme", "femme": "Femme"}
UNITES = "Unités"
UNITES_OPTIONS = {"metrique": "Métrique (kg, cm)", "imperial": "Impérial (lb, ft + in)"}
AGE = "Âge (ans)"
POIDS_KG = "Poids (kg)"
POIDS_LB = "Poids (lb)"
TAILLE_CM = "Taille (cm)"
TAILLE_FT = "Taille (ft)"
TAILLE_IN = "Taille (in)"
EQUATION = "Équation du BMR"
EQUATIONS = {
    "mifflin": "Mifflin-St Jeor (recommandée)",
    "harris": "Harris-Benedict (révisée)",
}

# --- Activité ---
ACTIVITE = "Niveau d'activité"
ACTIVITE_NIVEAUX = {
    "sedentaire": ("Sédentaire", "peu ou pas d'exercice"),
    "leger": ("Légèrement actif", "exercice léger 1 à 3 jours par semaine"),
    "modere": ("Modérément actif", "exercice modéré 3 à 5 jours par semaine"),
    "tres_actif": ("Très actif", "exercice intense 6 à 7 jours par semaine"),
    "extreme": ("Extrêmement actif", "exercice très intense ou travail physique"),
}
MULTIPLICATEUR = "Multiplicateur « {niveau} »"
TEF_PART = "Part du TEF dans le TDEE (%)"

# --- Objectif ---
OBJECTIF = "Objectif de poids"
OBJECTIFS = {
    "perte_agressive": ("Perte de graisse agressive", "0,5–0,75 kg perdu par semaine"),
    "perte": ("Perte de graisse", "0,25–0,5 kg perdu par semaine"),
    "maintien": ("Maintien", "poids stable"),
    "gain_maigre": ("Gain musculaire maigre", "0,1–0,25 kg pris par semaine"),
    "prise_agressive": ("Prise de masse agressive", "0,25–0,5 kg pris par semaine"),
}
AJUSTEMENT = "Ajustement quotidien (kcal)"

# --- Macros ---
MACROS_TITRE = "Répartition des macronutriments"
MACROS_NOMS = ("Protéines", "Glucides", "Lipides")
MACROS_PCT = "{nom} (%)"
MACROS_KCAL_G = "kcal par gramme — {nom}"

# --- Résultats ---
R_BMR = "BMR"
R_TDEE = "TDEE"
R_OBJECTIF = "Objectif"
R_UNITE = "kcal/jour"
R_VARIATION = "Variation de poids estimée : {texte}"
R_REPARTITION = "Répartition du TDEE"
R_PARTS = {
    "bmr": "BMR (métabolisme de base)",
    "tef": "TEF (effet thermique des aliments)",
    "eat": "EAT (exercice)",
    "neat": "NEAT (activité hors exercice)",
}
R_PARTS_COURT = {"bmr": "BMR", "tef": "TEF", "eat": "EAT", "neat": "NEAT"}
R_COL_PART, R_COL_PCT, R_COL_KCAL = "Composante", "Part", "kcal"
R_MACROS = "Macronutriments"
R_GRAMMES = "{nom} : {grammes} g · {kcal} kcal ({pct} %)"
R_ALERTE_MACROS = "Les macronutriments totalisent {total} % au lieu de 100 %."
R_FORMULE = "Formule appliquée"
F_BMR_MIFFLIN = "BMR = 10 × {w} + 6,25 × {h} − 5 × {a} {signe} {c} = {bmr} kcal"
F_BMR_HARRIS = "BMR = {c0} + {c1} × {w} + {c2} × {h} − {c3} × {a} = {bmr} kcal"
F_TDEE = "TDEE = {bmr} × {mult} = {tdee} kcal"
F_OBJECTIF = "Objectif = {tdee} {signe} {ajust} = {objectif} kcal"
