from unittest.mock import Mock, patch

import pytest

from models.game import Game
from models.player import Player


@pytest.fixture
def mock_action_provider():
    return Mock()


@pytest.fixture
def teams():
    team1 = [Player("A1"), Player("A2")]
    team2 = [Player("B1"), Player("B2")]
    return team1, team2


def test_game_initialization(teams, mock_action_provider):
    team1, team2 = teams
    game = Game(team1, team2, mock_action_provider)

    assert game.team1 == team1
    assert game.team2 == team2
    # Ordered: A1, B1, A2, B2
    assert game.ordered_players == [team1[0], team2[0], team1[1], team2[1]]
    assert game.team1_score == 0
    assert game.team2_score == 0


def test_game_initialization_invalid_teams():
    p1 = Player("P1")
    p2 = Player("P2")
    p3 = Player("P3")

    with pytest.raises(ValueError, match="Teams must have equal size"):
        Game([p1], [p2, p3], Mock())

    with pytest.raises(ValueError, match="Teams cannot be empty"):
        Game([], [], Mock())


@patch("models.game.Round")
def test_play_round(mock_round_class, teams, mock_action_provider):
    team1, team2 = teams
    game = Game(team1, team2, mock_action_provider)

    # Mock return values for round.play_round()
    mock_round_instance = mock_round_class.return_value
    mock_round_instance.play_round.return_value = (2, 0)

    game.play_round()

    assert game.team1_score == 2
    assert game.team2_score == 0
    assert game._next_round_starter_index == 1


@patch("models.game.Round")
def test_play_game(mock_round_class, teams, mock_action_provider):
    team1, team2 = teams
    game = Game(team1, team2, mock_action_provider)

    mock_round_instance = mock_round_class.return_value
    # Round 1: T1 wins 2 pts
    # Round 2: T2 wins 3 pts
    # Round 3: T1 wins 2 pts (Total T1=4, T2=3)
    # Loop until target
    mock_round_instance.play_round.side_effect = [(2, 0), (0, 3), (10, 0)]

    winner = game.play_game(target_points=5)

    assert winner == 1
    assert game.team1_score == 12
    assert game.team2_score == 3
