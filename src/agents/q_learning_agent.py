"""QLearningAgent: tabular Q-learning implementation for Truco."""

from __future__ import annotations

from agents.base_agent import BaseAgent
from logging_config import get_logger

logger = get_logger(__name__)


class QLearningAgent(BaseAgent):
    """Tabular Q-learning agent with epsilon-greedy exploration.

    Q-values are stored in a dictionary keyed by (state_key, action).
    """

    OUTPUT_SUBDIR = "ql"

    def __init__(
        self,
        *,
        alpha: float = 0.1,
        gamma: float = 0.99,
        epsilon_params: dict[str, float] | None = None,
        seed: int | None = None,
    ) -> None:
        if not (0.0 < alpha <= 1.0):
            msg = "alpha must be in (0, 1]"
            logger.error(msg)
            raise ValueError(msg)
        if not (0.0 <= gamma <= 1.0):
            msg = "gamma must be in [0, 1]"
            logger.error(msg)
            raise ValueError(msg)
        eps_start = (
            1.0 if epsilon_params is None else float(epsilon_params.get("epsilon_start", 1.0))
        )
        eps_min = 0.05 if epsilon_params is None else float(epsilon_params.get("epsilon_min", 0.05))
        eps_decay = (
            1e-4 if epsilon_params is None else float(epsilon_params.get("epsilon_decay", 1e-4))
        )
        if not (0.0 <= eps_min <= eps_start <= 1.0):
            msg = "epsilon bounds invalid"
            logger.error(msg)
            raise ValueError(msg)
        if eps_decay < 0:
            msg = "epsilon_decay must be >= 0"
            logger.error(msg)
            raise ValueError(msg)

        self.alpha = alpha
        self.gamma = gamma
        super().__init__(
            epsilon_start=eps_start,
            epsilon_min=eps_min,
            epsilon_decay=eps_decay,
            seed=seed,
        )

    def update(self, episode_trajectory: list[tuple[str, int, float]]) -> None:
        """Apply Q-learning TD updates from the per-episode trajectory.

        The trajectory is a list of (state_key, action, reward) tuples, with the
        terminal reward recorded on the final step and zeros elsewhere.
        Next-state keys are inferred from the subsequent element when present.
        """
        n = len(episode_trajectory)
        if n == 0:
            self.episodes_seen += 1
            return

        for t in range(n):
            s_key, action, reward = episode_trajectory[t]
            is_terminal = t == n - 1

            if is_terminal:
                target = reward
            else:
                next_s_key = episode_trajectory[t + 1][0]
                # Max over all discrete actions (0..5) since valid actions are not stored.
                # Unseen (s', a') pairs default to 0.0 via dict.get.
                max_q_next = max(self.q_values.get((next_s_key, a), 0.0) for a in range(6))
                target = reward + self.gamma * max_q_next

            current_q = self.q_values.get((s_key, int(action)), 0.0)
            updated_q = current_q + self.alpha * (target - current_q)
            self.q_values[(s_key, int(action))] = updated_q

        self.episodes_seen += 1

    def reset(self) -> None:
        return None
