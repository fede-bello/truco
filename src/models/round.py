from typing import TYPE_CHECKING

from logging_config import get_logger
from models.deck import Deck
from models.hand import Hand
from models.player import Player
from schemas.constants import CARDS_DEALT_PER_PLAYER
from schemas.hand_info import RoundInfo

if TYPE_CHECKING:
    from models.card import Card

logger = get_logger(__name__)

HANDS_TO_WIN_ROUND = CARDS_DEALT_PER_PLAYER // 2 + 1


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

        self._deal_cards()
        self.muestra: Card
        self.round_info: RoundInfo = RoundInfo()

    def _deal_cards(self) -> None:
        """Deal CARDS_DEALT_PER_PLAYER cards to each player and set the muestra card.

        This method draws CARDS_DEALT_PER_PLAYER cards for each player and assigns them directly
        to the player's hand. After dealing to all players, it draws one card to be the muestra.
        """
        for player in [self.player_1, self.player_2]:
            player.cards = self.deck.draw(CARDS_DEALT_PER_PLAYER)

        self.muestra = self.deck.draw(1)[0]

    def play_round(self) -> tuple[int, int]:
        """Play a round of the game.

        This method plays hands until one player wins 2 hands.
        If there's a tie, the first player to win the next hand wins the round.

        Returns:
            tuple[int, int]: The points for each team (team_1_points, team_2_points).
        """
        logger.info("Playing round")
        logger.info("Muestra is: %s", self.muestra)
        hand = Hand(self.player_1, self.player_2)
        player_1_wins = 0
        player_2_wins = 0

        for _ in range(CARDS_DEALT_PER_PLAYER):
            hand_result = hand.play_hand(self.muestra)
            player_1_wins += hand_result[0]
            player_2_wins += hand_result[1]

            if player_1_wins == HANDS_TO_WIN_ROUND and player_2_wins == HANDS_TO_WIN_ROUND:
                continue

            if HANDS_TO_WIN_ROUND in (player_1_wins, player_2_wins):
                # if one of the players has won the round, break
                break

        if player_1_wins > player_2_wins:
            logger.info("Player 1 wins the round")
            return 1, 0
        elif player_2_wins > player_1_wins:
            logger.info("Player 2 wins the round")
            return 0, 1
        else:
            # rare case where there are three ties, the "hand" wins
            logger.info("All tied, the hand wins")
            return 1, 0
