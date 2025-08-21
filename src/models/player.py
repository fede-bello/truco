from models.card import Card
from schemas.constants import CARDS_DEALT_PER_PLAYER


class Player:
    """Represents a player in the card game.

    Attributes:
        name (str): The name of the player.
        cards (List[Card]): The cards in the player's hand.
    """

    def __init__(self, name: str) -> None:
        """Initialize a player with a name and an empty hand.

        Args:
            name (str): The name of the player.
        """
        self.name = name
        self.cards: list[Card] = []
        self.played_cards: list[Card] = []

    def add_card(self, card: Card) -> None:
        """Add a card to the player's hand.

        Args:
            card (Card): The card to add to the hand.

        Raises:
            ValueError: If the player already has 3 cards or if the card is already in hand.
        """
        if card not in self.cards:
            if len(self.cards) >= CARDS_DEALT_PER_PLAYER:
                msg = f"Player can't have more than {CARDS_DEALT_PER_PLAYER} cards"
                raise ValueError(msg)
            self.cards.append(card)
        else:
            msg = f"Card {card} already in hand"
            raise ValueError(msg)

    def play_card(self, card_index: int) -> Card:
        """Play a card from the player's hand.

        Args:
            card_index (int): The index of the card to play.

        Raises:
            ValueError: If the card index is invalid or there are no cards.
        """
        if not self.cards:
            msg = "No cards in hand"
            raise ValueError(msg)
        if card_index < 0 or card_index >= len(self.cards):
            msg = "Invalid card index"
            raise ValueError(msg)
        card = self.cards.pop(card_index)
        self.played_cards.append(card)
        return card

    def __str__(self) -> str:
        """Return a string representation of the player.

        Returns:
            str: The player's name.
        """
        return f"{self.name}"

    def __repr__(self) -> str:
        """Return a string representation of the player for debugging.

        Returns:
            str: The player's name.
        """
        return f"{self.name}"
