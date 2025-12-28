import pytest

from models.card import Card
from models.player import Player


def test_player_initialization():
    player = Player("A1")
    assert player.name == "A1"
    assert player.cards == []
    assert player.played_cards == []
    assert str(player) == "A1"
    assert repr(player) == "A1"


def test_play_card():
    player = Player("A1")
    card1 = Card(1, "espadas")
    card2 = Card(2, "espadas")
    player.cards = [card1, card2]

    played = player.play_card(0)
    assert played == card1
    assert len(player.cards) == 1
    assert player.cards[0] == card2
    assert player.played_cards == [card1]


def test_play_card_invalid_index():
    player = Player("A1")
    player.cards = [Card(1, "espadas")]

    with pytest.raises(ValueError, match="Invalid card index"):
        player.play_card(1)

    with pytest.raises(ValueError, match="Invalid card index"):
        player.play_card(-1)


def test_play_card_no_cards():
    player = Player("A1")
    with pytest.raises(ValueError, match="No cards in hand"):
        player.play_card(0)
