from models.card import Card

class Player:
    """
    Represents a player in the card game.
    
    Attributes:
        name (str): The name of the player.
        cards (List[Card]): The cards in the player's hand.
    """
    def __init__(self, name: str):
        """
        Initialize a player with a name and an empty hand.
        
        Args:
            name (str): The name of the player.
        """
        self.name = name
        self.cards: list[Card] = []
        self.played_cards: list[Card] = []

    def __str__(self) -> str:
        """
        Return a string representation of the player.
        
        Returns:
            str: The player's name.
        """
        return f"{self.name}"
    
    def __repr__(self) -> str:
        """
        Return a string representation of the player for debugging.
        
        Returns:
            str: The player's name.
        """
        return f"{self.name}"

    def add_card(self, card: Card) -> None:
        """
        Add a card to the player's hand.
        
        Args:
            card (Card): The card to add to the hand.
            
        Raises:
            ValueError: If the player already has 3 cards or if the card is already in hand.
        """
        if card not in self.cards:
            if len(self.cards) >= 3:
                raise ValueError("Player can't have more than 3 cards")
            self.cards.append(card)
        else:
            raise ValueError(f"Card {card} already in hand")

    def play_card(self, card_index: int) -> None:
        """
        Play a card from the player's hand.
        
        Args:
            card_index (int): The index of the card to play.
            
        Raises:
            ValueError: If the card is not in the player's hand.
        """
        # TODO: Check how to properly implement this
        if not self.cards:
            raise ValueError("No cards in hand")
        card = self.cards.pop(card_index)
        self.played_cards.append(card)
        return card