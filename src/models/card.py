from constants import CardSuit, CARD_NUMBERS
from typing import Literal

class Card:
    """
    Represents a playing card in the card game.
    
    Attributes:
        number (CARD_NUMBERS): The number or face value of the card.
        suit (CardSuit): The suit of the card.
    """
    def __init__(self, number: CARD_NUMBERS, suit: CardSuit):
        """
        Initialize a card with a number and suit.
        
        Args:
            number (CARD_NUMBERS): The number or face value of the card.
            suit (CardSuit): The suit of the card.
        """
        self.number = number
        self.suit = suit

    def __str__(self) -> str:
        """
        Return a string representation of the card.
        
        Returns:
            str: A string showing the number and suit of the card.
        """
        return f"{self.number} of {self.suit}"
