from models.player import Player


class TrucoRejectedError(Exception):
    """Exception raised when a truco bid is rejected, ending the round."""

    def __init__(self, winning_player: Player) -> None:
        """Initialize the exception with the winning player.

        Args:
            winning_player: The player who wins due to truco rejection.
        """
        self.winning_player = winning_player
        super().__init__(f"Truco rejected, {winning_player.name} wins the round")
