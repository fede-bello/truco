"""Uniform random baseline agent that respects valid action masks."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from agents.base_agent import BaseAgent
from logging_config import get_logger

if TYPE_CHECKING:
    from collections.abc import Sequence

    from agents.base_agent import Observation

logger = get_logger(__name__)


class RandomAgent(BaseAgent):
    """Agent that selects uniformly among valid actions."""

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def select_action(self, observation: Observation, valid_actions: Sequence[int]) -> int:
        if not valid_actions:
            msg = "valid_actions is empty"
            logger.error(msg)
            raise ValueError(msg)
        _ = observation
        return int(self._rng.choice(list(valid_actions)))

    def update(self, episode_trajectory: list[tuple[str, int, float]]) -> None:
        super().update(episode_trajectory)

    def reset(self) -> None:
        super().reset()
