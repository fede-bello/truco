from exceptions.truco_rejected import TrucoRejectedError
from logging_config import get_logger
from models.card import Card
from models.deck import Deck
from models.player import Player
from schemas.actions import (
    ActionCode,
    ActionProvider,
    card_index_from_code,
)
from schemas.constants import CARDS_DEALT_PER_PLAYER, REY
from schemas.player_state import PlayerState
from schemas.round_state import TRUCO_STATE, RoundProgress, RoundState

logger = get_logger(__name__)

HANDS_TO_WIN_ROUND = CARDS_DEALT_PER_PLAYER // 2 + 1


class Round:
    """Represents a round in the card game, which is the play between dealing cards.

    Attributes:
        team1 (list[Player]): The players on team 1.
        team2 (list[Player]): The players on team 2.
        ordered_players (list[Player]): The interleaved order of players (A1, B1, A2, B2...).
        deck (Deck): The deck of cards for the round.
        muestra (Card | None): The card shown after dealing that determines the trump suit.
        show_teammate_cards (bool): Whether players can see their teammate's cards.
    """

    def __init__(
        self,
        team1: list[Player],
        team2: list[Player],
        ordered_players: list[Player],
        action_provider: ActionProvider,
        *,
        starting_player: Player,
        show_teammate_cards: bool = False,
    ) -> None:
        """Initialize a round with teams and a fresh deck.

        Args:
            team1: List of players on team 1.
            team2: List of players on team 2.
            ordered_players: Interleaved list of players.
            action_provider: Callback used to request an action.
            starting_player: The player who starts the first hand in this round.
            show_teammate_cards: Whether teammate cards are visible in PlayerState.
        """
        self.team1 = team1
        self.team2 = team2
        self.ordered_players = ordered_players
        self.deck = Deck()
        self.show_teammate_cards = show_teammate_cards

        self.round_state: RoundState = RoundState(
            truco_state="nada",
            cards_played_this_round={},
            flor_calls=[],
            player_initial_hands={},
        )
        self._deal_cards()
        self.muestra: Card

        self.last_truco_bidder: Player | None = None

        self._action_provider: ActionProvider = action_provider
        self._starting_player: Player = starting_player

    def _deal_cards(self) -> None:
        """Deal CARDS_DEALT_PER_PLAYER cards to each player and set the muestra card."""
        for player in self.ordered_players:
            player.cards = self.deck.draw(CARDS_DEALT_PER_PLAYER)
            # Store initial hand for Flor verification
            self.round_state.player_initial_hands[player] = list(player.cards)

        self.muestra = self.deck.draw(1)[0]

    def _get_teammates(self, player: Player) -> list[Player]:
        """Get the teammates of a player."""
        if player in self.team1:
            return [p for p in self.team1 if p != player]
        if player in self.team2:
            return [p for p in self.team2 if p != player]
        return []

    def _is_same_team(self, player_a: Player, player_b: Player) -> bool:
        """Check if two players are on the same team."""
        return (player_a in self.team1 and player_b in self.team1) or (
            player_a in self.team2 and player_b in self.team2
        )

    def _can_beat_truco(self, player: Player) -> bool:
        """Check if a player can beat (advance) the truco state.

        Any player from the opposing team of the last bidder can respond.
        If no one bid yet, anyone can start.
        """
        if self.round_state.truco_state == "vale4":
            return False

        if self.last_truco_bidder is None:
            return True

        # Must be on the opposite team of the last bidder
        return not self._is_same_team(player, self.last_truco_bidder)

    def _get_available_actions(self, player: Player) -> list[ActionCode]:
        """Compute the available actions for a player at this moment."""
        actions: list[ActionCode] = []

        # Card play actions: one per card in hand
        # Assuming max 3 cards dealt
        for i, _ in enumerate(player.cards):
            mapping = {
                0: ActionCode.PLAY_CARD_0,
                1: ActionCode.PLAY_CARD_1,
                2: ActionCode.PLAY_CARD_2,
            }
            action = mapping.get(i)
            if action is not None:
                actions.append(action)

        if self._can_beat_truco(player):
            actions.append(ActionCode.OFFER_TRUCO)

        # Flor: only available on the first turn of the round
        if (
            len(player.cards) == CARDS_DEALT_PER_PLAYER
            and player not in self.round_state.flor_calls
        ):
            actions.append(ActionCode.FLOR)

        # Envido: only available in the first trick, if no Flor has been called
        # and no Envido has been bid yet.
        if (
            len(player.cards) == CARDS_DEALT_PER_PLAYER
            and not self.round_state.flor_calls
            and self.round_state.envido_state == "nada"
        ):
            actions.append(ActionCode.OFFER_ENVIDO)

        return actions

    def _request_action(self, player: Player, available_actions: list[ActionCode]) -> ActionCode:
        """Request an action from the external provider and validate it."""
        player_state = self.get_player_state(player)
        chosen_action = self._action_provider(player, player_state, available_actions)

        for candidate in available_actions:
            if candidate == chosen_action:
                return candidate

        msg = f"Invalid action selected by provider: {chosen_action}. Valid: {available_actions}"
        logger.error(msg)
        raise ValueError(msg)

    def _get_points_truco_state(self) -> int:
        """Get the points for the current truco state.

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
        """Advance the truco state to the next level.

        Returns:
            TRUCO_STATE: The new enhanced truco state.
        """
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

    def _get_next_player(self, current_player: Player) -> Player:
        """Get the next player in the circular order.

        Args:
            current_player: The player currently acting.

        Returns:
            Player: The next player in the interleaved order.
        """
        idx = self.ordered_players.index(current_player)
        return self.ordered_players[(idx + 1) % len(self.ordered_players)]

    def _play_hand(self, starting_player: Player) -> Player | None:
        """Play a single hand (trick) where each player plays one card.

        Iterates through all players starting from `starting_player` in circular order.

        Args:
            starting_player: The player who leads the first card of this hand.

        Returns:
            Player | None: The player who won the hand, or None if it's a tie.
        """
        current_best_card: Card | None = None
        current_winner: Player | None = None
        is_tie = False

        # Order for this trick: start with starter, go around
        start_idx = self.ordered_players.index(starting_player)
        trick_order = self.ordered_players[start_idx:] + self.ordered_players[:start_idx]

        for player in trick_order:
            card = self._handle_player_turn(player)
            if card is None:
                # Should not happen in normal flow as rejection raises error
                logger.error("Unexpected None card from %s", player.name)
                continue

            logger.debug("%s plays %s", player.name, card)

            if current_best_card is None:
                current_best_card = card
                current_winner = player
            elif card.is_greater_than(current_best_card, self.muestra):
                current_best_card = card
                current_winner = player
                is_tie = False
            elif current_best_card.is_greater_than(card, self.muestra):
                pass  # Current best stays best
            else:
                # Tie with current best
                is_tie = True
                # In a tie, we track that it's a tie, but we don't change 'current_winner'
                # arbitrarily yet. Tie logic is handled by caller or resolved winner is None.

        if is_tie:
            logger.debug("Hand tied with best card %s", current_best_card)
            return None

        logger.debug(
            "Hand winner: %s with %s",
            current_winner.name if current_winner else "None",
            current_best_card,
        )
        return current_winner

    def _handle_player_turn(self, player: Player) -> Card | None:
        """Handle a player's turn, which may include truco bidding.

        Args:
            player: The player whose turn it is.

        Returns:
            Card | None: The card played, or None if a truco challenge was rejected.
        """
        available = self._get_available_actions(player)
        action = self._request_action(player, available)

        if action == ActionCode.OFFER_TRUCO:
            return self._handle_truco_bid(player)
        if action == ActionCode.OFFER_ENVIDO:
            return self._handle_envido_bid(player)
        if action == ActionCode.FLOR:
            logger.info("%s says FLOR!", player.name)
            self.round_state.flor_calls.append(player)
            # After saying Flor, the player must still play a card (or bid truco)
            return self._handle_player_turn(player)
        if action in {ActionCode.ACCEPT_TRUCO, ActionCode.REJECT_TRUCO}:
            msg = "Accept/Reject truco is not valid on a regular turn"
            logger.error(msg)
            raise ValueError(msg)

        # Play selected card
        card_index = card_index_from_code(action)
        if card_index is None:
            msg = "Play card action code must map to a card index"
            logger.error(msg)
            raise ValueError(msg)
        card = player.play_card(card_index)
        self.round_state.cards_played_this_round[player] = card
        return card

    def _handle_truco_bid(self, bidding_player: Player) -> Card | None:
        """Handle a truco bid from a player.

        The next player in rotation (who is an opponent) is asked to respond.

        Args:
            bidding_player: The player initiating the truco challenge.

        Returns:
            Card | None: The card played after truco resolution, or None if rejected.

        Raises:
            TrucoRejectedError: To signal immediate round end on rejection.
        """
        current_state = self.round_state.truco_state
        next_state_name = {"nada": "truco", "truco": "retruco", "retruco": "vale4"}.get(
            current_state, current_state
        )

        self.last_truco_bidder = bidding_player
        logger.debug("%s bids %s", bidding_player.name, next_state_name)

        # In team truco, typically the next player (opponent) responds
        responder = self._get_next_player(bidding_player)

        # Ensure responder is actually on the other team (sanity check)
        if self._is_same_team(bidding_player, responder):
            # This should not happen with alternating order
            logger.warning("Truco responder is on same team as bidder!")

        response = self._request_action(
            responder,
            [ActionCode.ACCEPT_TRUCO, ActionCode.REJECT_TRUCO],
        )

        if response == ActionCode.ACCEPT_TRUCO:
            logger.debug("%s accepts truco", responder.name)
            self._advance_truco_state()
            # Continue with bidding player playing a card
            return self._handle_player_turn(bidding_player)

        # Rejection: The bidding team wins the round immediately
        raise TrucoRejectedError(bidding_player)

    def _handle_envido_bid(self, bidding_player: Player) -> Card | None:
        """Handle an Envido bid from a player.

        Args:
            bidding_player: The player initiating the Envido challenge.

        Returns:
            Card | None: The card played after Envido resolution.
        """
        logger.debug("%s bids ENVIDO", bidding_player.name)
        self.round_state.envido_state = "envido"
        self.round_state.envido_bidder = bidding_player

        # The next player (opponent) responds
        responder = self._get_next_player(bidding_player)

        # Response options: Quiero, No Quiero, Flor
        available_responses = [
            ActionCode.ACCEPT_ENVIDO,
            ActionCode.REJECT_ENVIDO,
        ]
        # Opponent can respond with Flor if they have one
        available_responses.append(ActionCode.FLOR)

        response = self._request_action(responder, available_responses)

        if response == ActionCode.FLOR:
            # Flor overrides Envido (Rule 3)
            logger.info("%s responds with FLOR to Envido!", responder.name)
            self.round_state.flor_calls.append(responder)
            self.round_state.envido_state = "nada"  # Canceled
            # After saying Flor, the player must still play a card (or bid truco)
            # But the turn should continue with the bidding_player?
            # In the original flow, _handle_truco_bid returns _handle_player_turn(bidding_player).
            # Same here.
            return self._handle_player_turn(bidding_player)

        if response == ActionCode.ACCEPT_ENVIDO:
            logger.debug("%s accepts Envido", responder.name)
            self.round_state.envido_state = "querido"
            self._resolve_envido_comparison()
            return self._handle_player_turn(bidding_player)

        # No quiero
        logger.debug("%s rejects Envido", responder.name)
        self.round_state.envido_state = "no_quiero"
        # 1 point for the bidding team
        team_idx = 1 if bidding_player in self.team1 else 2
        self.round_state.envido_points[team_idx] += 1
        return self._handle_player_turn(bidding_player)

    def _resolve_envido_comparison(self) -> None:
        """Compare Envido values and award 2 points to the winner.

        Players announce values in the same order in which they played their first card.
        They only announce if necessary (to beat the current highest) or say 'son buenas'.
        Teammates remain silent if their team already holds the lead.
        """
        # Get play order for the first trick
        start_idx = self.ordered_players.index(self._starting_player)
        trick_order = self.ordered_players[start_idx:] + self.ordered_players[:start_idx]

        highest_announced_val = -1
        current_winner = None

        for player in trick_order:
            if current_winner and self._is_same_team(player, current_winner):
                # Teammate silent if their team already has the lead
                continue

            val = self.calculate_envido(self.round_state.player_initial_hands[player])

            # In truco, if values are equal, the one earlier in play order (player)
            # wins. Since we iterate in trick_order, only '>' changes the winner.
            if val > highest_announced_val:
                logger.info("%s has %d", player.name, val)
                highest_announced_val = val
                current_winner = player
            else:
                logger.info("%s says 'son buenas'", player.name)

        if current_winner:
            team_idx = 1 if current_winner in self.team1 else 2
            self.round_state.envido_points[team_idx] += 2
            logger.info("Team %d wins Envido", team_idx)

    def _determine_round_winner(
        self, team_1_wins: int, team_2_wins: int, hand_results: list[Player | None]
    ) -> tuple[int, int]:
        """Determine the winner when win counts are equal after 3 hands.

        Args:
            team_1_wins: Hands won by Team 1.
            team_2_wins: Hands won by Team 2.
            hand_results: Sequence of winners for each played hand.

        Returns:
            tuple[int, int]: Final win counts (forced to win threshold for the victor).
        """
        if team_1_wins > team_2_wins:
            return HANDS_TO_WIN_ROUND, 0
        if team_2_wins > team_1_wins:
            return 0, HANDS_TO_WIN_ROUND

        # Tie rules logic if win counts are equal (0-0 or 1-1 with ties)
        return self._resolve_tied_match(hand_results)

    def _resolve_tied_match(self, hand_results: list[Player | None]) -> tuple[int, int]:
        """Resolve a match that ended in a tie count based on Truco rules."""
        first_winner = hand_results[0]

        # Case: 3 ties or 1st tie
        if first_winner is None:
            # If all 3 tied, starter of 1st wins
            if all(r is None for r in hand_results):
                return self._winner_from_player(self._starting_player)

            # Tie 1st: Winner of 2nd wins (or 3rd if 2nd also tied)
            for winner in hand_results[1:]:
                if winner:
                    return self._winner_from_player(winner)

            # Fallback (should not happen with logic above)
            return self._winner_from_player(self._starting_player)

        # First not tied, but match ended in tie count (e.g. T1 won 1st, T2 won 2nd, 3rd tied)
        # First trick winner wins round.
        return self._winner_from_player(first_winner)

    def _winner_from_player(self, player: Player) -> tuple[int, int]:
        """Convert a winning player to a team point tuple."""
        if player in self.team1:
            return HANDS_TO_WIN_ROUND, 0
        return 0, HANDS_TO_WIN_ROUND

    def _apply_tie_shortcuts(
        self,
        *,
        hand_index: int,
        first_trick_tied: bool,
        first_trick_winner: Player | None,
        current_hand_winner: Player | None,
    ) -> Player | None:
        """Apply early-termination tie rules.

        Args:
            hand_index: Index of the current hand (0-2).
            first_trick_tied: Whether the first hand was a tie.
            first_trick_winner: Winner of the first hand if any.
            current_hand_winner: Winner of the current hand if any.

        Returns:
            Player | None: A player from the winning team if decided, else None.
        """
        # If first trick was tied, whoever wins the second trick wins the round
        if hand_index == 1 and first_trick_tied and current_hand_winner is not None:
            return current_hand_winner

        # If 2nd trick is tied and 1st had a winner, the 1st trick winner wins the round
        if (
            hand_index == 1
            and (not first_trick_tied)
            and current_hand_winner is None
            and first_trick_winner is not None
        ):
            return first_trick_winner

        return None

    def play_round(self) -> tuple[int, int]:
        """Play a round of the game and return points for each team.

        Returns:
            tuple[int, int]: (team_1_points, team_2_points).
        """
        logger.debug(
            "Playing round w/ teams: %s vs %s",
            [p.name for p in self.team1],
            [p.name for p in self.team2],
        )
        logger.info("Muestra is: %s", self.muestra)

        team_1_wins, team_2_wins = self._execute_round()
        return self.get_hand_points(team_1_wins, team_2_wins)

    def _execute_round(self) -> tuple[int, int]:
        """Execute the trick-by-trick logic for a round.

        Returns:
            tuple[int, int]: (team_1_wins, team_2_wins) for the round.
        """
        progress = RoundProgress(
            current_starter=self._starting_player,
            team_1_wins=0,
            team_2_wins=0,
            first_trick_tied=False,
            first_trick_winner=None,
        )

        hand_results: list[Player | None] = []

        try:
            for hand_num in range(CARDS_DEALT_PER_PLAYER):
                hand_winner = self._play_hand_step(hand_num, progress)
                hand_results.append(hand_winner)

                # Early exit if a team already won enough tricks
                if progress.team_1_wins >= HANDS_TO_WIN_ROUND:
                    return HANDS_TO_WIN_ROUND, 0
                if progress.team_2_wins >= HANDS_TO_WIN_ROUND:
                    return 0, HANDS_TO_WIN_ROUND

                # Early exit for tie shortcuts (e.g. 1st tie, 2nd winner takes all)
                shortcut_winner = self._apply_tie_shortcuts(
                    hand_index=hand_num,
                    first_trick_tied=progress.first_trick_tied,
                    first_trick_winner=progress.first_trick_winner,
                    current_hand_winner=hand_winner,
                )
                if shortcut_winner:
                    return self._winner_from_player(shortcut_winner)

            return self._determine_round_winner(
                progress.team_1_wins, progress.team_2_wins, hand_results
            )

        except TrucoRejectedError as error:
            logger.debug("Round ended due to truco rejection")
            return self._winner_from_player(error.winning_player)

    def _play_hand_step(self, hand_num: int, progress: RoundProgress) -> Player | None:
        """Play a single hand and update progress."""
        logger.debug("--------------------------------")
        logger.debug("Playing hand %d, %s starts", hand_num + 1, progress.current_starter.name)

        hand_winner = self._play_hand(progress.current_starter)

        # Track results for first trick
        if hand_num == 0:
            if hand_winner is None:
                progress.first_trick_tied = True
            else:
                progress.first_trick_winner = hand_winner

        # Update starter and scores if there's a winner
        if hand_winner:
            progress.current_starter = hand_winner
            if hand_winner in self.team1:
                progress.team_1_wins += 1
            else:
                progress.team_2_wins += 1

        return hand_winner

    def get_hand_points(self, team_1_wins: int, team_2_wins: int) -> tuple[int, int]:
        """Convert round win counts into game points based on truco state.

        Args:
            team_1_wins: Total hands won by Team 1.
            team_2_wins: Total hands won by Team 2.

        Returns:
            tuple[int, int]: (team_1_points, team_2_points).
        """
        truco_points = self._get_points_truco_state()

        team_1_points = 0
        team_2_points = 0

        if team_1_wins > team_2_wins:
            logger.debug("Team 1 wins the round")
            team_1_points = truco_points
        elif team_2_wins > team_1_wins:
            logger.debug("Team 2 wins the round")
            team_2_points = truco_points
        else:
            # Fallback for rare full tie
            logger.debug("All tied, determine by starter logic (Hand wins)")
            if self._starting_player in self.team1:
                team_1_points = truco_points
            else:
                team_2_points = truco_points

        # Calculate Flor points
        for player in self.round_state.flor_calls:
            has_real_flor = self._has_flor(self.round_state.player_initial_hands[player])
            points = 3
            if player in self.team1:
                if has_real_flor:
                    team_1_points += points
                else:
                    team_2_points += points
            elif has_real_flor:
                team_2_points += points
            else:
                team_1_points += points

        # Add Envido points
        team_1_points += self.round_state.envido_points[1]
        team_2_points += self.round_state.envido_points[2]

        return team_1_points, team_2_points

    def get_player_state(self, player: Player) -> PlayerState:
        """Get the observable state for a specific player.

        Args:
            player: The player whose perspective to build the state for.

        Returns:
            PlayerState: A snapshot of the game visible to the player.
        """
        round_state = self.round_state
        player_cards = player.cards

        teammate_cards = None
        if self.show_teammate_cards:
            teammates = self._get_teammates(player)
            # Flatten all teammate cards into one list
            teammate_cards = [card for p in teammates for card in p.cards]

        return PlayerState(
            round_state=round_state,
            player_cards=player_cards,
            teammate_cards=teammate_cards,
        )

    def _has_flor(self, cards: list[Card]) -> bool:
        """Check if a list of cards constitutes a Flor.

        A Flor is:
        - Three cards from the same suit.
        - One pieza and the other two from the same suit.
        - Two or more piezas.

        Args:
            cards: The list of cards to check (usually 3).

        Returns:
            bool: True if it's a Flor, False otherwise.
        """
        if len(cards) != 3:
            return False

        piezas = [c for c in cards if c.is_pieza(self.muestra)]
        non_piezas = [c for c in cards if not c.is_pieza(self.muestra)]

        # Two or more piezas
        if len(piezas) >= 2:
            return True

        # One pieza and the other two from the same suit
        if len(piezas) == 1:
            return non_piezas[0].suit == non_piezas[1].suit

        # Zero piezas and all three from the same suit
        return cards[0].suit == cards[1].suit == cards[2].suit

    def calculate_envido(self, cards: list[Card]) -> int:
        """Calculate the Envido value for a hand of cards.

        Args:
            cards: The list of cards to calculate Envido for.

        Returns:
            int: The Envido value.
        """
        if not cards:
            return 0

        piezas = [c for c in cards if c.is_pieza(self.muestra)]
        # Pieza values for Envido
        pieza_envido_values = {2: 30, 4: 29, 5: 28, 11: 27, 10: 27}

        if piezas:
            # Case A: Hand Contains a Pieza
            # Take the highest pieza value
            highest_pieza_val = 0
            for p in piezas:
                # If it's a 12 (Rey), it takes the value of the pieza it's replacing
                p_num = p.number if p.number != REY else self.muestra.number
                highest_pieza_val = max(highest_pieza_val, pieza_envido_values[p_num])

            # Add the highest Envido-value card among the remaining two cards
            # We need to be careful: if we have multiple piezas, the "remaining" cards
            # are the ones not used for the 'highest_pieza_val'.
            # Wait, the rule says "Take the highest pieza value.
            # Add the highest Envido-value card among the remaining two cards."
            # This implies if you have 2 piezas, you take the best one,
            # and then look at the other 2 cards (one of which is ALSO a pieza)
            # and take the best Envido value from them.

            # Find the card that gave the highest_pieza_val
            best_pieza = None
            for p in piezas:
                p_num = p.number if p.number != REY else self.muestra.number
                if pieza_envido_values[p_num] == highest_pieza_val:
                    best_pieza = p
                    break

            remaining_cards = list(cards)
            remaining_cards.remove(best_pieza)

            # For the remaining cards, we need their Envido value.
            # Normal cards use get_envido_value().
            # Piezas use their pieza_envido_values.
            # If the remaining is another pieza, does it count as 30/29/etc
            # or as facial? Usually it's the facial value for the second card.
            # Let's check Example 2 again. 4 (pieza) is 29. 6 is 6. 29+6=35.
            # If I had two piezas, say 2 and 4. 2 is 30. 4 is 29.
            # Usually the second card is its facial value if not used as base.

            max_remaining_val = max(c.get_envido_value() for c in remaining_cards)
            return highest_pieza_val + max_remaining_val

        # Cases B & C: No Piezas
        # Group by suit
        suit_groups: dict[str, list[Card]] = {}
        for c in cards:
            suit_groups.setdefault(c.suit, []).append(c)

        max_envido = 0
        for suit_cards in suit_groups.values():
            if len(suit_cards) >= 2:
                # Case C: No Pieza, Two (or three) Cards of the Same Suit
                # Take the two highest Envido-value cards of the same suit. Add 20 bonus points.
                vals = sorted([c.get_envido_value() for c in suit_cards], reverse=True)
                envido_val = vals[0] + vals[1] + 20
                max_envido = max(max_envido, envido_val)
            else:
                # Case B: No Pieza, All Cards Different Suits (or just this one)
                # Envido = highest single card value.
                envido_val = suit_cards[0].get_envido_value()
                max_envido = max(max_envido, envido_val)

        return max_envido
