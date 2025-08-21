from __future__ import annotations

from typing import TYPE_CHECKING

from schemas.actions import ActionCode
from schemas.constants import SUIT_TO_INDEX
from schemas.observation import encode_state_key
from schemas.round_state import TRUCO_STATE_TO_INDEX

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent, Observation
    from models.player import Player
    from models.round import Round
    from schemas.player_state import PlayerState


class RoundActionProvider:
    """Callable adapter implementing the `ActionProvider` protocol."""

    def __init__(self, agent: BaseAgent, opponent: BaseAgent, learner_name: str = "Agent") -> None:
        self._agent: BaseAgent = agent
        self._opponent: BaseAgent = opponent
        self._learner_name = learner_name
        self._round: Round | None = None
        self.trajectory: list[tuple[str, int, float]] = []

    def set_round(self, round_obj: Round) -> None:
        """Attach the live `Round` for richer observations (training only)."""
        self._round = round_obj

    def reset_trajectory(self) -> None:
        """Clear any stored trajectory from a prior episode."""
        self.trajectory = []

    # --- Internals --------------------------------------------------------------
    def _available_int_codes(self, actions: list[ActionCode]) -> list[int]:
        return [int(a) for a in actions]

    def _build_observation(self, player_state: PlayerState) -> Observation:
        numbers = [-1, -1, -1]
        suits = [-1, -1, -1]
        suit_to_int = SUIT_TO_INDEX
        truco_to_int = TRUCO_STATE_TO_INDEX

        for idx, card in enumerate(player_state.player_cards):
            numbers[idx] = int(card.number)
            suits[idx] = suit_to_int[card.suit]

        if self._round is None:
            return {
                "hand_numbers": numbers,
                "hand_suits": suits,
                "truco_state": 0,
                "muestra_number": 0,
                "muestra_suit": 0,
            }

        return {
            "hand_numbers": numbers,
            "hand_suits": suits,
            "truco_state": truco_to_int[self._round.round_state.truco_state],
            "muestra_number": int(self._round.muestra.number),
            "muestra_suit": suit_to_int[self._round.muestra.suit],
        }

    # --- Callable ---------------------------------------------------------------
    def __call__(
        self, player: Player, player_state: PlayerState, available: list[ActionCode]
    ) -> ActionCode:
        obs = self._build_observation(player_state)
        valid = self._available_int_codes(available)
        if player.name == self._learner_name:
            action = self._agent.select_action(obs, valid)
            self.trajectory.append((encode_state_key(obs), action, 0.0))
            return ActionCode(action)
        opp_action = self._opponent.select_action(obs, valid)
        return ActionCode(opp_action)
