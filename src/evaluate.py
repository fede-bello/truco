from __future__ import annotations

import argparse
import statistics
from pathlib import Path
from typing import TYPE_CHECKING

from agents.monte_carlo_agent import MonteCarloAgent
from agents.provider import RoundActionProvider
from agents.q_learning_agent import QLearningAgent
from agents.random_agent import RandomAgent
from logging_config import get_logger
from models.game import Game
from models.player import Player
from utils.config_loader import get_evaluation_params, load_agent_config

if TYPE_CHECKING:
    from schemas.train_config import TrainingConfig

logger = get_logger(__name__)


def evaluate(config: TrainingConfig) -> None:
    evaluation_config = get_evaluation_params(config)

    if evaluation_config.output_dir:
        session_dir = Path(evaluation_config.output_dir)
    elif config.agent_type == "mc_first_visit":
        session_dir = MonteCarloAgent.latest_session_dir()
    else:
        session_dir = QLearningAgent.latest_session_dir()
    if session_dir is None:
        msg = "No output session directory found."
        raise FileNotFoundError(msg)

    # Agent artifact within the session dir
    agent_path = session_dir / str(config.out)
    if config.agent_type == "mc_first_visit":
        agent = MonteCarloAgent.load(str(agent_path))
    else:
        agent = QLearningAgent.load(str(agent_path))
    opponent = RandomAgent(seed=evaluation_config.seed + 1)

    match_wins = 0
    total_points: list[tuple[int, int]] = []

    for _ in range(evaluation_config.matches):
        agent_player = Player("Agent")
        opponent_player = Player("Opponent")
        provider = RoundActionProvider(agent, opponent, learner_name=agent_player.name)
        game = Game(agent_player, opponent_player, provider)
        winner_team = game.play_game(evaluation_config.target_points)
        if winner_team == 1:
            match_wins += 1
        total_points.append((game.team1_score, game.team2_score))

    win_rate = match_wins / max(1, evaluation_config.matches)
    t1_vals = [p1 for (p1, _) in total_points]
    t2_vals = [p2 for (_, p2) in total_points]
    avg_t1 = float(statistics.mean(t1_vals))
    avg_t2 = float(statistics.mean(t2_vals))
    logger.info("Match win-rate: %.2f", win_rate)
    logger.info("Avg points per match — Team1: %.2f, Team2: %.2f", avg_t1, avg_t2)

    eval_file = session_dir / "evaluation.txt"
    with eval_file.open("w", encoding="utf-8") as f:
        f.write(f"win_rate {win_rate:.4f}\n")
        f.write(f"avg_points_team1 {avg_t1:.4f}\n")
        f.write(f"avg_points_team2 {avg_t2:.4f}\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True, help="Path to YAML config file")
    args = parser.parse_args()
    config = load_agent_config(args.config)
    evaluate(config)


if __name__ == "__main__":
    main()
