from constants import CardSuit, CARD_NUMBERS

class Card:
    def __init__(self, number: CARD_NUMBERS, suit: CardSuit):
        self.number = number
        self.suit = suit

    def __str__(self):
        return f"{self.number} of {self.suit}"
