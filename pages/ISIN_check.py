import streamlit as st

from lib.isin import isin_check

# --- UI ---
st.title("ISIN Code Validator")
st.write("Entrez un code ISIN pour vérifier sa validité.")
st.caption("Format : 2 lettres (pays ISO) + 9 caractères alphanumériques (NSIN) + 1 chiffre (clé)")

user_input = st.text_input("Code ISIN :", "US0378331005", max_chars=12)

if user_input:
    is_valid, message = isin_check(user_input)
    if is_valid:
        st.success(f"✅ Le code ISIN **{user_input.upper()}** est valide.")
    else:
        st.error(f"❌ Code invalide — {message}")
