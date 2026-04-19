import streamlit as st
import string

# Constante définie une fois : A=10, B=11, ..., Z=35
LETTER_VALUES = {c: str(ord(c) - ord('A') + 10) for c in string.ascii_uppercase}


def _transcode(isin):
    return ''.join(LETTER_VALUES.get(c, c) for c in isin)


def _validate_format(code):
    if len(code) != 12:
        return f"Un code ISIN doit contenir exactement 12 caractères (reçu : {len(code)})."
    if not code[:2].isalpha():
        return "Les 2 premiers caractères doivent être des lettres (code pays ISO)."
    if not code[2:11].isalnum():
        return "Les caractères 3 à 11 doivent être alphanumériques (NSIN)."
    if not code[11].isdigit():
        return "Le dernier caractère doit être un chiffre (clé de contrôle)."
    return None


def isin_check(code):
    code = code.strip().upper()

    error = _validate_format(code)
    if error:
        return False, error

    digits = _transcode(code)

    # Luhn mod 10 depuis la droite (check digit inclus)
    total = 0
    for i, d in enumerate(reversed(digits)):
        n = int(d)
        if i % 2 == 1:  # doubler un chiffre sur deux depuis la droite
            n *= 2
            if n > 9:
                n -= 9
        total += n

    if total % 10 != 0:
        return False, "La clé de contrôle est invalide."
    return True, None


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
