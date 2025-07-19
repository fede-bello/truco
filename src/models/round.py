from logging_config import get_logger
from models.card import Card
from models.deck import Deck
from models.player import Player
from schemas.constants import CARDS_DEALT_PER_PLAYER
from schemas.hand_info import RoundInfo
from schemas.round_state import RoundState

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

        self.round_state: RoundState = RoundState(truco_state="nada")

    def _deal_cards(self) -> None:
        """Deal CARDS_DEALT_PER_PLAYER cards to each player and set the muestra card.

        This method draws CARDS_DEALT_PER_PLAYER cards for each player and assigns them directly
        to the player's hand. After dealing to all players, it draws one card to be the muestra.
        """
        for player in [self.player_1, self.player_2]:
            player.cards = self.deck.draw(CARDS_DEALT_PER_PLAYER)

        self.muestra = self.deck.draw(1)[0]

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

    def _get_points_truco_state(self) -> int:
        """Get the points for the truco state.

        Returns:
            int: The points for the truco state.
        """
        match self.round_state.truco_state:
            case "nada":
                return 1
            case "truco":
                return 2
            case "retruco":
                return 3
            case "vale4":
                return 4

    def play_round(self) -> tuple[int, int]:
        """Play a round of the game.

        This method plays hands until one player wins 2 hands.
        If there's a tie, the first player to win the next hand wins the round.

        Returns:
            tuple[int, int]: The points for each team (team_1_points, team_2_points).
        """
        logger.info("Playing round")
        logger.info("Muestra is: %s", self.muestra)
        player_1_wins = 0
        player_2_wins = 0

        for _ in range(CARDS_DEALT_PER_PLAYER):
            hand_result = self.play_hand()
            player_1_wins += hand_result[0]
            player_2_wins += hand_result[1]

            if player_1_wins == HANDS_TO_WIN_ROUND and player_2_wins == HANDS_TO_WIN_ROUND:
                continue

            if HANDS_TO_WIN_ROUND in (player_1_wins, player_2_wins):
                # if one of the players has won the round, break
                break

        return self.get_hand_points(player_1_wins, player_2_wins)

    def play_hand(self) -> tuple[int, int]:
        """Have each player play one card and determine the winner.

        Returns:
            tuple[int, int]: The points for each team (team_1_points, team_2_points).
        """
        card_1 = self._choose_card(self.player_1)
        card_2 = self._choose_card(self.player_2)

        logger.debug("Player 1 (%s) played: %s", self.player_1.name, card_1)
        logger.debug("Player 2 (%s) played: %s", self.player_2.name, card_2)

        if card_1.is_greater_than(card_2, self.muestra):
            logger.info("%s wins with %s", self.player_1.name, card_1)
            return 1, 0
        elif card_2.is_greater_than(card_1, self.muestra):
            logger.info("%s wins with %s", self.player_2.name, card_2)
            return 0, 1
        else:
            logger.info("It's a tie! Both played equivalent cards")
            return 1, 1

    def get_hand_points(self, player_1_wins: int, player_2_wins: int) -> tuple[int, int]:
        """Get the points for the hand.

        Returns:
            tuple[int, int]: The points for each team (team_1_points, team_2_points).
        """
        truco_points = self._get_points_truco_state()

        if player_1_wins > player_2_wins:
            logger.info("Player 1 wins the round")
            return truco_points, 0
        elif player_2_wins > player_1_wins:
            logger.info("Player 2 wins the round")
            return 0, truco_points
        else:
            # rare case where there are three ties, the "hand" wins
            logger.info("All tied, the hand wins")
            return truco_points, 0
