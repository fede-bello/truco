from typing import Literal
from enum import Enum

CARD_NUMBERS = Literal[4, 5, 6, 7, 10, 11, 12, 1, 2, 3]

class CardSuit(Enum):
    BASTO = "basto"
    ESPADA = "espadas"
    ORO = "oro"
    COPA = "copa"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value
