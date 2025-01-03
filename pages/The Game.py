import streamlit as st
import random

# Configuration de la page Streamlit
st.set_page_config(
    page_title="The Game",
    page_icon="🎮",
    layout="centered"
)

# Styles CSS personnalisés
st.markdown("""
    <style>
        .card {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
        }
        .pile-ascending {
            color: #28a745;
        }
        .pile-descending {
            color: #dc3545;
        }
        .stButton>button {
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# Initialisation des piles et du jeu
def init_game():
    piles = {
        "↗️ Pile ascendante 1": [1],
        "↗️ Pile ascendante 2": [1],
        "↙️ Pile descendante 1": [100],
        "↙️ Pile descendante 2": [100]
    }
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
        if any(is_valid_move(card, piles[key], ascending="↗️" in key) for key in piles):
            return True
    return False

# Initialisation de la partie
if "game_state" not in st.session_state:
    st.session_state.show_rules = True
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
st.title("🎮 The Game")

# Règles du jeu (affichables/masquables)
with st.expander("📖 Règles du jeu", expanded=st.session_state.show_rules):
    st.markdown("""
    ### Comment jouer
    1. Vous devez jouer au moins 2 cartes par tour
    2. Sur les piles ascendantes (↗️), jouez des cartes plus grandes
    3. Sur les piles descendantes (↙️), jouez des cartes plus petites
    4. Vous pouvez jouer une carte 10 au-dessus ou en-dessous de la dernière carte
    5. Gagnez en jouant toutes vos cartes !
    """)
    st.session_state.show_rules = False

# Affichage des piles en colonnes
col1, col2 = st.columns(2)

with col1:
    st.subheader("Piles ascendantes")
    for pile_name, pile in piles.items():
        if "↗️" in pile_name:
            st.markdown(f"""
                <div class='card pile-ascending'>
                    <h3>{pile_name}</h3>
                    <h2>{pile[-1]}</h2>
                </div>
            """, unsafe_allow_html=True)

with col2:
    st.subheader("Piles descendantes")
    for pile_name, pile in piles.items():
        if "↙️" in pile_name:
            st.markdown(f"""
                <div class='card pile-descending'>
                    <h3>{pile_name}</h3>
                    <h2>{pile[-1]}</h2>
                </div>
            """, unsafe_allow_html=True)

# Main du joueur
st.header("🃏 Votre main")
st.write(f"Cartes: {', '.join(map(str, sorted(hand)))}")

# Gestion de la sélection dans session_state
if "selected_card" not in st.session_state:
    st.session_state.selected_card = None
if "selected_pile" not in st.session_state:
    st.session_state.selected_pile = None

# Affichage des cartes avec pills
st.write("Choisissez une carte:")
selected_card = st.pills("Cartes disponibles", options=[str(card) for card in sorted(hand)], key="card_pills")
if selected_card:
    st.session_state.selected_card = int(selected_card)

# Affichage des piles avec pills
st.write("Choisissez une pile:")
pile_options = [f"{pile_name} ({pile_values[-1]})" for pile_name, pile_values in piles.items()]
selected_pile = st.pills("Piles disponibles", options=pile_options, key="pile_pills")
if selected_pile:
    st.session_state.selected_pile = selected_pile.split(" (")[0]

# Bouton pour jouer la carte
if st.session_state.selected_card and st.session_state.selected_pile:
    if st.button("Jouer la carte sélectionnée"):
        ascending = "↗️" in st.session_state.selected_pile
        if is_valid_move(st.session_state.selected_card, piles[st.session_state.selected_pile], ascending):
            play_card(st.session_state.selected_card, st.session_state.selected_pile, piles)
            hand.remove(st.session_state.selected_card)
            # Recharger la main
            if deck and len(hand) < 6:
                hand.append(deck.pop())
            st.success(f"Carte {st.session_state.selected_card} jouée avec succès !")
            # Réinitialiser les sélections
            st.session_state.selected_card = None
            st.session_state.selected_pile = None
        else:
            st.error("❌ Mouvement non valide. Essayez une autre combinaison.")

# Informations sur l'état du jeu
col5, col6 = st.columns(2)

with col5:
    st.info(f"🎴 Cartes restantes dans le deck: {len(deck)}")

with col6:
    st.info(f"✋ Cartes dans votre main: {len(hand)}")

# Vérification des conditions de fin
if not has_valid_moves(hand, piles):
    st.error("😔 Aucun mouvement possible. Partie terminée !")
    if st.button("Nouvelle partie"):
        del st.session_state.game_state
        st.rerun()

if not deck and not hand:
    st.success("🎉 Félicitations, vous avez gagné !")
    if st.button("Nouvelle partie"):
        del st.session_state.game_state
        st.rerun()