from __future__ import annotations

from collections import defaultdict

from agents.base_agent import BaseAgent
from logging_config import get_logger

logger = get_logger(__name__)


class MonteCarloAgent(BaseAgent):
    """Tabular first-visit Monte Carlo agent with epsilon-soft policy."""

    OUTPUT_SUBDIR = "mc"

    def __init__(
        self,
        *,
        epsilon_start: float = 0.2,
        epsilon_min: float = 0.05,
        epsilon_decay: float = 1e-4,
        seed: int | None = None,
    ) -> None:
        super().__init__(
            epsilon_start=epsilon_start,
            epsilon_min=epsilon_min,
            epsilon_decay=epsilon_decay,
            seed=seed,
        )
        self.returns_sum_map: dict[tuple[str, int], float] = defaultdict(float)
        self.returns_count_map: dict[tuple[str, int], int] = defaultdict(int)

    def update(self, episode_trajectory: list[tuple[str, int, float]]) -> None:
        # First-visit MC: update only on first occurrence of (s,a)
        g_return = 0.0
        visited: set[tuple[str, int]] = set()
        for t in range(len(episode_trajectory) - 1, -1, -1):
            s, a, r = episode_trajectory[t]
            g_return += r  # gamma=1
            key = (s, a)
            if key in visited:
                continue
            visited.add(key)
            self.returns_sum_map[key] += g_return
            self.returns_count_map[key] += 1
            self.q_values[key] = self.returns_sum_map[key] / float(self.returns_count_map[key])
        self.episodes_seen += 1

    def reset(self) -> None:
        return None

    # Inherit pickle-based save/load from BaseAgent
