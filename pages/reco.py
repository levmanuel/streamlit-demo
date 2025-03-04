import streamlit as st
import requests
import json
import re

# Configuration Mistral
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_API_KEY = st.secrets["api"]["MISTRAL_API_KEY"]
MODEL = "mistral-medium"

# Fonction pour appeler l'API Mistral
def call_mistral(prompt, prompt_reco):
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}
    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": prompt_reco}, {"role": "user", "content": prompt}],
        "temperature": 0.7,
    }
    try:
        response = requests.post(MISTRAL_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Erreur API: {e}"

def extract_score(response_text):
    matches = re.findall(r"(\d+)/10", response_text)  # Trouver tous les scores
    scores = [int(m) for m in matches if m.isdigit()] if matches else []
    
    if len(scores) > 3:  # Vérification pour éviter un mauvais calcul
        return round(sum(scores) / len(scores), 1)  # Moyenne arrondie à 1 décimale
    return "N/A"

# Interface Streamlit
st.title("Évaluation de Recommandation d'Audit")

with st.expander("Prompt Detail"):
    prompt_reco = st.text_area("", "Nous sommes en 2025. Vous êtes un auditeur expérimenté et exigeant. Votre rôle est d’évaluer rigoureusement un constat et une recommandation d’audit en fonction des critères suivants :\n"
            "- **Clarté et pertinence du constat** :\n"
            "  - **8-10** : Factuel, précis, basé sur des preuves solides, appuyé par des références réglementaires ou procédurales.\n"
            "  - **4-7** : Compréhensible mais imprécis, manque de références ou d'éléments factuels.\n"
            "  - **0-3** : Flou, subjectif, sans preuve tangible.\n"
            "\n"
            "- **Cohérence entre le constat et la recommandation** :\n"
            "  - **8-10** : Logique, réaliste et directement liée au constat.\n"
            "  - **4-7** : Relation existante mais manque de clarté sur la faisabilité.\n"
            "  - **0-3** : Décalée ou inapplicable.\n"
            "\n"
            "- **Pertinence des délais** :\n"
            "  - **8-10** : Délais réalistes, adaptés aux ressources et à l’urgence, et **n’excédant pas un an**.\n"
            "  - **4-7** : Délais justifiés mais légèrement longs ou non détaillés.\n"
            "  - **0-3** : Délais irréalistes ou dépassant un an sans justification.\n"
            "\n"
            "- **Identification claire du responsable de mise en oeuvre de la recommandation** :\n"
            "  - **8-10** : Responsable clairement désigné (nom, rôle, contact) et cohérent avec la criticité.\n"
            "  - **4-7** : Responsable indiqué mais manque de précision.\n"
            "  - **0-3** : Pas de responsable identifié ou inapproprié.\n"
            "\n"
            "- **Pertinence du niveau de criticité** :\n"
            "  - **8-10** : Niveau cohérent avec l’impact du constat (Niveau 1 : urgent, Niveau 2 : moyen, Niveau 3 : conseil).\n"
            "  - **4-7** : Niveau de criticité correct mais manque d’explication.\n"
            "  - **0-3** : Criticité incohérente ou absente.\n"
            "\n"
            "- **Définition des livrables** :\n"
            "  - **8-10** : Clairs, mesurables, permettent de valider efficacement l’implémentation.\n"
            "  - **4-7** : Livrables présents mais imprécis ou difficilement mesurables.\n"
            "  - **0-3** : Livrables absents ou inutilisables.\n"
            "\n"
            "Fournissez une **analyse détaillée** et un **score global de 0 à 10**, avec une justification précise pour chaque critère.")

constat = st.text_area("Constat", "Les contrôles d'accès aux données sensibles ne sont pas documentés systématiquement, ce qui pourrait conduire à des accès non autorisés.")
recommandation = st.text_area("Recommandation", "Mettre en place une procédure formelle de documentation et de revue périodique des droits d'accès aux données sensibles.")
date_realisation = st.text_input("Date de réalisation", "2035-12-31")
criticite = st.selectbox("Niveau de criticité", ["1 - Urgent", "2 - Moyen", "3 - Conseil"])
responsable = st.text_input("Responsable", "Alice Dupont, stagiaire IT")
livrables = st.text_area("Livrables", 
"""- Procédure documentée de gestion des droits d'accès
- Tableau de suivi des revues trimestrielles
- Rapport d'audit interne validant l'implémentation
""")

if st.button("Évaluer"):
    recommendation = {
        "constat": constat,
        "recommandation": recommandation,
        "date_realisation": date_realisation,
        "Niveau de criticité": criticite,
        "responsable": responsable,
        "livrables": livrables.split("\n"),
    }
    prompt = json.dumps(recommendation, indent=2, ensure_ascii=False)
    response_text = call_mistral(prompt, prompt_reco)    
    score = extract_score(response_text)
    st.subheader("Résultats")
    st.write(f"**Score Global : {score}/10**")
    st.write("### Analyse détaillée")
    st.write(response_text)