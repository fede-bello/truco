from unittest.mock import Mock

import pytest

from models.card import Card
from models.round import Round


@pytest.fixture
def round_instance():
    # We only need a partially initialized Round for calculate_envido
    # as it heavily depends on self.muestra
    team1 = []
    team2 = []
    players = []
    return Round(
        team1=team1,
        team2=team2,
        ordered_players=players,
        action_provider=Mock(),
        starting_player=None,
    )


def test_calculate_envido_case_a_single_pieza(round_instance):
    # Muestra: 3 of Cups
    # Hand: 4 of Cups (Pieza -> 29), 6 of Spades (6), 1 of Cups (1)
    # Envido = 29 + 6 = 35
    round_instance.muestra = Card(3, "copa")
    hand = [Card(4, "copa"), Card(6, "espadas"), Card(1, "copa")]
    assert round_instance.calculate_envido(hand) == 35


def test_calculate_envido_case_a_multiple_piezas(round_instance):
    # Muestra: 3 of Cups
    # Hand: 2 of Cups (Pieza -> 30), 4 of Cups (Pieza -> 29), 1 of Cups (1)
    # Highest pieza is 2 (30). Other cards: 4 (facial 4), 1 (facial 1).
    # Envido = 30 + 4 = 34
    round_instance.muestra = Card(3, "copa")
    hand = [Card(2, "copa"), Card(4, "copa"), Card(1, "copa")]
    assert round_instance.calculate_envido(hand) == 34


def test_calculate_envido_case_b_different_suits(round_instance):
    # Muestra: 10 of Oro
    # Hand: 3 of Spades (3), 2 of Cups (2), 1 of Hearts (1) -> Use Oro numbers
    # Hand: 3 of Spades (3), 2 of Cups (2), 1 of Basto (1)
    # No piezas. Different suits.
    round_instance.muestra = Card(10, "oro")  # Muestra is Oro, so only Oro cards are piezas
    hand = [Card(3, "espadas"), Card(2, "copa"), Card(1, "basto")]
    assert round_instance.calculate_envido(hand) == 3


def test_calculate_envido_case_c_same_suit(round_instance):
    # Muestra: 3 of Cups
    # Hand: 5 of Spades (5), 7 of Spades (7), 1 of Hearts (1)
    # No piezas. Two cards of same suit (Spades).
    # Envido = 5 + 7 + 20 = 32
    round_instance.muestra = Card(3, "copa")
    hand = [Card(5, "espadas"), Card(7, "espadas"), Card(1, "oro")]
    assert round_instance.calculate_envido(hand) == 32


def test_calculate_envido_with_figures_same_suit(round_instance):
    # Muestra: 3 of Cups
    # Hand: 10 of Spades (0), 11 of Spades (0), 1 of Hearts (1)
    # No piezas. Two cards same suit (Spades).
    # Envido = 0 + 0 + 20 = 20
    round_instance.muestra = Card(3, "copa")
    hand = [Card(10, "espadas"), Card(11, "espadas"), Card(1, "oro")]
    assert round_instance.calculate_envido(hand) == 20


def test_calculate_envido_with_one_figure_one_num_same_suit(round_instance):
    # Muestra: 3 of Cups
    # Hand: 10 of Spades (0), 7 of Spades (7), 1 of Hearts (1)
    # No piezas. Two cards same suit (Spades).
    # Envido = 7 + 0 + 20 = 27
    round_instance.muestra = Card(3, "copa")
    hand = [Card(10, "espadas"), Card(7, "espadas"), Card(1, "oro")]
    assert round_instance.calculate_envido(hand) == 27


def test_calculate_envido_all_same_suit_no_pieza(round_instance):
    # Muestra: 3 of Cups
    # Hand: 5 of Spades (5), 6 of Spades (6), 7 of Spades (7)
    # Highest two: 7 + 6 + 20 = 33
    round_instance.muestra = Card(3, "copa")
    hand = [Card(5, "espadas"), Card(6, "espadas"), Card(7, "espadas")]
    assert round_instance.calculate_envido(hand) == 33


def test_calculate_envido_pieza_rey_replacement(round_instance):
    # Muestra: 2 of Oro
    # Hand: 12 of Oro (Pieza replacing 2 -> 30), 7 of Spades (7), 1 of Basto (1)
    # Envido = 30 + 7 = 37
    round_instance.muestra = Card(2, "oro")
    hand = [Card(12, "oro"), Card(7, "espadas"), Card(1, "basto")]
    assert round_instance.calculate_envido(hand) == 37
