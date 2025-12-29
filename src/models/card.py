from schemas.constants import REY, CardNumber, CardSuit


class Card:
    """Represents a playing card in the card game.

    Attributes:
        number (int): The number or face value of the card (1-7, 10).
        suit (str): The suit of the card ("basto", "espadas", "oro", "copa").
    """

    _CARD_ORDER = {4: 0, 5: 1, 6: 2, 7: 3, 10: 4, 11: 5, 12: 6, 1: 7, 2: 8, 3: 9}

    # Matas - Special cards with unique hierarchy (from worst to best)
    _MATAS = {
        (7, "oro"): 10,  # Siete de Oro
        (7, "espadas"): 11,  # Siete de Espada
        (1, "basto"): 12,  # Uno de Basto
        (1, "espadas"): 13,  # Uno de Espada (best)
    }

    _PIEZAS = {10: 14, 11: 15, 5: 16, 4: 17, 2: 18}

    def __init__(self, number: CardNumber, suit: CardSuit) -> None:
        """Initialize a card with a number and suit.

        Args:
            number (CardNumber): The number or face value of the card (1-7, 10).
            suit (CardSuit): The suit of the card ("basto", "espadas", "oro", "copa").
        """
        self.number = number
        self.suit = suit

    def is_pieza(self, muestra: "Card") -> bool:
        """Check if this card is a Pieza (trump suit special card).

        Piezas are the 2, 4, 5, Caballo (11), and Sota (10) of the muestra suit.
        If any of these is the muestra itself, the Rey (12) of that suit becomes the Pieza.

        Args:
            muestra (Card): The muestra card that determines the trump suit.

        Returns:
            bool: True if this card is a Pieza, False otherwise.
        """
        if self.suit != muestra.suit:
            return False

        if self.number in self._PIEZAS:
            return True

        # If muestra is one of the standard piezas, then 12 becomes a pieza
        return muestra.number in self._PIEZAS and self.number == REY

    def _is_mata(self) -> bool:
        """Check if this card is a Mata (trump suit special card)."""
        return (self.number, self.suit) in self._MATAS

    def get_card_value(self, muestra: "Card") -> int:
        """Get the value of this card considering Matas (special cards).

        Matas hierarchy (from worst to best):
        1. Normal cards (using _CARD_ORDER)
        2. Siete de Oro (7 of oro) - value 8
        3. Siete de Espada (7 of espadas) - value 9
        4. Uno de Basto (1 of basto) - value 10
        5. Uno de Espada (1 of espadas) - value 11

        Returns:
            int: The value of this card for comparison purposes.
        """
        if self.is_pieza(muestra):
            # If the card is 12 and a pieza, then it takes the value of the muestra
            number = self.number if self.number != REY else muestra.number
            return self._PIEZAS[number]

        if self._is_mata():
            return self._MATAS[(self.number, self.suit)]

        # Use normal card order for all other cards
        return self._CARD_ORDER[self.number]

    def is_greater_than(self, other: "Card", muestra: "Card") -> bool:
        """Compare two cards considering the muestra.

        Args:
            other (Card): The other card to compare against.
            muestra (Card): The muestra card that determines the trump suit.

        Returns:
            bool: True if this card is greater than the other card, False otherwise.
        """
        return self.get_card_value(muestra) > other.get_card_value(muestra)

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

    def __hash__(self) -> int:
        """Return hash of the card for use in sets and as dict keys."""
        return hash((self.number, self.suit))
