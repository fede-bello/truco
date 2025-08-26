from __future__ import annotations

import math
import pickle
import random
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from random import Random
from typing import TYPE_CHECKING, Self

from schemas.constants import BASE_OUTPUT_DIR
from schemas.observation import encode_state_key

if TYPE_CHECKING:
    from collections.abc import Sequence

    from schemas.observation import Observation


class BaseAgent:
    """Concrete base class for tabular agents with epsilon-greedy policy.

    Provides RNG, Q-table storage, epsilon scheduling, and default
    `select_action` implemented via epsilon-greedy over valid actions.
    Subclasses should implement `update()` and may override `reset()`.
    """

    OUTPUT_SUBDIR = ""

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
            raise ValueError(msg)
        if epsilon_decay < 0:
            msg = "epsilon_decay must be >= 0"
            raise ValueError(msg)
        self.epsilon_start = epsilon_start
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.episodes_seen = 0

        self._rng: Random = random.Random(seed)
        self.q_values: dict[tuple[str, int], float] = defaultdict(float)

    # --- Policy helpers ---------------------------------------------------------
    def epsilon(self) -> float:
        """Compute exponentially decayed epsilon for epsilon-greedy."""
        val = self.epsilon_start * math.exp(-self.epsilon_decay * float(self.episodes_seen))
        return max(self.epsilon_min, val)

    def _greedy_action(self, state_key: str, valid_actions: Sequence[int]) -> int:
        """Choose action with highest Q among valid actions for a state.

        Args:
            state_key: Encoded state key string.
            valid_actions: Iterable of valid integer action codes.

        Returns:
            The greedy action code.

        Raises:
            ValueError: If no valid actions are available.
        """
        if not valid_actions:
            msg = "valid_actions is empty"
            raise ValueError(msg)
        best_a: int | None = None
        best_q = -1e18
        for a in valid_actions:
            q = self.q_values.get((state_key, int(a)), 0.0)
            if q > best_q:
                best_q = q
                best_a = int(a)
        if best_a is None:
            msg = "Failed to choose a greedy action"
            raise ValueError(msg)
        return best_a

    def _epsilon_greedy_action(self, state_key: str, valid_actions: Sequence[int]) -> int:
        """Select an action using epsilon-greedy over valid actions.

        Args:
            state_key: Encoded state key string.
            valid_actions: Iterable of valid integer action codes.

        Returns:
            The selected action code.
        """
        if not valid_actions:
            msg = "valid_actions is empty"
            raise ValueError(msg)
        if self._rng.random() < self.epsilon():
            return int(self._rng.choice(list(valid_actions)))
        return self._greedy_action(state_key, valid_actions)

    # --- API methods ------------------------------------------------------------
    def select_action(self, observation: Observation, valid_actions: Sequence[int]) -> int:
        """Choose an action index from the provided valid actions.

        Args:
            observation: Agent observation dict.
            valid_actions: A sequence of integer action codes that are valid now.

        Returns:
            The chosen action code as an integer.
        """
        state_key = encode_state_key(observation)
        return self._epsilon_greedy_action(state_key, valid_actions)

    def update(self, episode_trajectory: list[tuple[str, int, float]]) -> None:
        """Update agent from an episode trajectory.

        Subclasses must implement this to perform learning.
        """
        raise NotImplementedError

    def reset(self) -> None:
        """Optional per-episode reset hook."""
        return None

    # --- Persistence -----------------------------------------------------------
    def save(self, path: str) -> None:
        """Serialize the agent to a pickle file.

        Args:
            path: Destination file path. Parent directories are created.
        """
        dst = Path(path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        with dst.open("wb") as f:
            pickle.dump(self, f)  # type: ignore[reportUnknownReturnType]

    @classmethod
    def load(cls, path: str) -> Self:
        """Load an agent from a pickle file created by save().

        Args:
            path: Source file path.

        Returns:
            An instance of the invoking subclass.
        """
        src = Path(path)
        with src.open("rb") as f:
            obj = pickle.load(f)  # type: ignore[reportUnknownReturnType]
        if not isinstance(obj, cls):
            msg = f"Loaded object is not an instance of {cls.__name__}"
            raise TypeError(msg)
        return obj

    @classmethod
    def create_session_dir(cls, now: datetime | None = None) -> Path:
        """Create a new timestamped session directory under the class subdir.

        Path format: BASE_OUTPUT_DIR/<OUTPUT_SUBDIR>/<YYYYmmdd-HHMMSS>
        """
        base = BASE_OUTPUT_DIR
        if cls.OUTPUT_SUBDIR:
            base = base / cls.OUTPUT_SUBDIR
        base.mkdir(parents=True, exist_ok=True)
        ts = (now or datetime.now(UTC)).strftime("%Y%m%d-%H%M%S")
        session_dir = base / ts
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir

    @classmethod
    def latest_session_dir(cls) -> Path | None:
        """Return latest session dir under the class subdir, if any."""
        base = BASE_OUTPUT_DIR / cls.OUTPUT_SUBDIR if cls.OUTPUT_SUBDIR else BASE_OUTPUT_DIR
        if not base.exists():
            return None
        subdirs = [p for p in base.iterdir() if p.is_dir()]
        if not subdirs:
            return None
        subdirs.sort(key=lambda p: p.name)
        return subdirs[-1]
