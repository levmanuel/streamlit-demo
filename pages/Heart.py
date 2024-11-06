import streamlit as st

def heart_pattern(text):
    # Répète le texte pour remplir le motif en cœur
    text_repeated = (text * 100)[:100]
    n = len(text_repeated)

    for row in range(6):
        for col in range(7 * n // 10):
            # Conditions pour dessiner les parties du cœur
            if ((row == 0 and col % 5 != 0) or 
                (row == 1 and col % 5 == 0) or 
                (row - col == 2) or 
                (row + col == 8)):
                # Affiche le caractère correspondant dans `text_repeated`
                print(text_repeated[(row * 7 + col) % n], end="")
            else:
                print(" ", end="")
        print()

# Interface utilisateur Streamlit
st.title("Motif en forme de cœur personnalisé")

# Entrée de l'utilisateur pour le texte à afficher
user_input = st.text_input("Entrez le texte à afficher dans le cœur :", "Essai")

# Génère le motif avec le texte fourni
heart_text = heart_pattern(user_input)

# Affiche le motif avec un bloc de code pour un alignement plus stable
st.text(heart_text)