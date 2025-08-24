from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
from gymnasium import Env, spaces

from logging_config import get_logger
from models.player import Player
from models.round import Round
from schemas.actions import ActionCode, ActionProvider
from schemas.constants import SUIT_TO_INDEX
from schemas.observation import Observation
from schemas.round_state import TRUCO_STATE_TO_INDEX

if TYPE_CHECKING:
    from schemas.player_state import PlayerState


logger = get_logger(__name__)


class TrucoRoundEnv(Env[Observation, int]):
    """Round-level Gym environment for Truco.

    Episodes correspond to a single round. The learning side is always the
    first player (player_1). The opponent actions are provided by a callback
    implementing the same protocol as the training agents.

    Args:
        opponent_action_provider: Callback to produce actions for player_2.
            Signature compatible with `schemas.actions.ActionProvider`.
        seed: Optional RNG seed (delegated to agents where applicable).

    Attributes:
        action_space: Discrete(6), aligned with `ActionCode` values.
        observation_space: Minimal Dict space encoding hand and muestra.
    """

    def __init__(
        self,
        opponent_action_provider: ActionProvider,
        *,
        seed: int | None = None,
    ) -> None:
        self._seed = seed
        self._opponent_action_provider = opponent_action_provider

        self.action_space: spaces.Space[Any] = spaces.Discrete(6)
        self.observation_space: spaces.Space[Any] = spaces.Dict(
            {
                "hand_numbers": spaces.Box(low=-1, high=12, shape=(3,), dtype=np.int32),
                "hand_suits": spaces.Box(low=-1, high=3, shape=(3,), dtype=np.int32),
                "truco_state": spaces.Discrete(4),
                "muestra_number": spaces.Discrete(13),
                "muestra_suit": spaces.Discrete(4),
            }
        )

        self._round: Round | None = None
        self._player_1: Player | None = None
        self._player_2: Player | None = None

    def reset(
        self, *, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[Observation, dict[str, np.ndarray]]:
        """Start a fresh round and return the initial observation and info.

        Args:
            seed: Optional seed for reproducibility (stored only).
            options: Currently unused.

        Returns:
            A tuple of (observation, info). The info contains an `action_mask`
            with the valid opening actions for player_1.
        """
        super().reset(seed=seed, options=options)
        if seed is not None:
            self._seed = seed

        self._player_1 = Player("Agent")
        self._player_2 = Player("Opponent")

        # Placeholder provider. Real actions are provided in step via a
        # dedicated provider that will enforce the first action.
        def noop_provider(
            _player: Player, _player_state: PlayerState, _available_actions: list[ActionCode]
        ) -> ActionCode:
            # This provider should never be called before step() binds the real one.
            msg = "reset called without step; provide an action via step()."
            logger.error(msg)
            raise RuntimeError(msg)

        self._round = Round(
            self._player_1, self._player_2, noop_provider, starting_player=self._player_1
        )

        obs = self._build_observation(self._player_1)
        action_mask = np.asarray(self._get_action_mask(self._player_1), dtype=np.int32)
        return obs, {"action_mask": action_mask}

    def step(self, action: int) -> tuple[Observation, float, bool, bool, dict[str, np.ndarray]]:
        """Apply the provided opening action and complete the round.

        This executes the rest of the round using the opponent provider. It
        returns the terminal transition for the end of the round.

        Args:
            action: Integer action code from `ActionCode`.

        Returns:
            observation, reward, terminated, truncated, info
        """
        if self._round is None or self._player_1 is None or self._player_2 is None:
            msg = "Environment not reset. Call reset() first."
            logger.error(msg)
            raise RuntimeError(msg)

        opening_mask = self._get_action_mask(self._player_1)
        chosen = ActionCode(action)
        if opening_mask[action] == 0:
            msg = f"Invalid opening action {action} for current state"
            logger.error(msg)
            raise ValueError(msg)

        opening_action_used = {"used": False}

        def provider(
            player: Player, player_state: PlayerState, available: list[ActionCode]
        ) -> ActionCode:
            if player == self._player_1 and not opening_action_used["used"]:
                opening_action_used["used"] = True
                if chosen not in available:
                    msg = "Chosen opening action not in available list"
                    logger.error(msg)
                    raise ValueError(msg)
                return chosen
            if player == self._player_2:
                return self._opponent_action_provider(player, player_state, available)

            return available[0]

        self._round.set_action_provider(provider)

        team1_pts, team2_pts = self._round.play_round()

        reward = 0.0
        if team1_pts > team2_pts:
            reward = 1.0
        elif team2_pts > team1_pts:
            reward = -1.0

        obs = self._build_observation(self._player_1)
        info: dict[str, Any] = {"team1_points": team1_pts, "team2_points": team2_pts}
        terminated = True
        truncated = False
        return obs, reward, terminated, truncated, info

    def render(self, mode: str = "human") -> None:
        """No-op render hook; logging in Round provides visibility."""
        pass

    def close(self) -> None:
        """No-op close hook.

        This is required by the Gymnasium API.
        """
        pass

    def _build_observation(self, player: Player) -> Observation:
        if self._round is None:
            msg = "Environment not reset. Call reset() first."
            logger.error(msg)
            raise RuntimeError(msg)

        player_state = self._round.get_player_state(player)
        numbers = [-1, -1, -1]
        suits = [-1, -1, -1]
        for idx, card in enumerate(player_state.player_cards):
            numbers[idx] = int(card.number)
            suits[idx] = SUIT_TO_INDEX[card.suit]

        return {
            "hand_numbers": numbers,
            "hand_suits": suits,
            "truco_state": TRUCO_STATE_TO_INDEX[self._round.round_state.truco_state],
            "muestra_number": int(self._round.muestra.number),
            "muestra_suit": SUIT_TO_INDEX[self._round.muestra.suit],
        }

    def _get_action_mask(self, player: Player) -> list[int]:
        if self._round is None:
            msg = "Environment not reset. Call reset() first."
            logger.error(msg)
            raise RuntimeError(msg)

        available = self._round.get_available_actions(player)
        mask = [0] * 6
        for a in available:
            mask[int(a)] = 1
        return mask
