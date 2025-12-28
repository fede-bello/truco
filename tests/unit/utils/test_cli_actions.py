from unittest.mock import patch

from models.card import Card
from schemas.actions import ActionCode
from utils.cli_actions import print_available_actions, prompt_action_code


@patch("utils.cli_actions.logger")
def test_print_available_actions(mock_logger):
    player_name = "A1"
    player_cards = [Card(1, "espadas"), Card(7, "oro")]
    actions = [ActionCode.PLAY_CARD_0, ActionCode.OFFER_TRUCO]

    print_available_actions(player_name, player_cards, actions)

    # Check if logger was called for each action
    assert mock_logger.info.call_count >= 3  # "Available actions...", card action, truco action

    # Verify specific log calls
    mock_logger.info.assert_any_call("Available actions for %s:", "A1")
    mock_logger.info.assert_any_call("Action %s: Play %s", 0, "1 of espadas")
    mock_logger.info.assert_any_call("Action %s: Offer Truco", 3)


@patch("utils.cli_actions.input")
@patch("utils.cli_actions.logger")
def test_prompt_action_code_valid(mock_logger, mock_input):
    mock_input.return_value = "0"
    available_actions = [ActionCode.PLAY_CARD_0, ActionCode.OFFER_TRUCO]

    result = prompt_action_code("A1", available_actions)

    assert result == ActionCode.PLAY_CARD_0
    mock_logger.info.assert_any_call("Selected action code: %s", 0)


@patch("utils.cli_actions.input")
@patch("utils.cli_actions.logger")
def test_prompt_action_code_retry_invalid(mock_logger, mock_input):
    # First "4" (valid ActionCode but not available), then "abc" (ValueError), then "3" (valid and available)
    # ActionCode(4) is ACCEPT_TRUCO
    mock_input.side_effect = ["4", "abc", "3"]
    available_actions = [ActionCode.PLAY_CARD_0, ActionCode.OFFER_TRUCO]

    result = prompt_action_code("A1", available_actions)

    assert result == ActionCode.OFFER_TRUCO
    # Verify warnings were logged
    mock_logger.warning.assert_any_call("Action code %s is not available right now.", 4)
    mock_logger.warning.assert_any_call("Invalid input. Please enter a valid integer action code.")
