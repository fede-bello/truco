from constants import CardSuit, CARD_NUMBERS
from models.card import Card
import random
class Deck:
    def __init__(self):
        self.cards = [Card(number, suit) for number in CARD_NUMBERS.__args__ for suit in CardSuit]

    def __str__(self):
        return f"Deck of {len(self.cards)} cards"

    def __repr__(self):
        return f"Deck of {len(self.cards)} cards"
    
    def draw(self, n: int) -> list[Card]:
        drawn_cards = random.sample(self.cards, n)
        for card in drawn_cards:
            self.cards.remove(card)
        return drawn_cards

