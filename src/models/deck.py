from constants import CardSuit, CARD_NUMBERS
from models.card import Card
import random
from typing import List

class Deck:
    """
    Represents a deck of cards for the card game.
    
    Attributes:
        cards (List[Card]): The cards in the deck.
    """
    def __init__(self):
        """
        Initialize a deck with all possible cards.
        """
        self.cards: List[Card] = [Card(number, suit) for number in CARD_NUMBERS.__args__ for suit in CardSuit]

    def __str__(self) -> str:
        """
        Return a string representation of the deck.
        
        Returns:
            str: A string showing the number of cards in the deck.
        """
        return f"Deck of {len(self.cards)} cards"

    def __repr__(self) -> str:
        """
        Return a string representation of the deck for debugging.
        
        Returns:
            str: A string showing the number of cards in the deck.
        """
        return f"Deck of {len(self.cards)} cards"
    
    def draw(self, n: int) -> List[Card]:
        """
        Draw n random cards from the deck.
        
        Args:
            n (int): The number of cards to draw.
            
        Returns:
            List[Card]: The drawn cards.
            
        Raises:
            ValueError: If trying to draw more cards than available in the deck.
        """
        drawn_cards = random.sample(self.cards, n)
        for card in drawn_cards:
            self.cards.remove(card)
        return drawn_cards
