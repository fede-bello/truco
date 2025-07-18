from typing import TYPE_CHECKING

from models.deck import Deck
from models.hand import Hand
from models.player import Player
from schemas.constants import CARDS_DEALT_PER_PLAYER
from schemas.hand_info import RoundInfo

if TYPE_CHECKING:
    from models.card import Card


class Round:
    """Represents a round in the card game, which is the play between dealing cards.

    Attributes:
        player_1 (Player): The player in team 1.
        player_2 (Player): The player in team 2.
        deck (Deck): The deck of cards for the round.
        muestra (Card | None): The card shown after dealing that determines the trump suit.
    """

    def __init__(self, player_1: Player, player_2: Player) -> None:
        """Initialize a round with two players and a fresh deck.

        Args:
            player_1 (Player): The player in team 1.
            player_2 (Player): The player in team 2.
        """
        self.player_1 = player_1
        self.player_2 = player_2
        self.deck = Deck()
        self.muestra: Card | None = None
        self.round_info: RoundInfo = RoundInfo()

    def deal_cards(self) -> None:
        """Deal CARDS_DEALT_PER_PLAYER cards to each player and set the muestra card.

        This method draws CARDS_DEALT_PER_PLAYER cards for each player and assigns them directly
        to the player's hand. After dealing to all players, it draws one card to be the muestra.
        """
        for player in [self.player_1, self.player_2]:
            player.cards = self.deck.draw(CARDS_DEALT_PER_PLAYER)

        self.muestra = self.deck.draw(1)[0]

    def play_round(self) -> None:
        """Play a round of the game.

        This method plays a round of the game, which consists of 3 hands.
        """
        hand = Hand(self.player_1, self.player_2)
        for _ in range(CARDS_DEALT_PER_PLAYER):
            hand.play_hand()
