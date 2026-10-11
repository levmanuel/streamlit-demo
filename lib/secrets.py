"""Accès aux secrets Streamlit avec message d'erreur lisible."""
import streamlit as st


def mistral_api_key() -> str:
    """Renvoie la clé Mistral, ou affiche une erreur explicite et arrête la page."""
    try:
        return st.secrets["api"]["MISTRAL_API_KEY"]
    except (KeyError, FileNotFoundError):
        st.error(
            "Clé Mistral manquante : ajoutez `MISTRAL_API_KEY` dans la section `[api]` "
            "de `.streamlit/secrets.toml` (ou des secrets Streamlit Cloud)."
        )
        st.stop()


def exiger_mot_de_passe_diagnostic() -> None:
    """Protège la page de diagnostic : `[api] DIAGNOSTIC_PASSWORD` doit être défini
    dans les secrets, et le visiteur doit le saisir. Sinon la page est désactivée."""
    try:
        attendu = st.secrets["api"]["DIAGNOSTIC_PASSWORD"]
    except (KeyError, FileNotFoundError):
        st.warning(
            "Page désactivée : définissez `DIAGNOSTIC_PASSWORD` dans la section `[api]` "
            "des secrets pour l'activer."
        )
        st.stop()
    saisi = st.text_input("Mot de passe", type="password")
    if saisi != attendu:
        if saisi:
            st.error("Mot de passe incorrect.")
        st.stop()
