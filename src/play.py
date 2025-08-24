from logging_config import get_logger
from models.game import Game
from models.player import Player
from schemas.actions import ActionCode, ActionProvider
from schemas.player_state import PlayerState
from utils.cli_actions import print_available_actions, prompt_action_code

logger = get_logger(__name__)


def _cli_action_provider(
    player: Player, player_state: PlayerState, available_actions: list[ActionCode]
) -> ActionCode:
    """Simple CLI-based action provider for human input.

    Args:
        player: Acting player.
        player_state: Current visible state for the player.
        available_actions: Valid actions player can take now.

    Returns:
        The chosen `Action` from the available list.
    """
    print_available_actions(player.name, player_state.player_cards, available_actions)
    return prompt_action_code(player.name, available_actions)


def play(target_points: int = 10) -> None:
    """Run a full game loop with two human players via CLI."""
    player_1 = Player("Player 1")
    player_2 = Player("Player 2")
    action_provider: ActionProvider = _cli_action_provider
    game = Game(player_1, player_2, action_provider)

    winner_team = game.play_game(target_points=target_points)

    logger.info("Final Team 1 score: %s", game.team1_score)
    logger.info("Final Team 2 score: %s", game.team2_score)
    logger.info("Winner: Team %s", winner_team)


if __name__ == "__main__":
    play()
