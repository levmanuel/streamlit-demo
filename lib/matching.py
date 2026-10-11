"""Matching stable équipes / joueurs (Gale-Shapley, équipes proposantes)."""


def gale_shapley(teams, players, team_prefs, player_prefs, players_per_team):
    """Retourne (joueurs_par_equipe, equipe_par_joueur).

    team_prefs[team] et player_prefs[player] sont des classements complets
    (du préféré au moins préféré).
    """
    proposals = {team: [] for team in teams}
    player_matches = {player: None for player in players}
    proposed = {team: set() for team in teams}

    while True:
        active_teams = [
            t for t in teams
            if len(proposals[t]) < players_per_team and len(proposed[t]) < len(players)
        ]
        if not active_teams:
            break

        for team in active_teams:
            for player in team_prefs[team]:
                if player in proposed[team]:
                    continue
                proposed[team].add(player)
                current_team = player_matches[player]

                if current_team is None:
                    proposals[team].append(player)
                    player_matches[player] = team
                    break
                if player_prefs[player].index(team) < player_prefs[player].index(current_team):
                    proposals[current_team].remove(player)
                    proposals[team].append(player)
                    player_matches[player] = team
                    break
    return proposals, player_matches
