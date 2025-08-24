from __future__ import annotations

import argparse
import random
import statistics
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from agents.monte_carlo_agent import MonteCarloAgent
from agents.provider import RoundActionProvider
from agents.q_learning_agent import QLearningAgent
from agents.random_agent import RandomAgent
from logging_config import get_logger
from models.player import Player
from models.round import Round
from utils.config_loader import load_agent_config

if TYPE_CHECKING:
    from schemas.train_config import EpsilonParams, QParams, TrainingConfig

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent

logger = get_logger(__name__)


def _play_one_episode(
    agent: BaseAgent, opponent: BaseAgent
) -> tuple[list[tuple[str, int, float]], float]:
    """Simulate a single round episode and return trajectory and reward.

    Args:
        agent: Learning agent instance.
        opponent: Opponent agent instance.

    Returns:
        A tuple of (trajectory, reward), where trajectory is a list of
        (state_key, action, reward) and reward is the terminal reward.
    """
    player_1 = Player("Agent")
    player_2 = Player("Opponent")
    provider = RoundActionProvider(agent, opponent, learner_name=player_1.name)
    round_obj = Round(player_1, player_2, provider, starting_player=player_1)
    provider.set_round(round_obj)
    provider.reset_trajectory()
    t1_pts, t2_pts = round_obj.play_round()

    reward = t1_pts - t2_pts

    if provider.trajectory:
        s, a, _ = provider.trajectory[-1]
        provider.trajectory[-1] = (s, a, reward)

    return provider.trajectory, reward


def train(config: TrainingConfig) -> None:
    """Train an agent and store artifacts in a session directory.

    Args:
        config: Training configuration loaded from YAML.
    """
    _ = random.Random(config.seed)  # seeding for reproducibility where used
    agent_type = config.agent_type
    q_params: QParams = config.q_params or {}  # type: ignore[assignment]
    epsilon_params: EpsilonParams = config.epsilon_params or {}  # type: ignore[assignment]

    if agent_type == "mc_first_visit":
        agent = MonteCarloAgent(
            epsilon_start=epsilon_params.epsilon_start,
            epsilon_min=epsilon_params.epsilon_min,
            epsilon_decay=epsilon_params.epsilon_decay,
            seed=config.seed,
        )
    elif agent_type == "q_learning":
        agent = QLearningAgent(
            alpha=q_params.alpha,
            gamma=q_params.gamma,
            epsilon_params={
                "epsilon_start": epsilon_params.epsilon_start,
                "epsilon_min": epsilon_params.epsilon_min,
                "epsilon_decay": epsilon_params.epsilon_decay,
            },
            seed=config.seed,
        )
    else:
        msg = "Unsupported agent_type. Use 'mc_first_visit' or 'q_learning'."
        raise ValueError(msg)
    opponent = RandomAgent(seed=config.seed + 1)

    rewards: list[float] = []
    round_wins: list[int] = []

    # Create per-class session directory (src/output/<mc|ql>/<timestamp>)
    agent_cls = MonteCarloAgent if agent_type == "mc_first_visit" else QLearningAgent
    session_dir = agent_cls.create_session_dir()
    agent_path = session_dir / str(config.out)

    with Path(session_dir / "config.yaml").open("w") as f:
        yaml.dump(config, f)

    for episode in range(1, config.episodes + 1):
        trajectory, reward = _play_one_episode(agent, opponent)
        rewards.append(reward)
        round_wins.append(1 if reward > 0 else 0)
        agent.update(trajectory)
        rolling_window_size = 2000
        if episode % rolling_window_size == 0:
            mean_reward = float(statistics.mean(rewards[-rolling_window_size:]))
            win_rate = sum(round_wins[-rolling_window_size:]) / max(
                1, len(round_wins[-rolling_window_size:])
            )
            rewards_file = session_dir / "rewards.txt"
            if episode == rolling_window_size:
                rewards_file.write_text("", encoding="utf-8")
            with rewards_file.open("a", encoding="utf-8") as f:
                f.write(f"{episode} {mean_reward} {win_rate}\n")
            logger.info(
                "Ep %s | meanR=%.3f | winR=%.2f",
                episode,
                mean_reward,
                win_rate,
            )

    agent.save(str(agent_path))
    logger.info("Saved %s agent to %s", agent_type, str(agent_path))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True, help="Path to YAML config file")
    args = parser.parse_args()
    config = load_agent_config(args.config)
    train(config)


if __name__ == "__main__":
    main()
