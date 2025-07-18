from models.deck import Deck
from models.player import Player
from models.card import Card
from typing import Optional
from schemas.hand_info import RoundInfo
from models.hand import Hand
class Round:
    """
    Represents a round in the card game, which is the play between dealing cards.
    
    Attributes:
        team1 (List[Player]): The players in team 1.
        team2 (List[Player]): The players in team 2. 
        deck (Deck): The deck of cards for the round.
        muestra (Optional[Card]): The card shown after dealing that determines the trump suit.
    """
    def __init__(self, team1: list[Player], team2: list[Player]):
        """
        Initialize a round with two teams and a fresh deck.
            
        Args:
            team1 (List[Player]): The players in team 1.
            team2 (List[Player]): The players in team 2.
        """
        self.team1 = team1
        self.team2 = team2
        self.deck = Deck()
        self.muestra: Optional[Card] = None
        self.round_info: RoundInfo = RoundInfo()

    def deal_cards(self) -> None:
        """
        Deal 3 cards to each player and set the muestra card.
        
        This method draws 3 cards for each player and assigns them directly to the player's hand.
        After dealing to all players, it draws one more card to be the muestra.
        """
        for player in self.team1:
            player.cards = self.deck.draw(3)
        for player in self.team2:
            player.cards = self.deck.draw(3)
        
        self.muestra = self.deck.draw(1)[0]

    def play_round(self) -> None:
        """
        Play a round of the game.
        """
        hand = Hand(self.team1, self.team2)
        for i in range(3):
            hand.play_hand()




