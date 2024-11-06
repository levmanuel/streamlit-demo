import streamlit as st

def generate_heart(text):
    # Génère le motif en forme de cœur avec le texte fourni
    heart_pattern = '\n'.join(
        [''.join(
            [(text[(x - y) % len(text)]
              if ((x * 0.05) ** 2 + (y * 0.1) ** 2 - 1) ** 3 - (x * 0.05) ** 2 * (y * 0.1) ** 3 <= 0
              else ' ')
             for x in range(-30, 30)])
         for y in range(15, -15, -1)]
    )
    return heart_pattern

# Interface utilisateur Streamlit
st.title("Motif en forme de cœur personnalisé")

# Entrée de l'utilisateur pour le texte à afficher
user_input = st.text_input("Entrez le texte à afficher dans le cœur :", "YourName")

# Génère le motif avec le texte fourni
heart_text = generate_heart(user_input)

# Affiche le motif
st.code(heart_text, language="plaintext")