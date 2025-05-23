from models.deck import Deck
from models.player import Player
from models.card import Card
from typing import Optional

class Round:
    """
    Represents a round in the card game.
    
    Attributes:
        players (List[Player]): The players participating in the round.
        deck (Deck): The deck of cards for the round.
        muestra (Optional[Card]): The card shown after dealing that determines the trump suit.
    """
    def __init__(self, players: list[Player]):
        """
        Initialize a round with players and a fresh deck.
        
        Args:
            players (List[Player]): The players participating in the round.
        """
        self.players = players
        self.deck = Deck()
        self.muestra: Optional[Card] = None

    def deal_cards(self) -> None:
        """
        Deal 3 cards to each player and set the muestra card.
        
        This method draws 3 cards for each player and assigns them directly to the player's hand.
        After dealing to all players, it draws one more card to be the muestra.
        """
        for player in self.players:
            player.hand = self.deck.draw(3)
        
        self.muestra = self.deck.draw(1)[0]

    def play_card(self, player: Player, card: Card) -> None:
        """
        Have a player play a card from their hand.
        
        Args:
            player (Player): The player who is playing the card.
            card (Card): The card being played.
            
        Raises:
            ValueError: If the card is not in the player's hand.
        """
        player.play_card(card)
