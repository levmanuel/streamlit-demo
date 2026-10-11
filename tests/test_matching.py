from lib.matching import gale_shapley


def test_chaque_joueur_a_une_equipe_et_les_equipes_sont_pleines():
    teams = ["A", "B"]
    players = ["p1", "p2", "p3", "p4"]
    team_prefs = {"A": ["p1", "p2", "p3", "p4"], "B": ["p1", "p2", "p3", "p4"]}
    player_prefs = {p: ["A", "B"] for p in players}

    equipes, joueurs = gale_shapley(teams, players, team_prefs, player_prefs, 2)

    assert sorted(equipes["A"] + equipes["B"]) == players
    assert all(len(v) == 2 for v in equipes.values())
    assert all(joueurs[p] in teams for p in players)
    for team, membres in equipes.items():
        assert all(joueurs[m] == team for m in membres)


def test_les_preferences_des_joueurs_priment_sur_la_premiere_proposition():
    # A propose d'abord à p1, mais p1 préfère B, qui le réclame ensuite.
    teams = ["A", "B"]
    players = ["p1", "p2"]
    team_prefs = {"A": ["p1", "p2"], "B": ["p1", "p2"]}
    player_prefs = {"p1": ["B", "A"], "p2": ["A", "B"]}

    equipes, joueurs = gale_shapley(teams, players, team_prefs, player_prefs, 1)

    assert joueurs == {"p1": "B", "p2": "A"}
    assert equipes == {"A": ["p2"], "B": ["p1"]}
