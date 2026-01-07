from unittest.mock import Mock

import pytest

from models.card import Card
from models.player import Player
from models.round import Round
from schemas.actions import ActionCode


@pytest.fixture
def mock_action_provider():
    return Mock()


@pytest.fixture
def players():
    return [Player("A1"), Player("B1"), Player("A2"), Player("B2")]


@pytest.fixture
def round_instance(players, mock_action_provider):
    team1 = [players[0], players[2]]
    team2 = [players[1], players[3]]
    return Round(
        team1=team1,
        team2=team2,
        ordered_players=players,
        action_provider=mock_action_provider,
        starting_player=players[0],
    )


def test_round_initialization(round_instance, players):
    assert len(players[0].cards) == 3
    assert isinstance(round_instance.muestra, Card)
    assert round_instance.round_state.truco_state == "nada"


def test_get_teammates(round_instance, players):
    assert round_instance._get_teammates(players[0]) == [players[2]]
    assert round_instance._get_teammates(players[1]) == [players[3]]


def test_is_same_team(round_instance, players):
    assert round_instance._is_same_team(players[0], players[2]) is True
    assert round_instance._is_same_team(players[0], players[1]) is False


def test_can_beat_truco(round_instance, players):
    # Initial state
    assert round_instance._can_beat_truco(players[0]) is True

    # After T1 bids, T2 can beat, T1 cannot
    round_instance.last_truco_bidder = players[0]
    assert round_instance._can_beat_truco(players[1]) is True
    assert round_instance._can_beat_truco(players[0]) is False

    # After vale4, no one can beat
    round_instance.round_state.truco_state = "vale4"
    assert round_instance._can_beat_truco(players[1]) is False


def test_advance_truco_state(round_instance):
    assert round_instance._advance_truco_state() == "truco"
    assert round_instance._advance_truco_state() == "retruco"
    assert round_instance._advance_truco_state() == "vale4"
    with pytest.raises(ValueError, match="Cannot advance truco state from vale4"):
        round_instance._advance_truco_state()


def test_get_points_truco_state(round_instance):
    round_instance.round_state.truco_state = "nada"
    assert round_instance._get_points_truco_state() == 1
    round_instance.round_state.truco_state = "truco"
    assert round_instance._get_points_truco_state() == 2
    round_instance.round_state.truco_state = "retruco"
    assert round_instance._get_points_truco_state() == 3
    round_instance.round_state.truco_state = "vale4"
    assert round_instance._get_points_truco_state() == 4


def test_play_hand_simple(round_instance, players, mock_action_provider):
    # Clear existing hands from deal during __init__
    for p in players:
        p.cards = []

    # Mocking card plays
    # A1 plays 1 Espada (Mata, value 13)
    # B1 plays 4 Copa (Normal, value 0)
    # A2 plays 4 Basto (Normal, value 0)
    # B2 plays 3 Oro (Normal, value 9)
    # Muestra is 10 Copa (so ONLY Copa cards can be Piezas)
    # 4 Copa would be Pieza (value 17), so we use a different muestra.
    # Muestra is 10 Oro (so ONLY Oro cards can be Piezas)
    # 3 Oro is NOT a pieza (Piezas for 10 Oro are 2, 4, 5, 11, 10)
    round_instance.muestra = Card(10, "oro")
    players[0].cards = [Card(1, "espadas")]
    players[1].cards = [Card(4, "copa")]
    players[2].cards = [Card(4, "basto")]
    players[3].cards = [Card(3, "oro")]

    mock_action_provider.side_effect = [
        ActionCode.PLAY_CARD_0,
        ActionCode.PLAY_CARD_0,
        ActionCode.PLAY_CARD_0,
        ActionCode.PLAY_CARD_0,
    ]

    winner = round_instance._play_hand(players[0])
    assert winner == players[0]


def test_play_hand_tie(round_instance, players, mock_action_provider):
    # Clear existing hands
    for p in players:
        p.cards = []

    round_instance.muestra = Card(10, "copa")
    # Tying cards
    players[0].cards = [Card(3, "espadas")]
    players[1].cards = [Card(3, "basto")]
    players[2].cards = [Card(4, "basto")]
    players[3].cards = [Card(4, "oro")]

    mock_action_provider.side_effect = [
        ActionCode.PLAY_CARD_0,
        ActionCode.PLAY_CARD_0,
        ActionCode.PLAY_CARD_0,
        ActionCode.PLAY_CARD_0,
    ]

    winner = round_instance._play_hand(players[0])
    assert winner is None


def test_get_team_pie(round_instance, players):
    # Players: [A1, B1, A2, B2]
    # Team 1: [A1, A2], Team 2: [B1, B2]

    # Case 1: Starter A1 (Order: A1, B1, A2, B2)
    round_instance._starting_player = players[0]
    assert round_instance._get_team_pie(1).name == "A2"
    assert round_instance._get_team_pie(2).name == "B2"

    # Case 2: Starter B1 (Order: B1, A2, B2, A1)
    round_instance._starting_player = players[1]
    assert round_instance._get_team_pie(2).name == "B2"
    assert round_instance._get_team_pie(1).name == "A1"

    # Case 3: Starter A2 (Order: A2, B2, A1, B1)
    round_instance._starting_player = players[2]
    assert round_instance._get_team_pie(1).name == "A1"
    assert round_instance._get_team_pie(2).name == "B1"

    # Case 4: Starter B2 (Order: B2, A1, B1, A2)
    round_instance._starting_player = players[3]
    assert round_instance._get_team_pie(2).name == "B1"
    assert round_instance._get_team_pie(1).name == "A2"
