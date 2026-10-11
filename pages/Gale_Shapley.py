import streamlit as st
import pandas as pd

from lib.matching import gale_shapley

# Configuration de base
st.set_page_config(layout="wide")
st.title("🎮 Système de Matching Équipes/Joueurs v2")
st.markdown("Algorithme Gale-Shapley avec configuration dynamique")

# Configuration initiale avec colonnes
config_col1, config_col2 = st.columns(2)
with config_col1:
    num_teams = st.number_input("Nombre d'équipes", min_value=1, value=3, step=1)
with config_col2:
    num_players = st.number_input("Nombre total de joueurs", 
                                min_value=num_teams*2, 
                                value=12, 
                                step=num_teams,
                                help="Doit être un multiple du nombre d'équipes")

# Validation de la configuration
if num_players % num_teams != 0:
    st.error(f"❌ Le nombre de joueurs doit être un multiple du nombre d'équipes (actuellement {num_players % num_teams} reste)")
    st.stop()

players_per_team = num_players // num_teams
teams = [f"Équipe {i+1}" for i in range(num_teams)]
players = [f"Joueur {i+1}" for i in range(num_players)]

# Section des préférences
with st.expander("🎮 Configurer les préférences", expanded=True):
    # Préférences des équipes avec mise en page dynamique
    st.header("Préférences des Équipes (Coach)")
    team_prefs = {}
    
    # Création de lignes de 3 colonnes chacune
    for i in range(0, len(teams), 3):
        team_group = teams[i:i+3]
        cols = st.columns(len(team_group))
        
        for j, team in enumerate(team_group):
            with cols[j]:
                team_prefs[team] = st.multiselect(
                    f"{team}",
                    players,
                    key=f"team_{team}"
                )
                if len(team_prefs[team]) != len(players):
                    st.error(f"⚠️ Classer tous les {len(players)} joueurs")

    # Préférences des joueurs avec 4 colonnes par ligne
    st.header("Préférences des Joueurs")
    player_prefs = {}
    player_cols = st.columns(4)
    
    for i, player in enumerate(players):
        with player_cols[i % 4]:
            player_prefs[player] = st.multiselect(
                f"{player}",
                teams,
                key=f"player_{player}"
            )
            if len(player_prefs[player]) != len(teams):
                st.error(f"⚠️ Classer toutes les {len(teams)} équipes")

# Exécution et résultats
if st.button("🔍 Lancer le Matching"):
    valid_teams = all(len(v) == len(players) for v in team_prefs.values())
    valid_players = all(len(v) == len(teams) for v in player_prefs.values())
    
    if not (valid_teams and valid_players):
        st.error("❌ Completez toutes les préférences avant de lancer le matching !")
    else:
        team_matches, player_matches = gale_shapley(
            teams, players, team_prefs, player_prefs, players_per_team
        )
        
        # Affichage amélioré
        st.success(f"✅ Matching réussi ! ({players_per_team} joueurs/équipe)")
        
        # Résumé global
        st.subheader("Récapitulatif par Équipe")
        for team, members in team_matches.items():
            st.markdown(f"**{team}**: {', '.join(members)}")

        # Bouton de téléchargement
        df = pd.DataFrame.from_dict(player_matches, orient='index', columns=['Équipe'])
        csv = df.to_csv().encode('utf-8')
        st.download_button("📥 Télécharger les résultats", csv, "matching_results.csv", "text/csv")