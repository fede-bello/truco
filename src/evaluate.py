from __future__ import annotations

import argparse
import statistics
from pathlib import Path

from agents.monte_carlo_agent import MonteCarloAgent
from agents.provider import RoundActionProvider
from agents.random_agent import RandomAgent
from logging_config import get_logger
from models.game import Game
from models.player import Player
from utils.paths import get_latest_session_dir

logger = get_logger(__name__)


def evaluate(
    agent_path: str,
    matches: int,
    target_points: int,
    seed: int,
    output_dir: str | None = None,
) -> None:
    """Evaluate a saved agent and write metrics into the session directory.

    Args:
        agent_path: Path to the agent file, or a filename inside the output directory.
        matches: Number of matches to simulate.
        target_points: Points needed to win a match.
        seed: Random seed for the opponent agent.
        output_dir: Directory to write evaluation results; defaults to the latest
            timestamped session directory if not provided.
    """
    session_dir = Path(output_dir) if output_dir else get_latest_session_dir()
    if session_dir is None:
        msg = "No output session directory found."
        raise FileNotFoundError(msg)

    candidate = Path(agent_path)
    resolved_agent_path = candidate if candidate.exists() else (session_dir / candidate)
    agent = MonteCarloAgent.load(str(resolved_agent_path))
    opponent = RandomAgent(seed=seed + 1)

    match_wins = 0
    total_points: list[tuple[int, int]] = []

    for _ in range(matches):
        agent_player = Player("Agent")
        opponent_player = Player("Opponent")
        provider = RoundActionProvider(agent, opponent, learner_name=agent_player.name)
        game = Game(agent_player, opponent_player, provider)
        winner_team = game.play_game(target_points)
        if winner_team == 1:
            match_wins += 1
        total_points.append((game.team1_score, game.team2_score))
        # Round wins approximated by which team scored per round; not stored directly
        # so we only track match wins here.

    win_rate = match_wins / max(1, matches)
    t1_vals = [p1 for (p1, _) in total_points]
    t2_vals = [p2 for (_, p2) in total_points]
    avg_t1 = float(statistics.mean(t1_vals))
    avg_t2 = float(statistics.mean(t2_vals))
    logger.info("Match win-rate: %.2f", win_rate)
    logger.info("Avg points per match — Team1: %.2f, Team2: %.2f", avg_t1, avg_t2)

    # Write evaluation summary
    eval_file = session_dir / "evaluation.txt"
    with eval_file.open("w", encoding="utf-8") as f:
        f.write(f"win_rate {win_rate:.4f}\n")
        f.write(f"avg_points_team1 {avg_t1:.4f}\n")
        f.write(f"avg_points_team2 {avg_t2:.4f}\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", type=str, default="mc_agent.pkl")
    parser.add_argument("--matches", type=int, default=200)
    parser.add_argument("--target", type=int, default=40)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--outdir", type=str, default="")
    args = parser.parse_args()

    outdir = args.outdir or None
    evaluate(args.agent, args.matches, args.target, args.seed, outdir)


if __name__ == "__main__":
    main()
