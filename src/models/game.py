from models.player import Player
from models.round import Round


class Game:
    def __init__(self, player_1: Player, player_2: Player) -> None:
        if player_1 == player_2:
            msg = "Players must be different"
            raise ValueError(msg)

        self.player_1 = player_1
        self.player_2 = player_2

        self.team1_score = 0
        self.team2_score = 0

    def play_round(self) -> None:
        """Play a round of the game."""
        game_round = Round(self.player_1, self.player_2)
        team_1_points, team_2_points = game_round.play_round()
        self.team1_score += team_1_points
        self.team2_score += team_2_points
