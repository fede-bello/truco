from exceptions.truco_rejected import TrucoRejectedError
from logging_config import get_logger
from models.card import Card
from models.deck import Deck
from models.player import Player
from schemas.constants import CARDS_DEALT_PER_PLAYER
from schemas.hand_info import RoundInfo
from schemas.player_state import PlayerState
from schemas.round_state import TRUCO_STATE, RoundState

logger = get_logger(__name__)

HANDS_TO_WIN_ROUND = CARDS_DEALT_PER_PLAYER // 2 + 1

TRUCO_BID_OFFER_ACTION = 4
TRUCO_BID_ACCEPT_ACTION = 5
TRUCO_BID_REJECT_ACTION = 6

TRUCO_ACTIONS = [TRUCO_BID_OFFER_ACTION, TRUCO_BID_ACCEPT_ACTION, TRUCO_BID_REJECT_ACTION]


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

        self.round_state: RoundState = RoundState(truco_state="nada", cards_played_this_round={})
        self.last_truco_bidder: Player | None = None

        self.truco_bid_offered: bool = False

    def _deal_cards(self) -> None:
        """Deal CARDS_DEALT_PER_PLAYER cards to each player and set the muestra card.

        This method draws CARDS_DEALT_PER_PLAYER cards for each player and assigns them directly
        to the player's hand. After dealing to all players, it draws one card to be the muestra.
        """
        for player in [self.player_1, self.player_2]:
            player.cards = self.deck.draw(CARDS_DEALT_PER_PLAYER)

        self.muestra = self.deck.draw(1)[0]

    def _can_beat_truco(self, player: Player) -> bool:
        """Check if a player can beat (advance) the truco state.

        Args:
            player (Player): The player who wants to beat truco.

        Returns:
            bool: True if the player can beat truco, False otherwise.
        """
        # Cannot advance beyond vale4
        if self.round_state.truco_state == "vale4":
            return False

        # If no one has bid yet, anyone can start
        if self.last_truco_bidder is None:
            return True

        # Only the other player can advance (alternating rule)
        return player != self.last_truco_bidder

    def _show_actions(self, player: Player) -> None:
        """Show available actions for a player and return the truco option index.

        Args:
            player (Player): The player to show actions for.

        Returns:
            int: The index that would be used for the truco beat option.
        """
        if self.truco_bid_offered:
            logger.info("Truco bid offered, player must accept or reject")
            logger.info("%s: Accept truco", TRUCO_BID_ACCEPT_ACTION)
            logger.info("%s: Reject truco", TRUCO_BID_REJECT_ACTION)
            return

        # Show cards with their indices
        for i, card in enumerate(player.cards):
            logger.info("%s: %s", i, card)

        if self._can_beat_truco(player):
            current_state = self.round_state.truco_state
            next_state_name = {"nada": "truco", "truco": "retruco", "retruco": "vale4"}.get(
                current_state, current_state
            )
            logger.info("%s: Beat truco to %s", TRUCO_BID_OFFER_ACTION, next_state_name)

    def _choose_action(self, player: Player) -> Card | int:
        """Choose an action for the player (play card or truco action).

        Args:
            player (Player): The player to choose an action for.

        Returns:
            Card | int: The card played or the truco action code.
        """
        self._show_actions(player)

        while True:
            try:
                choice = int(input(f"Choose action for {player.name}: "))

                if choice in TRUCO_ACTIONS:
                    return choice

                # Validate card index
                if 0 <= choice < len(player.cards):
                    card = player.play_card(choice)
                    self.round_state.cards_played_this_round[player] = card
                    return card
                else:
                    logger.warning("Invalid card index. Please choose a valid card.")
                    continue

            except (ValueError, IndexError):
                logger.warning("Invalid input. Please enter a number.")
                continue

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

    def _advance_truco_state(self) -> TRUCO_STATE:
        """Advance the truco state."""
        match self.round_state.truco_state:
            case "nada":
                self.round_state.truco_state = "truco"
            case "truco":
                self.round_state.truco_state = "retruco"
            case "retruco":
                self.round_state.truco_state = "vale4"
            case "vale4":
                msg = "Cannot advance truco state from vale4"
                logger.error(msg)
                raise ValueError(msg)

        return self.round_state.truco_state

    def _play_hand(self, starting_player: Player) -> Player | None:
        """Play a single hand between two players.

        Args:
            starting_player (Player): The player who starts this hand.

        Returns:
            Player | None: The player who won the hand, or None if it's a tie.
        """
        other_player = self.player_2 if starting_player == self.player_1 else self.player_1

        # First player plays
        card_1 = self._handle_player_turn(starting_player)
        if card_1 is None:
            logger.error("Unexpected None card from first player")
            return other_player

        # Second player plays
        card_2 = self._handle_player_turn(other_player)
        if card_2 is None:
            logger.error("Unexpected None card from second player")
            return starting_player

        # Compare cards to determine winner
        if card_1.is_greater_than(card_2, self.muestra):
            logger.info("%s wins hand with %s vs %s", starting_player.name, card_1, card_2)
            return starting_player
        elif card_2.is_greater_than(card_1, self.muestra):
            logger.info("%s wins hand with %s vs %s", other_player.name, card_2, card_1)
            return other_player
        else:
            logger.info("Hand tied with %s vs %s", card_1, card_2)
            return None  # Tie

    def _handle_player_turn(self, player: Player) -> Card | None:
        """Handle a player's turn, which may include truco bidding.

        Args:
            player (Player): The player whose turn it is.

        Returns:
            Card | None: The card played, or None if truco was rejected.
        """
        while True:
            action = self._choose_action(player)

            if isinstance(action, int):  # Truco action
                if action == TRUCO_BID_OFFER_ACTION:
                    return self._handle_truco_bid(player)
                elif action == TRUCO_BID_ACCEPT_ACTION:
                    self.truco_bid_offered = False
                    # The accepting player doesn't become the bidder
                    continue  # Player still needs to play a card
                elif action == TRUCO_BID_REJECT_ACTION:
                    logger.error("Unexpected truco rejection in player turn")
                    return None
            else:  # Card played
                return action

    def _handle_truco_bid(self, bidding_player: Player) -> Card | None:
        """Handle a truco bid from a player.

        Args:
            bidding_player (Player): The player making the truco bid.

        Returns:
            Card | None: The card played after truco resolution, or None if rejected.

        Raises:
            TrucoRejectedError: When truco is rejected, indicating the round should end.
        """
        other_player = self.player_2 if bidding_player == self.player_1 else self.player_1

        # Store current state and determine what the bid would advance to
        current_state = self.round_state.truco_state
        next_state_name = {"nada": "truco", "truco": "retruco", "retruco": "vale4"}.get(
            current_state, current_state
        )

        self.last_truco_bidder = bidding_player
        logger.info("%s bids %s", bidding_player.name, next_state_name)

        # Other player must respond
        self.truco_bid_offered = True
        response = self._choose_action(other_player)

        if response == TRUCO_BID_ACCEPT_ACTION:
            logger.info("%s accepts truco", other_player.name)
            # Only now advance the truco state since it was accepted
            self._advance_truco_state()
            self.truco_bid_offered = False
            # Continue with bidding player playing a card
            return self._handle_player_turn(bidding_player)
        else:  # TRUCO_BID_REJECT_ACTION
            logger.info(
                "%s rejects truco - round ends, %s wins", other_player.name, bidding_player.name
            )
            raise TrucoRejectedError(bidding_player)

    def _determine_round_winner(
        self, player_1_wins: int, player_2_wins: int, hand_results: list[Player | None]
    ) -> tuple[int, int]:
        """Determine the winner when all hands are tied.

        Args:
            player_1_wins: Number of hands won by player 1.
            player_2_wins: Number of hands won by player 2.
            hand_results: List of hand winners (or None for ties).

        Returns:
            tuple[int, int]: Updated win counts.
        """
        if player_1_wins != player_2_wins:
            return player_1_wins, player_2_wins

        # Find who won the first hand that wasn't tied
        for result in hand_results:
            if result is not None:
                if result == self.player_1:
                    return HANDS_TO_WIN_ROUND, 0
                else:
                    return 0, HANDS_TO_WIN_ROUND

        # All hands were tied - very rare case, player 1 wins by convention
        logger.info("All hands tied, player 1 wins by convention")
        return HANDS_TO_WIN_ROUND, 0

    def play_round(self) -> tuple[int, int]:
        """Play a round of the game.

        This method plays hands until one player wins 2 hands.
        If there's a tie, the first player to win the next hand wins the round.
        If truco is rejected, the round ends immediately.

        Returns:
            tuple[int, int]: The points for each team (team_1_points, team_2_points).
        """
        logger.info("Playing round")
        logger.info("Muestra is: %s", self.muestra)

        player_1_wins = 0
        player_2_wins = 0
        hand_results: list[Player | None] = []

        # Player 1 starts the first hand
        current_starter = self.player_1

        try:
            for hand_num in range(CARDS_DEALT_PER_PLAYER):
                logger.info("Playing hand %d, %s starts", hand_num + 1, current_starter.name)

                hand_winner = self._play_hand(current_starter)
                hand_results.append(hand_winner)

                if hand_winner == self.player_1:
                    player_1_wins += 1
                    current_starter = self.player_1  # Winner starts next hand
                elif hand_winner == self.player_2:
                    player_2_wins += 1
                    current_starter = self.player_2  # Winner starts next hand

                # Check if someone has won the round
                if HANDS_TO_WIN_ROUND in {player_1_wins, player_2_wins}:
                    break

            # Handle tie-breaking
            player_1_wins, player_2_wins = self._determine_round_winner(
                player_1_wins, player_2_wins, hand_results
            )

        except TrucoRejectedError as e:
            # Truco was rejected, round ends immediately
            logger.info("Round ended due to truco rejection")
            if e.winning_player == self.player_1:
                player_1_wins = HANDS_TO_WIN_ROUND
                player_2_wins = 0
            else:
                player_1_wins = 0
                player_2_wins = HANDS_TO_WIN_ROUND

        return self.get_hand_points(player_1_wins, player_2_wins)

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

    def get_player_state(self, player: Player) -> PlayerState:
        """Get the state of a player."""
        round_state = self.round_state
        player_cards = player.cards
        return PlayerState(round_state=round_state, player_cards=player_cards)
