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

    def play_hand(self) -> tuple[Player, int]:
        """Have all players play one card each from their hands.

        Returns:
            tuple[Player, int]: The winning player and the index of the winning player in that team.
        """
        highest_card = None
        winning_player = None
        winning_player_index = None

        for i in range(len([self.player_1, self.player_2])):
            for player in [self.player_1, self.player_2]:
                card = self._choose_card(player)

                if highest_card is None or card > highest_card:
                    highest_card = card
                    winning_player = player
                    winning_player_index = i

        logger.debug("Highest card: %s", highest_card)
        logger.debug("Winning player: %s", winning_player)

        if winning_player is None:
            msg = "No winning player"
            raise ValueError(msg)
        if winning_player_index is None:
            msg = "No winning player index"
            raise ValueError(msg)
        return winning_player, winning_player_index
