from __future__ import annotations

import argparse
import random
import statistics

from agents.monte_carlo_agent import MonteCarloAgent
from agents.provider import RoundActionProvider
from agents.random_agent import RandomAgent
from logging_config import get_logger
from models.player import Player
from models.round import Round
from utils.paths import create_new_session_dir

logger = get_logger(__name__)


def train(num_episodes: int, seed: int, save_path: str) -> None:
    """Train a Monte Carlo agent and store artifacts in a session directory.

    Args:
        num_episodes: Number of training episodes.
        seed: Random seed for reproducibility.
        save_path: Filename for the saved agent within the session directory.
    """
    _ = random.Random(seed)
    agent = MonteCarloAgent(seed=seed)
    opponent = RandomAgent(seed=seed + 1)

    rewards: list[float] = []
    round_wins: list[int] = []

    session_dir = create_new_session_dir()

    for episode in range(1, num_episodes + 1):
        player_1 = Player("Agent")
        player_2 = Player("Opponent")
        provider = RoundActionProvider(agent, opponent, learner_name=player_1.name)
        round_obj = Round(player_1, player_2, provider, starting_player=player_1)
        provider.set_round(round_obj)
        provider.reset_trajectory()
        t1_pts, t2_pts = round_obj.play_round()

        # Set terminal reward for all steps in this episode (gamma = 1)
        reward = 0.0
        if t1_pts > t2_pts:
            reward = 1.0
            round_wins.append(1)
        elif t2_pts > t1_pts:
            reward = -1.0
            round_wins.append(0)
        else:
            reward = 0.0
            round_wins.append(0)

        rewards.append(reward)

        # Replace the last reward in the trajectory with terminal reward, others stay 0
        if provider.trajectory:
            s, a, _ = provider.trajectory[-1]
            provider.trajectory[-1] = (s, a, reward)

        agent.update(provider.trajectory)
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

    agent_path = session_dir / save_path
    agent.save(str(agent_path))
    logger.info("Saved agent to %s", str(agent_path))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=str, default="mc_agent.pkl")
    args = parser.parse_args()

    train(args.episodes, args.seed, args.out)


if __name__ == "__main__":
    main()
