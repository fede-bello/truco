from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Sequence

    from schemas.observation import Observation


class BaseAgent(Protocol):
    """Protocol for Truco agents.

    Methods follow a light-weight API suitable for tabular agents.
    """

    def select_action(self, observation: Observation, valid_actions: Sequence[int]) -> int:
        """Choose an action index from the provided valid actions.

        Args:
            observation: Agent observation dict.
            valid_actions: A sequence of integer action codes that are valid now.

        Returns:
            The chosen action code as an integer.
        """
        ...

    def update(self, episode_trajectory: list[tuple[str, int, float]]) -> None:
        """Update agent from an episode trajectory.

        Args:
            episode_trajectory: List of (state_key, action, reward) tuples for one episode.
        """

    def reset(self) -> None:
        """Optional per-episode reset hook."""
