import streamlit as st
import requests
import json
from datetime import date, timedelta

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_API_KEY = st.secrets["api"]["MISTRAL_API_KEY"]
MODEL = "mistral-large-latest"

CRITERES_LABELS = {
    "clarte_constat": "Clarté et pertinence du constat",
    "coherence": "Cohérence constat / recommandation",
    "delais": "Pertinence des délais",
    "responsable": "Identification du responsable",
    "criticite": "Pertinence du niveau de criticité",
    "livrables": "Définition des livrables",
}

DEFAULT_SYSTEM_PROMPT = (
    "Nous sommes en 2025. Vous êtes un auditeur expérimenté et exigeant. "
    "Votre rôle est d'évaluer rigoureusement un constat et une recommandation d'audit "
    "en fonction des critères suivants :\n"
    "\n"
    "- Clarté et pertinence du constat :\n"
    "  - 8-10 : Factuel, précis, basé sur des preuves solides, appuyé par des références réglementaires ou procédurales.\n"
    "  - 4-7 : Compréhensible mais imprécis, manque de références ou d'éléments factuels.\n"
    "  - 0-3 : Flou, subjectif, sans preuve tangible.\n"
    "\n"
    "- Cohérence entre le constat et la recommandation :\n"
    "  - 8-10 : Logique, réaliste et directement liée au constat.\n"
    "  - 4-7 : Relation existante mais manque de clarté sur la faisabilité.\n"
    "  - 0-3 : Décalée ou inapplicable.\n"
    "\n"
    "- Pertinence des délais :\n"
    "  - 8-10 : Délais réalistes, adaptés aux ressources et à l'urgence, et n'excédant pas un an.\n"
    "  - 4-7 : Délais justifiés mais légèrement longs ou non détaillés.\n"
    "  - 0-3 : Délais irréalistes ou dépassant un an sans justification.\n"
    "\n"
    "- Identification claire du responsable de mise en oeuvre de la recommandation :\n"
    "  - 8-10 : Responsable clairement désigné (nom, rôle, contact) et cohérent avec la criticité.\n"
    "  - 4-7 : Responsable indiqué mais manque de précision.\n"
    "  - 0-3 : Pas de responsable identifié ou inapproprié.\n"
    "\n"
    "- Pertinence du niveau de criticité :\n"
    "  - 8-10 : Niveau cohérent avec l'impact du constat (Niveau 1 : urgent, Niveau 2 : moyen, Niveau 3 : conseil).\n"
    "  - 4-7 : Niveau de criticité correct mais manque d'explication.\n"
    "  - 0-3 : Criticité incohérente ou absente.\n"
    "\n"
    "- Définition des livrables :\n"
    "  - 8-10 : Clairs, mesurables, permettent de valider efficacement l'implémentation.\n"
    "  - 4-7 : Livrables présents mais imprécis ou difficilement mesurables.\n"
    "  - 0-3 : Livrables absents ou inutilisables.\n"
    "\n"
    "Répondez UNIQUEMENT en JSON valide, sans texte avant ou après, selon ce schéma exact :\n"
    "{\n"
    '  "criteres": {\n'
    '    "clarte_constat": {"score": <0-10>, "justification": "<texte>"},\n'
    '    "coherence":      {"score": <0-10>, "justification": "<texte>"},\n'
    '    "delais":         {"score": <0-10>, "justification": "<texte>"},\n'
    '    "responsable":    {"score": <0-10>, "justification": "<texte>"},\n'
    '    "criticite":      {"score": <0-10>, "justification": "<texte>"},\n'
    '    "livrables":      {"score": <0-10>, "justification": "<texte>"}\n'
    "  },\n"
    '  "score_global": <moyenne arrondie à 1 décimale>,\n'
    '  "synthese": "<paragraphe de synthèse>"\n'
    "}"
)


def call_mistral(prompt, system_prompt):
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
    }
    response = requests.post(MISTRAL_API_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def parse_response(raw):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def validate_date(date_str):
    try:
        d = date.fromisoformat(date_str)
    except ValueError:
        return "Format de date invalide (attendu : AAAA-MM-JJ)."
    if d > date.today() + timedelta(days=365):
        return f"La date dépasse un an ({d}) — le critère 'délais' sera pénalisé."
    if d < date.today():
        return "La date de réalisation est dans le passé."
    return None


# --- UI ---
st.title("Évaluation de Recommandation d'Audit")

with st.expander("Prompt système (modifiable)"):
    system_prompt = st.text_area("", DEFAULT_SYSTEM_PROMPT, height=300)

constat = st.text_area(
    "Constat",
    "Les contrôles d'accès aux données sensibles ne sont pas documentés systématiquement, "
    "ce qui pourrait conduire à des accès non autorisés.",
)
recommandation = st.text_area(
    "Recommandation",
    "Mettre en place une procédure formelle de documentation et de revue périodique "
    "des droits d'accès aux données sensibles.",
)

date_realisation = st.text_input("Date de réalisation (AAAA-MM-JJ)", "2027-04-19")
date_warning = validate_date(date_realisation)
if date_warning:
    st.warning(date_warning)

criticite = st.selectbox("Niveau de criticité", ["1 - Urgent", "2 - Moyen", "3 - Conseil"])
responsable = st.text_input("Responsable", "Alice Dupont, stagiaire IT")
livrables = st.text_area(
    "Livrables",
    "- Procédure documentée de gestion des droits d'accès\n"
    "- Tableau de suivi des revues trimestrielles\n"
    "- Rapport d'audit interne validant l'implémentation",
)

if st.button("Évaluer"):
    recommendation = {
        "constat": constat,
        "recommandation": recommandation,
        "date_realisation": date_realisation,
        "niveau_criticite": criticite,
        "responsable": responsable,
        "livrables": [l.strip("- ").strip() for l in livrables.splitlines() if l.strip()],
    }
    prompt = json.dumps(recommendation, indent=2, ensure_ascii=False)

    with st.spinner("Analyse en cours…"):
        try:
            raw = call_mistral(prompt, system_prompt)
        except requests.exceptions.Timeout:
            st.error("L'API Mistral n'a pas répondu dans les 30 secondes.")
            st.stop()
        except requests.exceptions.RequestException as e:
            st.error(f"Erreur API : {e}")
            st.stop()

    result = parse_response(raw)

    if result is None:
        st.error("La réponse de l'API n'est pas au format JSON attendu.")
        st.code(raw)
        st.stop()

    st.subheader("Résultats")

    score_global = result.get("score_global", "N/A")
    color = "#28a745" if isinstance(score_global, (int, float)) and score_global >= 7 else \
            "#ffc107" if isinstance(score_global, (int, float)) and score_global >= 4 else "#dc3545"
    st.markdown(
        f"<h2 style='color:{color}'>Score global : {score_global}/10</h2>",
        unsafe_allow_html=True,
    )

    criteres = result.get("criteres", {})
    if criteres:
        st.subheader("Détail par critère")
        rows = []
        for key, label in CRITERES_LABELS.items():
            c = criteres.get(key, {})
            rows.append({"Critère": label, "Score": f"{c.get('score', '?')}/10", "Justification": c.get("justification", "")})
        st.table(rows)

    synthese = result.get("synthese")
    if synthese:
        st.subheader("Synthèse")
        st.write(synthese)
