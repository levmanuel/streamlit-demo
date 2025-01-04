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

# Fonctions du jeu
def init_game():
    """Initialise une nouvelle partie"""
    piles = {
        "↗️ Pile ascendante 1": [1],
        "↗️ Pile ascendante 2": [1],
        "↙️ Pile descendante 1": [100],
        "↙️ Pile descendante 2": [100]
    }
    deck = list(range(2, 100))
    random.shuffle(deck)
    return piles, deck

def is_valid_move(card, pile, ascending=True):
    """Vérifie si une carte peut être jouée sur une pile"""
    top_card = pile[-1]
    if ascending:
        return card > top_card or card == top_card - 10
    else:
        return card < top_card or card == top_card + 10

def has_valid_moves(hand, piles):
    """Vérifie si le joueur a encore des mouvements possibles"""
    for card in hand:
        if any(is_valid_move(card, piles[key], ascending="↗️" in key) for key in piles):
            return True
    return False

def update_game_state(card, pile_key):
    """Mise à jour de l'état du jeu après avoir joué une carte"""
    game_state = st.session_state.game_state
    # Jouer la carte
    game_state["piles"][pile_key].append(card)
    game_state["hand"].remove(card)
    # Piocher une nouvelle carte si possible
    if game_state["deck"] and len(game_state["hand"]) < 6:
        game_state["hand"].append(game_state["deck"].pop())
    # Incrémenter le compteur de mouvements
    game_state["moves_this_turn"] += 1
    # Mettre à jour l'état
    st.session_state.game_state = game_state

# Initialisation de l'état du jeu
if "game_state" not in st.session_state:
    st.session_state.show_rules = True
    piles, deck = init_game()
    hand_size = 6
    hand = [deck.pop() for _ in range(hand_size)]
    st.session_state.game_state = {
        "piles": piles,
        "deck": deck,
        "hand": hand,
        "moves_this_turn": 0,
        "turn_number": 1
    }

# Chargement de l'état du jeu
game_state = st.session_state.game_state
piles = game_state["piles"]
deck = game_state["deck"]
hand = game_state["hand"]

# Interface utilisateur
st.title("🎮 The Game")

# Règles du jeu dans un expander
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

# Affichage des piles
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

# Section de jeu
st.subheader("🎯 Jouer une carte")

# Gestion de la sélection
if "selected_card" not in st.session_state:
    st.session_state.selected_card = None
if "selected_pile" not in st.session_state:
    st.session_state.selected_pile = None

# Sélection de la carte avec pills
st.write("Choisissez une carte:")
selected_card = st.pills("Cartes disponibles", options=[str(card) for card in sorted(hand)], key="card_pills")
if selected_card:
    st.session_state.selected_card = int(selected_card)

# Sélection de la pile avec pills
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
            update_game_state(st.session_state.selected_card, st.session_state.selected_pile)
            st.success(f"Carte {st.session_state.selected_card} jouée avec succès !")
            st.session_state.selected_card = None
            st.session_state.selected_pile = None
            st.rerun()
        else:
            st.error("❌ Mouvement non valide. Essayez une autre combinaison.")

# Informations sur l'état du jeu
col3, col4 = st.columns(2)
with col3:
    st.info(f"🎴 Cartes dans le deck: {len(deck)}")
with col4:
    st.info(f"✋ Cartes en main: {len(hand)}")

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