import pytest

from models.deck import Deck


def test_deck_initialization():
    deck = Deck()
    # 1-7, 10, 11, 12 (10 values) * 4 suits = 40 cards
    # Actually checking constants: 1-7, 10, 11, 12 are standard.
    assert len(deck.cards) == 40
    assert str(deck) == "Deck of 40 cards"
    assert repr(deck) == "Deck of 40 cards"

    # Check uniqueness
    card_set = {(c.number, c.suit) for c in deck.cards}
    assert len(card_set) == 40


def test_draw():
    deck = Deck()
    drawn = deck.draw(3)
    assert len(drawn) == 3
    assert len(deck.cards) == 37
    for card in drawn:
        assert card not in deck.cards


def test_draw_all():
    deck = Deck()
    drawn = deck.draw(40)
    assert len(drawn) == 40
    assert len(deck.cards) == 0


def test_draw_too_many():
    deck = Deck()
    with pytest.raises(ValueError):
        deck.draw(41)
