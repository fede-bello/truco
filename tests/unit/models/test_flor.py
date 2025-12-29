from unittest.mock import Mock

import pytest

from models.card import Card
from models.player import Player
from models.round import Round
from schemas.actions import ActionCode


@pytest.mark.parametrize(
    ("muestra", "cards", "expected"),
    [
        # Muestra: 10 oro. Piezas: 2, 4, 5, 11, 12 oro (10 is muestra)
        (
            Card(10, "oro"),
            [Card(2, "oro"), Card(4, "oro"), Card(5, "oro")],
            True,
        ),  # 3 piezas
        (
            Card(10, "oro"),
            [Card(2, "oro"), Card(4, "oro"), Card(1, "espadas")],
            True,
        ),  # 2 piezas + trash
        (
            Card(10, "oro"),
            [Card(2, "oro"), Card(1, "espadas"), Card(7, "espadas")],
            True,
        ),  # 1 pieza + 2 same suit
        (
            Card(10, "oro"),
            [Card(2, "oro"), Card(1, "oro"), Card(7, "oro")],
            True,
        ),  # 1 pieza + 2 same suit (actually 3 same suit)
        (
            Card(10, "oro"),
            [Card(1, "espadas"), Card(2, "espadas"), Card(3, "espadas")],
            True,
        ),  # 3 same suit, 0 piezas
        (
            Card(10, "oro"),
            [Card(2, "oro"), Card(1, "espadas"), Card(7, "basto")],
            False,
        ),  # 1 pieza + 2 different suits
        (
            Card(10, "oro"),
            [Card(1, "espadas"), Card(2, "espadas"), Card(3, "basto")],
            False,
        ),  # 2 same suit + 1 different, 0 piezas
        (
            Card(10, "oro"),
            [Card(1, "espadas"), Card(2, "basto"), Card(3, "oro")],
            False,
        ),  # 3 different suits, 0 piezas
        # Rey replacement case. Muestra: 2 oro. Piezas: 10, 11, 5, 4, 12 oro
        (
            Card(2, "oro"),
            [Card(12, "oro"), Card(1, "espadas"), Card(7, "espadas")],
            True,
        ),  # 12 is pieza, + 2 same suit
        (
            Card(2, "oro"),
            [Card(12, "oro"), Card(1, "espadas"), Card(7, "basto")],
            False,
        ),  # 12 is pieza, + 2 diff
        (
            Card(2, "oro"),
            [Card(12, "oro"), Card(11, "oro"), Card(7, "basto")],
            True,
        ),  # 2 piezas + trash
    ],
)
def test_has_flor_comprehensive(muestra, cards, expected):
    players = [Player("A1"), Player("B1")]
    round_inst = Round(
        team1=[players[0]],
        team2=[players[1]],
        ordered_players=players,
        action_provider=Mock(),
        starting_player=players[0],
    )
    round_inst.muestra = muestra
    assert round_inst._has_flor(cards) == expected


def test_flor_action_availability():
    players = [Player("A1"), Player("B1")]
    mock_provider = Mock()
    round_inst = Round(
        team1=[players[0]],
        team2=[players[1]],
        ordered_players=players,
        action_provider=mock_provider,
        starting_player=players[0],
    )

    # A1 has 3 cards (trash hand), hasn't called flor
    players[0].cards = [Card(1, "oro"), Card(2, "basto"), Card(3, "espadas")]
    actions = round_inst._get_available_actions(players[0])
    assert ActionCode.FLOR in actions
    # Double check it doesn't have flor
    assert not round_inst._has_flor(players[0].cards)

    # A1 calls flor
    round_inst.round_state.flor_calls.append(players[0])
    actions = round_inst._get_available_actions(players[0])
    assert ActionCode.FLOR not in actions

    # After playing a card
    players[0].cards = [Card(1, "oro"), Card(2, "oro")]
    round_inst.round_state.flor_calls = []  # Reset for test
    actions = round_inst._get_available_actions(players[0])
    assert ActionCode.FLOR not in actions


def test_flor_scoring_real():
    players = [Player("A1"), Player("B1")]
    mock_provider = Mock()
    round_inst = Round(
        team1=[players[0]],
        team2=[players[1]],
        ordered_players=players,
        action_provider=mock_provider,
        starting_player=players[0],
    )
    round_inst.muestra = Card(10, "oro")
    # A1 has flor
    a1_cards = [Card(1, "espadas"), Card(2, "espadas"), Card(3, "espadas")]
    players[0].cards = list(a1_cards)
    round_inst.round_state.player_initial_hands[players[0]] = list(a1_cards)

    round_inst.round_state.flor_calls.append(players[0])

    # End round with T1 winning (1 truco point)
    p1, p2 = round_inst.get_hand_points(2, 0)
    assert p1 == 1 + 3  # 1 for truco, 3 for flor
    assert p2 == 0


def test_flor_scoring_fake():
    players = [Player("A1"), Player("B1")]
    mock_provider = Mock()
    round_inst = Round(
        team1=[players[0]],
        team2=[players[1]],
        ordered_players=players,
        action_provider=mock_provider,
        starting_player=players[0],
    )
    round_inst.muestra = Card(10, "oro")
    # A1 does NOT have flor
    a1_cards = [Card(1, "espadas"), Card(2, "copa"), Card(3, "basto")]
    players[0].cards = list(a1_cards)
    round_inst.round_state.player_initial_hands[players[0]] = list(a1_cards)

    round_inst.round_state.flor_calls.append(players[0])

    # End round with T1 winning (1 truco point)
    p1, p2 = round_inst.get_hand_points(2, 0)
    assert p1 == 1  # 1 for truco, 0 for fake flor
    assert p2 == 3  # 3 for A1's fake flor penalized to T2
