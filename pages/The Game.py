import streamlit as st
import random
import time
from streamlit.components.v1 import html

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
        .auto-play-status {
            color: #4a4a4a;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
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
        for pile_name in piles:
            ascending = "↗️" in pile_name
            if is_valid_move(card, piles[pile_name], ascending):
                return True
    return False

def update_game_state(card, pile_key):
    """Mise à jour de l'état du jeu après avoir joué une carte"""
    game_state = st.session_state.game_state
    game_state["piles"][pile_key].append(card)
    game_state["hand"].remove(card)
    
    if game_state["deck"] and len(game_state["hand"]) < 6:
        game_state["hand"].append(game_state["deck"].pop())
    
    game_state["moves_this_turn"] += 1
    st.session_state.game_state = game_state

def end_turn():
    """Termine le tour en cours"""
    game_state = st.session_state.game_state
    game_state["moves_this_turn"] = 0
    game_state["turn_number"] += 1

def ai_make_move():
    """Fait jouer l'IA automatiquement"""
    game_state = st.session_state.game_state
    hand = game_state["hand"]
    piles = game_state["piles"]
    
    # Trouver tous les mouvements valides
    valid_moves = []
    for card in hand:
        for pile_name in piles:
            ascending = "↗️" in pile_name
            if is_valid_move(card, piles[pile_name], ascending):
                valid_moves.append((card, pile_name))
    
    if valid_moves:
        # Choisir un mouvement aléatoire
        card, pile_name = random.choice(valid_moves)
        update_game_state(card, pile_name)
        return True
    return False

# Initialisation de l'état du jeu
if "game_state" not in st.session_state:
    st.session_state.show_rules = True
    piles, deck = init_game()
    hand = [deck.pop() for _ in range(6)]
    st.session_state.game_state = {
        "piles": piles,
        "deck": deck,
        "hand": hand,
        "moves_this_turn": 0,
        "turn_number": 1
    }
    st.session_state.game_over = False
    st.session_state.auto_play = False

# Chargement de l'état
game_state = st.session_state.game_state
piles = game_state["piles"]
deck = game_state["deck"]
hand = game_state["hand"]

# Interface utilisateur
st.title("🎮 The Game - Mode Auto-play")

# Contrôles d'auto-play
col1, col2, col3 = st.columns(3)
with col1:
    auto_play = st.checkbox("Activer l'auto-play", key="auto_play")
with col2:
    ai_speed = st.slider("Vitesse (s)", 0.1, 2.0, 0.5, key="ai_speed")
with col3:
    if st.button("Arrêter l'auto-play"):
        st.session_state.auto_play = False
        st.rerun()

# Gestion de l'auto-play
if st.session_state.auto_play and not st.session_state.game_over:
    if has_valid_moves(hand, piles):
        if ai_make_move():
            # Rechargement automatique après délai
            delay = int(st.session_state.ai_speed * 1000)
            js = f"""
            <script>
                setTimeout(function(){{
                    window.location.reload();
                }}, {delay});
            </script>
            """
            html(js)
    else:
        if game_state["moves_this_turn"] >= 2:
            end_turn()
            st.rerun()
        else:
            st.session_state.game_over = True

# Affichage des piles
col_left, col_right = st.columns(2)
with col_left:
    st.subheader("Piles ascendantes ↗️")
    for name, pile in piles.items():
        if "↗️" in name:
            st.markdown(f"""
                <div class='card pile-ascending'>
                    <h3>{name}</h3>
                    <h2>{pile[-1]}</h2>
                </div>
            """, unsafe_allow_html=True)

with col_right:
    st.subheader("Piles descendantes ↙️")
    for name, pile in piles.items():
        if "↙️" in name:
            st.markdown(f"""
                <div class='card pile-descending'>
                    <h3>{name}</h3>
                    <h2>{pile[-1]}</h2>
                </div>
            """, unsafe_allow_html=True)

# Informations de partie
st.markdown(f"""
    <div class='auto-play-status' style='background-color: {"#e6f4ff" if st.session_state.auto_play else "#ffe6e6"}'>
        Tour {game_state['turn_number']} - Cartes jouées ce tour: {game_state['moves_this_turn']}/2
        <br>Cartes restantes: {len(deck)} dans le deck • {len(hand)} en main
    </div>
""", unsafe_allow_html=True)

# Gestion de fin de partie
if st.session_state.game_over or not has_valid_moves(hand, piles):
    st.error("💀 Partie terminée - Aucun mouvement possible !")
    if st.button("Nouvelle partie"):
        del st.session_state.game_state
        st.rerun()

if not deck and not hand:
    st.success("🎉 Félicitations, vous avez gagné !")
    if st.button("Nouvelle partie"):
        del st.session_state.game_state
        st.rerun()