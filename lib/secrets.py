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
