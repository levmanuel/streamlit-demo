import streamlit as st
import random

# Initialisation des piles et du jeu
def init_game():
    piles = {"asc1": [1], "asc2": [1], "desc1": [100], "desc2": [100]}
    deck = list(range(2, 100))
    random.shuffle(deck)
    return piles, deck

# Vérifie si une carte peut être jouée sur une pile
def is_valid_move(card, pile, ascending=True):
    top_card = pile[-1]
    if ascending:
        return card > top_card or card == top_card - 10
    else:
        return card < top_card or card == top_card + 10

# Jouer une carte
def play_card(card, pile_key, piles):
    piles[pile_key].append(card)

# Vérifie si le joueur a encore des mouvements possibles
def has_valid_moves(hand, piles):
    for card in hand:
        if any(is_valid_move(card, piles[key], ascending=(key.startswith("asc"))) for key in piles):
            return True
    return False

# Initialisation Streamlit
if "game_state" not in st.session_state:
    piles, deck = init_game()
    hand_size = 6
    hand = [deck.pop() for _ in range(hand_size)]
    st.session_state.game_state = {"piles": piles, "deck": deck, "hand": hand}

# Chargement de l'état du jeu
game_state = st.session_state.game_state
piles = game_state["piles"]
deck = game_state["deck"]
hand = game_state["hand"]

# Interface
st.title("The Game avec Streamlit")

st.header("Piles")
for pile_name, pile in piles.items():
    st.write(f"{pile_name}: {pile[-1]}")

st.header("Votre main")
st.write("Cartes:", hand)

# Actions de jeu
st.subheader("Jouer une carte")
selected_card = st.selectbox("Choisissez une carte", hand)
selected_pile = st.selectbox("Choisissez une pile", list(piles.keys()))
if st.button("Jouer la carte"):
    ascending = selected_pile.startswith("asc")
    if is_valid_move(selected_card, piles[selected_pile], ascending):
        play_card(selected_card, selected_pile, piles)
        hand.remove(selected_card)

        # Recharger la main
        if deck and len(hand) < 6:
            hand.append(deck.pop())
    else:
        st.error("Mouvement non valide. Essayez encore.")

# Vérifier les conditions de fin
if not has_valid_moves(hand, piles):
    st.warning("Aucun mouvement possible. Partie terminée !")
    st.stop()

if not deck and not hand:
    st.success("Félicitations, vous avez gagné !")
    st.stop()

# Afficher le nombre de cartes restantes dans le deck
st.subheader("Cartes restantes dans le deck")
st.write(len(deck))