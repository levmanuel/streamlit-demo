import streamlit as st

def generate_heart(text):
    # Génère le motif en forme de cœur avec le texte fourni
    heart_pattern = '\n'.join(
        [''.join(
            [(text[(x - y) % len(text)]  # Sélectionne le caractère en fonction de x et y
              if ((x * 0.05) ** 2 + (y * 0.1) ** 2 - 1) ** 3 - (x * 0.05) ** 2 * (y * 0.1) ** 3 <= 0
              else ' ')  # Crée des espaces pour l'extérieur du cœur
             for x in range(-30, 30)])  # Largeur du cœur
         for y in range(15, -15, -1)]   # Hauteur du cœur
    )
    return heart_pattern

# Interface utilisateur Streamlit
st.title("Motif en forme de cœur personnalisé")

# Entrée de l'utilisateur pour le texte à afficher
user_input = st.text_input("Entrez le texte à afficher dans le cœur :", "Essai")

# Génère le motif avec le texte fourni
heart_text = generate_heart(user_input)

# Affiche le motif avec un bloc de code pour un alignement plus stable
st.text(heart_text)

print(generate_heart("Audit"))