from __future__ import annotations

import json
import math
import random
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from agents.base_agent import BaseAgent
from logging_config import get_logger
from schemas.observation import Observation, encode_state_key

if TYPE_CHECKING:
    from collections.abc import Sequence


logger = get_logger(__name__)


class MonteCarloAgent(BaseAgent):
    """Tabular first-visit Monte Carlo agent with epsilon-soft policy."""

    def __init__(
        self,
        *,
        epsilon_start: float = 0.2,
        epsilon_min: float = 0.05,
        epsilon_decay: float = 1e-4,
        seed: int | None = None,
    ) -> None:
        if not (0.0 <= epsilon_min <= epsilon_start <= 1.0):
            msg = "epsilon bounds invalid"
            logger.error(msg)
            raise ValueError(msg)
        if epsilon_decay < 0:
            msg = "epsilon_decay must be >= 0"
            logger.error(msg)
            raise ValueError(msg)
        self.epsilon_start = epsilon_start
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.episodes_seen = 0

        self._rng = random.Random(seed)
        self.q_values: dict[tuple[str, int], float] = defaultdict(float)
        self.returns_sum_map: dict[tuple[str, int], float] = defaultdict(float)
        self.returns_count_map: dict[tuple[str, int], int] = defaultdict(int)

    def _epsilon(self) -> float:
        if self.epsilon_decay == 0:
            return self.epsilon_start
        val = self.epsilon_start * math.exp(-self.epsilon_decay * self.episodes_seen)
        return max(self.epsilon_min, val)

    def _greedy_action(self, state_key: str, valid_actions: Sequence[int]) -> int:
        best_a = None
        best_q = -1e9
        for a in valid_actions:
            q = self.q_values[(state_key, int(a))]
            if q > best_q:
                best_q = q
                best_a = int(a)
        if best_a is None:
            msg = "best_a is None"
            logger.error(msg)
            raise ValueError(msg)
        return best_a

    def select_action(self, observation: Observation, valid_actions: Sequence[int]) -> int:
        if not valid_actions:
            msg = "valid_actions is empty"
            logger.error(msg)
            raise ValueError(msg)
        state_key = encode_state_key(observation)
        eps = self._epsilon()
        if self._rng.random() < eps:
            return int(self._rng.choice(list(valid_actions)))
        return self._greedy_action(state_key, valid_actions)

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

    def save(self, path: str) -> None:
        """Persist agent state to a JSON file (avoids unsafe pickle).

        Args:
            path: Destination file path.
        """
        q_values_list = [[s, int(a), float(v)] for (s, a), v in self.q_values.items()]
        returns_sum_list = [[s, int(a), float(v)] for (s, a), v in self.returns_sum_map.items()]
        returns_count_list = [[s, int(a), int(v)] for (s, a), v in self.returns_count_map.items()]

        data: dict[str, Any] = {
            "q_values_list": q_values_list,
            "returns_sum_list": returns_sum_list,
            "returns_count_list": returns_count_list,
            "episodes_seen": int(self.episodes_seen),
            "epsilon_start": float(self.epsilon_start),
            "epsilon_min": float(self.epsilon_min),
            "epsilon_decay": float(self.epsilon_decay),
        }
        with Path(path).open("w", encoding="utf-8") as file_obj:
            json.dump(data, file_obj)

    @classmethod
    def load(cls, path: str) -> MonteCarloAgent:
        """Load agent state from a JSON file saved by save().

        Args:
            path: Source file path.

        Returns:
            A reconstructed MonteCarloAgent instance.
        """
        with Path(path).open("r", encoding="utf-8") as file_obj:
            raw: Any = json.load(file_obj)
        data = cast("dict[str, Any]", raw)
        agent = cls(
            epsilon_start=float(data["epsilon_start"]),
            epsilon_min=float(data["epsilon_min"]),
            epsilon_decay=float(data["epsilon_decay"]),
        )
        q_values_list = cast("list[list[Any]]", data.get("q_values_list", []))
        returns_sum_list = cast("list[list[Any]]", data.get("returns_sum_list", []))
        returns_count_list = cast("list[list[Any]]", data.get("returns_count_list", []))

        agent.q_values = defaultdict(
            float, {(str(s), int(a)): float(v) for s, a, v in q_values_list}
        )
        agent.returns_sum_map = defaultdict(
            float, {(str(s), int(a)): float(v) for s, a, v in returns_sum_list}
        )
        agent.returns_count_map = defaultdict(
            int, {(str(s), int(a)): int(v) for s, a, v in returns_count_list}
        )
        agent.episodes_seen = int(data["episodes_seen"])
        return agent
