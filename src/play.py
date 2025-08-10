from logging_config import get_logger
from models.game import Game
from models.player import Player
from schemas.actions import (
    ActionCode,
    ActionProvider,
    card_index_from_code,
)
from schemas.player_state import PlayerState

logger = get_logger(__name__)


def _print_available_actions(
    player_name: str, player_state: PlayerState, actions: list[ActionCode]
) -> None:
    """Log available actions for the given player."""
    logger.info("Available actions for %s:", player_name)
    for action in actions:
        card_index = card_index_from_code(action)
        if card_index is not None:
            if not (0 <= card_index < len(player_state.player_cards)):
                continue
            card_str = str(player_state.player_cards[card_index])
            logger.info("Action %s: Play %s", int(action), card_str)
        elif action == ActionCode.OFFER_TRUCO:
            logger.info("Action %s: Offer Truco", int(action))
        elif action == ActionCode.ACCEPT_TRUCO:
            logger.info("Action %s: Accept Truco", int(action))
        elif action == ActionCode.REJECT_TRUCO:
            logger.info("Action %s: Reject Truco", int(action))


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
    _print_available_actions(player.name, player_state, available_actions)
    valid_codes = {int(code) for code in available_actions}
    prompt = f"Choose action code for {player.name} (valid: {sorted(valid_codes)}): "
    while True:
        try:
            choice = int(input(prompt))
            chosen = ActionCode(choice)
            if chosen in available_actions:
                logger.info("Selected action code: %s", int(chosen))
                return chosen
            logger.warning("Action code %s is not available right now.", choice)
        except ValueError:
            logger.warning("Invalid input. Please enter a valid integer action code.")


def play() -> None:
    """Run a full game loop until a team reaches 40 points."""
    player_1 = Player("Player 1")
    player_2 = Player("Player 2")
    action_provider: ActionProvider = _cli_action_provider
    game = Game(player_1, player_2, action_provider)

    winner_team = game.play_game(target_points=40)

    logger.info("Final Team 1 score: %s", game.team1_score)
    logger.info("Final Team 2 score: %s", game.team2_score)
    logger.info("Winner: Team %s", winner_team)


play()
# %%
