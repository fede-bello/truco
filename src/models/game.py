from typing import Protocol, runtime_checkable

from logging_config import get_logger
from models.player import Player
from models.round import Round
from schemas.actions import ActionProvider

logger = get_logger(__name__)


# Runtime-checkable feature detection for providers that can accept a live Round.
@runtime_checkable
class SupportsSetRound(Protocol):
    """Providers that expose a set_round method for richer observations."""

    def set_round(self, round_obj: Round) -> None:
        """Attach the current Round so the provider can build full observations."""
        ...


class Game:
    """Represents a full game session tracking players and scores.

    Attributes:
        team1: The players on the first team.
        team2: The players on the second team.
        ordered_players: Interleaved turn order (T1P1, T2P1, ...).
        team1_score: Current game score for Team 1.
        team2_score: Current game score for Team 2.
        show_teammate_cards: Whether players can see teammate's hands.
    """

    def __init__(
        self,
        team1: list[Player],
        team2: list[Player],
        action_provider: ActionProvider,
        *,
        show_teammate_cards: bool = False,
    ) -> None:
        """Initialize the game with two teams and an action provider.

        Args:
            team1: List of players on the first team.
            team2: List of players on the second team.
            action_provider: Callback used by rounds to obtain player actions.
            show_teammate_cards: Whether players can see their teammate's cards.

        Raises:
            ValueError: If the team structure is invalid.
        """
        if len(team1) != len(team2):
            msg = "Teams must have equal size"
            raise ValueError(msg)
        if not team1:
            msg = "Teams cannot be empty"
            raise ValueError(msg)

        self.team1 = team1
        self.team2 = team2
        self._action_provider = action_provider
        self.show_teammate_cards = show_teammate_cards

        # Flatten players into interleaved order: T1P1, T2P1, T1P2, T2P2...
        self.ordered_players: list[Player] = []
        for i in range(len(team1)):
            self.ordered_players.append(team1[i])
            self.ordered_players.append(team2[i])

        self.team1_score = 0
        self.team2_score = 0
        self._next_round_starter_index = 0

    def play_round(self) -> None:
        """Play a round and update team scores accordingly.

        Rotates the starting player each round based on the interleaved order.
        """
        # Determine the starting player from the ordered list
        starting_player = self.ordered_players[self._next_round_starter_index]

        game_round = Round(
            team1=self.team1,
            team2=self.team2,
            ordered_players=self.ordered_players,
            action_provider=self._action_provider,
            starting_player=starting_player,
            show_teammate_cards=self.show_teammate_cards,
        )
        # If the action provider supports richer observations via `set_round`,
        # attach the live round so agents see muestra and truco state like in training.
        if isinstance(self._action_provider, SupportsSetRound):
            self._action_provider.set_round(game_round)

        team_1_points, team_2_points = game_round.play_round()
        self.team1_score += team_1_points
        self.team2_score += team_2_points

    def play_game(self, target_points: int) -> int:
        """Play successive rounds until one team reaches the target points.

        Args:
            target_points: The score threshold required to win the game.

        Returns:
            The winning team number as an integer (1 or 2).
        """
        round_count = 0
        while max(self.team1_score, self.team2_score) < target_points:
            round_count += 1
            self.play_round()

            # Rotate starter for the next round
            self._next_round_starter_index = (self._next_round_starter_index + 1) % len(
                self.ordered_players
            )

            logger.info("Round %s completed", round_count)
            logger.info("Team 1 score: %s", self.team1_score)
            logger.info("Team 2 score: %s", self.team2_score)
            logger.info("--------------------------------")

        return 1 if self.team1_score >= target_points else 2
