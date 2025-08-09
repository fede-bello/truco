from models.player import Player
from models.round import Round
from schemas.actions import ActionProvider


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
