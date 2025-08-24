from __future__ import annotations

from typing import TYPE_CHECKING

from logging_config import get_logger
from schemas.actions import ActionCode, card_index_from_code

logger = get_logger(__name__)

if TYPE_CHECKING:
    from models.card import Card


def print_available_actions(
    player_name: str, player_cards: list[Card], actions: list[ActionCode]
) -> None:
    """Print available actions for a player given their cards.

    Args:
        player_name: Name of the acting player.
        player_cards: Cards currently in the player's hand.
        actions: Valid actions the player can take.
    """
    logger.info("Available actions for %s:", player_name)
    for action in actions:
        card_index = card_index_from_code(action)
        if card_index is not None:
            if not (0 <= card_index < len(player_cards)):
                continue
            card_str = str(player_cards[card_index])
            logger.info("Action %s: Play %s", int(action), card_str)
        elif action == ActionCode.OFFER_TRUCO:
            logger.info("Action %s: Offer Truco", int(action))
        elif action == ActionCode.ACCEPT_TRUCO:
            logger.info("Action %s: Accept Truco", int(action))
        elif action == ActionCode.REJECT_TRUCO:
            logger.info("Action %s: Reject Truco", int(action))


def prompt_action_code(player_name: str, available_actions: list[ActionCode]) -> ActionCode:
    """Prompt the user for an action code that is within available_actions."""
    prompt = f"Choose action code for {player_name}: "
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
