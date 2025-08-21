from __future__ import annotations

from typing import TypedDict


class Observation(TypedDict):
    """Minimal observation schema used by agents.

    Keys mirror those produced by the environment and training loop wrappers.
    """

    hand_numbers: list[int]
    hand_suits: list[int]
    truco_state: int
    muestra_number: int
    muestra_suit: int


def encode_state_key(observation: Observation) -> str:
    """Create a deterministic state key from an observation.

    Args:
        observation: Observation dict following the `Observation` schema.

    Returns:
        A stable string key representing the observation contents.
    """
    hn = tuple(int(x) for x in observation.get("hand_numbers", []))
    hs = tuple(int(x) for x in observation.get("hand_suits", []))
    ts = int(observation.get("truco_state", 0))
    mn = int(observation.get("muestra_number", 0))
    ms = int(observation.get("muestra_suit", 0))
    return f"hn={hn}|hs={hs}|ts={ts}|mn={mn}|ms={ms}"
