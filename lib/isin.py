"""Validation des codes ISIN (Luhn mod 10 après transcodage des lettres)."""
import string

# A=10, B=11, ..., Z=35
LETTER_VALUES = {c: str(ord(c) - ord("A") + 10) for c in string.ascii_uppercase}


def _transcode(isin):
    return "".join(LETTER_VALUES.get(c, c) for c in isin)


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
    """Retourne (valide, message_erreur) ; message_erreur vaut None si valide."""
    code = code.strip().upper()

    error = _validate_format(code)
    if error:
        return False, error

    # Luhn mod 10 depuis la droite (clé de contrôle incluse)
    total = 0
    for i, d in enumerate(reversed(_transcode(code))):
        n = int(d)
        if i % 2 == 1:  # doubler un chiffre sur deux depuis la droite
            n *= 2
            if n > 9:
                n -= 9
        total += n

    if total % 10 != 0:
        return False, "La clé de contrôle est invalide."
    return True, None
