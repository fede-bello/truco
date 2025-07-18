import random

from models.card import Card
from schemas.constants import CardNumber, CardSuit


class Deck:
    """Represents a deck of cards for the card game.

    Attributes:
        cards (List[Card]): The cards in the deck.
    """

    def __init__(self) -> None:
        """Initialize a deck with all possible cards."""
        self.cards: list[Card] = [
            Card(number, suit) for number in CardNumber.__args__ for suit in CardSuit.__args__
        ]

    def __str__(self) -> str:
        """Return a string representation of the deck."""
        return f"Deck of {len(self.cards)} cards"

    def __repr__(self) -> str:
        """Return a string representation of the deck for debugging."""
        return f"Deck of {len(self.cards)} cards"

    def draw(self, n: int) -> list[Card]:
        """Draw n random cards from the deck.

        Args:
            n (int): The number of cards to draw.

        Returns:
            list[Card]: The drawn cards.

        Raises:
            ValueError: If trying to draw more cards than available in the deck.
        """
        drawn_cards = random.sample(self.cards, n)
        for card in drawn_cards:
            self.cards.remove(card)
        return drawn_cards
