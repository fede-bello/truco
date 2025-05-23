from models.deck import Deck
from models.player import Player
from models.card import Card
from typing import Optional

class Hand:
    """
    Represents a hand in the card game, which is the play between dealing cards.
    
    Attributes:
        team1 (List[Player]): The players in team 1.
        team2 (List[Player]): The players in team 2. 
        deck (Deck): The deck of cards for the hand.
        muestra (Optional[Card]): The card shown after dealing that determines the trump suit.
    """
    def __init__(self, team1: list[Player], team2: list[Player]):
        """
        Initialize a hand with two teams and a fresh deck.
        
        Args:
            team1 (List[Player]): The players in team 1.
            team2 (List[Player]): The players in team 2.
        """
        self.team1 = team1
        self.team2 = team2
        self.deck = Deck()
        self.muestra: Optional[Card] = None

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
        Have all players play one card each from their hands.
        """
        for player in self.team1:
            print(f"{player.name}: {player.cards}", flush=True)
            print(f"Choose a card to play", flush=True)
            card_index = int(input("Enter card index (0-2): "))
            card_1 = player.play_card(card_index)
        for player in self.team2:
            print(f"{player.name}: {player.cards}", flush=True)
            print(f"Choose a card to play", flush=True)
            card_index = int(input("Enter card index (0-2): "))
            card_2 = player.play_card(card_index)

        print(f"Card 1: {card_1}")
        print(f"Card 2: {card_2}")

        print(card_1 > card_2)
