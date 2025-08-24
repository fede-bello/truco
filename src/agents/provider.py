from __future__ import annotations

from typing import TYPE_CHECKING

from schemas.actions import ActionCode
from schemas.constants import SUIT_TO_INDEX
from schemas.observation import encode_state_key
from schemas.round_state import TRUCO_STATE_TO_INDEX

if TYPE_CHECKING:
    from collections.abc import Callable

    from agents.base_agent import BaseAgent, Observation
    from models.player import Player
    from models.round import Round
    from schemas.player_state import PlayerState


def _available_int_codes(actions: list[ActionCode]) -> list[int]:
    return [int(a) for a in actions]


def _build_observation_for_round(round_obj: Round | None, player_state: PlayerState) -> Observation:
    numbers = [-1, -1, -1]
    suits = [-1, -1, -1]
    suit_to_int = SUIT_TO_INDEX
    truco_to_int = TRUCO_STATE_TO_INDEX

    for idx, card in enumerate(player_state.player_cards):
        numbers[idx] = int(card.number)
        suits[idx] = suit_to_int[card.suit]

    if round_obj is None:
        truco_state = 0
        muestra_number = 0
        muestra_suit = 0
    else:
        truco_state = truco_to_int[round_obj.round_state.truco_state]
        muestra_number = int(round_obj.muestra.number)
        muestra_suit = suit_to_int[round_obj.muestra.suit]

    return {
        "hand_numbers": numbers,
        "hand_suits": suits,
        "truco_state": truco_state,
        "muestra_number": muestra_number,
        "muestra_suit": muestra_suit,
    }


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

    def __call__(
        self, player: Player, player_state: PlayerState, available: list[ActionCode]
    ) -> ActionCode:
        obs = _build_observation_for_round(self._round, player_state)
        valid = _available_int_codes(available)
        if player.name == self._learner_name:
            action = self._agent.select_action(obs, valid)
            self.trajectory.append((encode_state_key(obs), action, 0.0))
            return ActionCode(action)
        opp_action = self._opponent.select_action(obs, valid)
        return ActionCode(opp_action)


class HumanVsAgentProvider:
    """Action provider that pairs a human CLI with an agent opponent.

    The human is assumed to be `human_player_name`. When the human is to act,
    this provider calls a supplied CLI callback to obtain the action from the
    user. The agent acts automatically using its policy.
    """

    def __init__(
        self,
        agent: BaseAgent,
        human_player_name: str,
        cli_callback: Callable[[Player, PlayerState, list[ActionCode]], ActionCode],
    ) -> None:
        self._agent = agent
        self._human_name = human_player_name
        self._cli: Callable[[Player, PlayerState, list[ActionCode]], ActionCode] = cli_callback
        self._round: Round | None = None

    def set_round(self, round_obj: Round) -> None:
        self._round = round_obj

    # --- Internals --------------------------------------------------------------

    def __call__(
        self, player: Player, player_state: PlayerState, available: list[ActionCode]
    ) -> ActionCode:
        if player.name == self._human_name:
            return self._cli(player, player_state, available)

        obs = _build_observation_for_round(self._round, player_state)
        valid = _available_int_codes(available)
        action = self._agent.select_action(obs, valid)
        return ActionCode(action)
