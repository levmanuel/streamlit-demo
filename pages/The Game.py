import streamlit as st
import random
import time

st.set_page_config(
    page_title="The Game",
    page_icon="🎮",
    layout="centered"
)

st.markdown("""
    <style>
        .card {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
        }
        .pile-ascending { color: #28a745; }
        .pile-descending { color: #dc3545; }
        .stButton>button { width: 100%; }
        .game-status {
            color: #4a4a4a;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
""", unsafe_allow_html=True)


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


def is_valid_move(card, pile, ascending=True):
    top = pile[-1]
    if ascending:
        return card > top or card == top - 10
    else:
        return card < top or card == top + 10


def has_valid_moves(hand, piles):
    for card in hand:
        for pile_name, pile in piles.items():
            if is_valid_move(card, pile, ascending="↗️" in pile_name):
                return True
    return False


def update_game_state(card, pile_key):
    gs = st.session_state.game_state
    gs["piles"][pile_key].append(card)
    gs["hand"].remove(card)
    if gs["deck"] and len(gs["hand"]) < 6:
        gs["hand"].append(gs["deck"].pop())
    gs["moves_this_turn"] += 1
    st.session_state.game_state = gs


def end_turn():
    gs = st.session_state.game_state
    gs["moves_this_turn"] = 0
    gs["turn_number"] += 1
    st.session_state.game_state = gs  # FIX: persist state back


def ai_make_move():
    gs = st.session_state.game_state
    hand, piles = gs["hand"], gs["piles"]

    # Score moves: prefer smallest gap (jump-back = 0 = highest priority)
    scored = []
    for card in hand:
        for pile_name, pile in piles.items():
            ascending = "↗️" in pile_name
            if is_valid_move(card, pile, ascending):
                top = pile[-1]
                if ascending:
                    gap = card - top if card > top else 0
                else:
                    gap = top - card if card < top else 0
                scored.append((gap, card, pile_name))

    if scored:
        scored.sort(key=lambda x: x[0])
        _, card, pile_name = scored[0]
        update_game_state(card, pile_name)
        return True
    return False


# --- Initialization ---
if "game_state" not in st.session_state:
    piles, deck = init_game()
    hand = [deck.pop() for _ in range(6)]
    st.session_state.game_state = {
        "piles": piles,
        "deck": deck,
        "hand": hand,
        "moves_this_turn": 0,
        "turn_number": 1,
    }
    st.session_state.game_over = False
    st.session_state.auto_play = False
    st.session_state.selected_card = None


def reset_game():
    for key in ["game_state", "game_over", "auto_play", "selected_card"]:
        st.session_state.pop(key, None)


gs = st.session_state.game_state
piles = gs["piles"]
deck = gs["deck"]
hand = gs["hand"]
moves = gs["moves_this_turn"]
min_moves = 1 if not deck else 2

# Compute once per render
can_move = has_valid_moves(hand, piles)

st.title("🎮 The Game")

# --- Auto-play controls ---
col1, col2 = st.columns([1, 1])
with col1:
    auto_play = st.checkbox("Auto-play (IA)", key="auto_play")
with col2:
    if auto_play:
        st.slider("Vitesse (s)", 0.1, 2.0, 0.5, key="ai_speed")

# --- Auto-play loop ---
if st.session_state.auto_play and not st.session_state.game_over:
    if can_move:
        ai_make_move()
        time.sleep(st.session_state.get("ai_speed", 0.5))
        st.rerun()
    elif moves >= min_moves:
        end_turn()
        st.rerun()
    else:
        st.session_state.game_over = True

# --- Piles display ---
col_left, col_right = st.columns(2)
with col_left:
    st.subheader("Piles ascendantes ↗️")
    for name, pile in piles.items():
        if "↗️" not in name:
            continue
        st.markdown(f"""
            <div class='card pile-ascending'>
                <h3>{name}</h3>
                <h2>{pile[-1]}</h2>
            </div>
        """, unsafe_allow_html=True)
        sel = st.session_state.selected_card
        if not auto_play and sel is not None and is_valid_move(sel, pile, ascending=True):
            if st.button(f"Jouer {sel} ici", key=f"play_{name}"):
                update_game_state(sel, name)
                st.session_state.selected_card = None
                st.rerun()

with col_right:
    st.subheader("Piles descendantes ↙️")
    for name, pile in piles.items():
        if "↙️" not in name:
            continue
        st.markdown(f"""
            <div class='card pile-descending'>
                <h3>{name}</h3>
                <h2>{pile[-1]}</h2>
            </div>
        """, unsafe_allow_html=True)
        sel = st.session_state.selected_card
        if not auto_play and sel is not None and is_valid_move(sel, pile, ascending=False):
            if st.button(f"Jouer {sel} ici", key=f"play_{name}"):
                update_game_state(sel, name)
                st.session_state.selected_card = None
                st.rerun()

# --- Status bar ---
st.markdown(f"""
    <div class='game-status' style='background-color: {"#e6f4ff" if auto_play else "#f0f2f6"}'>
        Tour {gs['turn_number']} — Cartes jouées ce tour : {moves}/{min_moves} minimum
        <br>Cartes restantes : {len(deck)} dans le deck • {len(hand)} en main
    </div>
""", unsafe_allow_html=True)

# --- Manual play: hand + end turn ---
if not auto_play and not st.session_state.game_over:
    st.subheader("Votre main")
    if hand:
        cols = st.columns(len(hand))
        for i, card in enumerate(sorted(hand)):
            with cols[i]:
                is_selected = st.session_state.selected_card == card
                label = f"**[{card}]**" if is_selected else str(card)
                if st.button(label, key=f"card_{i}_{card}"):
                    st.session_state.selected_card = None if is_selected else card
                    st.rerun()

    if st.button("Fin de tour ✅", disabled=(moves < min_moves)):
        end_turn()
        st.session_state.selected_card = None
        st.rerun()

# --- Win condition ---
if not deck and not hand:
    st.success("🎉 Félicitations, vous avez gagné !")
    if st.button("Nouvelle partie", key="btn_win"):
        reset_game()
        st.rerun()

# --- Game over condition ---
elif st.session_state.game_over or (not can_move and moves < min_moves):
    st.error("💀 Partie terminée — Aucun mouvement possible !")
    if st.button("Nouvelle partie", key="btn_loss"):
        reset_game()
        st.rerun()
