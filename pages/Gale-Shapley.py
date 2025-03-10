import streamlit as st
import pandas as pd

# Configuration de base
st.set_page_config(layout="wide")
st.title("🎮 Système de Matching Équipes/Joueurs")
st.markdown("Algorithme Gale-Shapley adapté pour les équipes esport")

# Données initiales
players = [f"Joueur {i+1}" for i in range(12)]
teams = [f"Équipe {i+1}" for i in range(3)]

# Section des préférences
with st.expander("🎮 Configurer les préférences", expanded=True):
    st.header("Préférences des Équipes (Coach)")
    team_cols = st.columns(3)
    team_prefs = {}
    
    for i, team in enumerate(teams):
        with team_cols[i]:
            team_prefs[team] = st.multiselect(
                f"{team} - Classement des joueurs",
                players,
                key=f"team_{team}"
            )
            if len(team_prefs[team]) != 12:
                st.error("⚠️ Classer tous les 12 joueurs")

    st.header("Préférences des Joueurs")
    player_cols = st.columns(4)
    player_prefs = {}

    for i, player in enumerate(players):
        with player_cols[i % 4]:
            player_prefs[player] = st.multiselect(
                f"{player} - Classement des équipes",
                teams,
                key=f"player_{player}"
            )
            if len(player_prefs[player]) != 3:
                st.error("⚠️ Classer toutes les 3 équipes")

# Algorithme Gale-Shapley adapté
def gale_shapley(team_prefs, player_prefs):
    proposals = {team: [] for team in teams}
    player_matches = {player: None for player in players}
    proposed = {team: set() for team in teams}

    while True:
        # Trouver les équipes avec places restantes
        active_teams = [t for t in teams if len(proposals[t]) < 4 and len(proposed[t]) < 12]
        if not active_teams:
            break

        for team in active_teams:
            # Trouver le prochain joueur non proposé
            for player in team_prefs[team]:
                if player not in proposed[team]:
                    proposed[team].add(player)
                    current_team = player_matches[player]
                    
                    if current_team is None:
                        proposals[team].append(player)
                        player_matches[player] = team
                        break
                    else:
                        # Comparer les préférences
                        if player_prefs[player].index(team) < player_prefs[player].index(current_team):
                            proposals[current_team].remove(player)
                            proposals[team].append(player)
                            player_matches[player] = team
                            break
                    if len(proposals[team]) == 4:
                        break
    return proposals, player_matches

# Exécution et résultats
if st.button("🔍 Lancer le Matching"):
    # Validation
    valid = all(len(v) == 12 for v in team_prefs.values()) and all(len(v) == 3 for v in player_prefs.values())
    
    if not valid:
        st.error("❌ Completez toutes les préférences avant de lancer le matching !")
    else:
        team_matches, player_matches = gale_shapley(team_prefs, player_prefs)
        
        # Affichage des résultats
        st.success("✅ Matching réussi !")
        
        st.subheader("Composition des Équipes")
        team_df = pd.DataFrame(
            [(team, ", ".join(matches)) for team, matches in team_matches.items()],
            columns=["Équipe", "Joueurs"]
        )
        st.table(team_df)
        
        st.subheader("Affectation des Joueurs")
        player_df = pd.DataFrame(
            [(player, team) for player, team in player_matches.items()],
            columns=["Joueur", "Équipe"]
        )
        st.table(player_df)