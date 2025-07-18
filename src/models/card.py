from schemas.constants import CardNumber, CardSuit


class Card:
    """Represents a playing card in the card game.

    Attributes:
        number (int): The number or face value of the card (1-7, 10).
        suit (str): The suit of the card ("basto", "espadas", "oro", "copa").
    """

    _CARD_ORDER = {4: 0, 5: 1, 6: 2, 7: 3, 10: 4, 1: 5, 2: 6, 3: 7}

    def __init__(self, number: CardNumber, suit: CardSuit) -> None:
        """Initialize a card with a number and suit.

        Args:
            number (CardNumber): The number or face value of the card (1-7, 10).
            suit (CardSuit): The suit of the card ("basto", "espadas", "oro", "copa").
        """
        self.number = number
        self.suit = suit

    def __str__(self) -> str:
        """Return a string representation of the card.

        Returns:
            str: A string showing the number and suit of the card.
        """
        return f"{self.number} of {self.suit}"

    def __repr__(self) -> str:
        """Return a string representation of the card for debugging.

        This allows lists of cards to be printed properly.

        Returns:
            str: A string showing the number and suit of the card.
        """
        return self.__str__()

    def __lt__(self, other: "Card") -> bool:
        """Compare two cards.

        Returns:
            bool: True if the current card is less than the other card, False otherwise.
        """
        return self._CARD_ORDER[self.number] < self._CARD_ORDER[other.number]

    def __le__(self, other: "Card") -> bool:
        """Compare two cards.

        Returns:
            bool: True if the current card is less than or equal to the other card, False otherwise.
        """
        return self._CARD_ORDER[self.number] <= self._CARD_ORDER[other.number]

    def __gt__(self, other: "Card") -> bool:
        """Compare two cards.

        Returns:
            bool: True if the current card is greater than the other card, False otherwise.
        """
        return self._CARD_ORDER[self.number] > self._CARD_ORDER[other.number]

    def __ge__(self, other: "Card") -> bool:
        """Compare two cards.

        Returns:
            bool: True if the current card is greater than to the other card, False otherwise.
        """
        return self._CARD_ORDER[self.number] > self._CARD_ORDER[other.number]

    def __eq__(self, other: object) -> bool:
        """Compare two cards.

        Returns:
            bool: True if the current card is equal to the other card, False otherwise.
        """
        if not isinstance(other, Card):
            return NotImplemented
        return self.number == other.number and self.suit == other.suit

    def __hash__(self) -> int:
        """Return hash of the card for use in sets and as dict keys."""
        return hash((self.number, self.suit))

    def __ne__(self, other: object) -> bool:
        """Compare two cards.

        Returns:
            bool: True if the current card is not equal to the other card, False otherwise.
        """
        if not isinstance(other, Card):
            return NotImplemented
        return self.number != other.number or self.suit != other.suit
