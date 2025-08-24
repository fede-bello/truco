from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING

from agents.monte_carlo_agent import MonteCarloAgent
from agents.provider import HumanVsAgentProvider
from agents.q_learning_agent import QLearningAgent
from logging_config import get_logger
from models.game import Game
from models.player import Player
from utils.cli_actions import print_available_actions, prompt_action_code
from utils.config_loader import get_evaluation_params, load_agent_config

if TYPE_CHECKING:
    from schemas.actions import ActionCode, ActionProvider
    from schemas.player_state import PlayerState

logger = get_logger(__name__)


def _print_available_actions(
    player_name: str, player_state: PlayerState, actions: list[ActionCode]
) -> None:
    print_available_actions(player_name, player_state.player_cards, actions)


def _cli_action_provider(
    player: Player, player_state: PlayerState, available_actions: list[ActionCode]
) -> ActionCode:
    _print_available_actions(player.name, player_state, available_actions)
    return prompt_action_code(player.name, available_actions)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True, help="Path to YAML config file")
    args = parser.parse_args()
    config = load_agent_config(args.config)
    eval_cfg = get_evaluation_params(config)

    # Determine session directory and agent artifact path
    if eval_cfg.output_dir:
        session_dir = Path(eval_cfg.output_dir)
    elif config.agent_type == "mc_first_visit":
        session_dir = MonteCarloAgent.latest_session_dir()
    else:
        session_dir = QLearningAgent.latest_session_dir()
    if session_dir is None:
        msg = "No output session directory found."
        raise FileNotFoundError(msg)
    agent_path = session_dir / str(config.out)

    # Load agent
    if config.agent_type == "mc_first_visit":
        agent = MonteCarloAgent.load(str(agent_path))
    else:
        agent = QLearningAgent.load(str(agent_path))

    human = Player("Human")
    bot = Player("Agent")

    provider = HumanVsAgentProvider(
        agent, human_player_name=human.name, cli_callback=_cli_action_provider
    )
    action_provider: ActionProvider = provider
    game = Game(human, bot, action_provider)
    winner_team = game.play_game(eval_cfg.target_points)

    logger.info("Final Team 1 score: %s", game.team1_score)
    logger.info("Final Team 2 score: %s", game.team2_score)
    logger.info("Winner: Team %s", winner_team)


if __name__ == "__main__":
    main()
