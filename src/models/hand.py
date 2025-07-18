from logging_config import get_logger
from models.card import Card
from models.player import Player

logger = get_logger(__name__)


class Hand:
    def __init__(self, player_1: Player, player_2: Player) -> None:
        """Initialize a hand with two players."""
        self.player_1 = player_1
        self.player_2 = player_2

    def _choose_card(self, player: Player) -> Card:
        """Choose a card to play from the player's hand.

        Args:
            player (Player): The player to choose a card for.

        Returns:
            Card: The card chosen by the player.
        """
        for i, card in enumerate(player.cards):
            logger.info("%s: %s", i, card)
        card_index = int(input(f"Choose a card to play for {player.name}: "))
        return player.play_card(card_index)

    def play_hand(self, muestra: Card) -> tuple[int, int]:
        """Have each player play one card and determine the winner.

        Args:
            muestra (Card): The muestra card that determines the trump suit.

        Returns:
            tuple[int, int]: The points for each team (team_1_points, team_2_points).
        """
        card_1 = self._choose_card(self.player_1)
        card_2 = self._choose_card(self.player_2)

        logger.debug("Player 1 (%s) played: %s", self.player_1.name, card_1)
        logger.debug("Player 2 (%s) played: %s", self.player_2.name, card_2)

        if card_1.is_greater_than(card_2, muestra):
            logger.info("%s wins with %s", self.player_1.name, card_1)
            return 1, 0
        elif card_2.is_greater_than(card_1, muestra):
            logger.info("%s wins with %s", self.player_2.name, card_2)
            return 0, 1
        else:
            logger.info("It's a tie! Both played equivalent cards")
            return 1, 1
