from logging_config import get_logger
from models.player import Player
from models.round import Round
from schemas.actions import ActionProvider

logger = get_logger(__name__)


class Game:
    """Represents a full game session tracking players and scores."""

    def __init__(self, player_1: Player, player_2: Player, action_provider: ActionProvider) -> None:
        """Initialize the game with two players and an action provider.

        Args:
            player_1: The first player.
            player_2: The second player.
            action_provider: Callback used by rounds to obtain player actions.

        Raises:
            ValueError: If both references point to the same player.
        """
        if player_1 == player_2:
            msg = "Players must be different"
            raise ValueError(msg)

        self.player_1 = player_1
        self.player_2 = player_2

        self.team1_score = 0
        self.team2_score = 0
        self._action_provider = action_provider

    def play_round(self) -> None:
        """Play a round and update team scores accordingly."""
        game_round = Round(self.player_1, self.player_2, self._action_provider)
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
            logger.info("Round %s completed", round_count)
            logger.info("Team 1 score: %s", self.team1_score)
            logger.info("Team 2 score: %s", self.team2_score)
            logger.info("--------------------------------")

        return 1 if self.team1_score >= target_points else 2
