"""Fixed integer action codes suitable for RL agents and UIs.

The mapping is stable and never changes:
- 0, 1, 2: Play card at index 0, 1, 2 respectively
- 3: Offer/advance Truco
- 4: Accept Truco
- 5: Reject Truco
- 6: Flor
- 7: Offer Envido
- 8: Accept Envido
- 9: Reject Envido
"""

from collections.abc import Callable
from enum import IntEnum

from models.player import Player
from schemas.player_state import PlayerState


class ActionCode(IntEnum):
    PLAY_CARD_0 = 0
    PLAY_CARD_1 = 1
    PLAY_CARD_2 = 2
    OFFER_TRUCO = 3
    ACCEPT_TRUCO = 4
    REJECT_TRUCO = 5
    FLOR = 6
    OFFER_ENVIDO = 7
    ACCEPT_ENVIDO = 8
    REJECT_ENVIDO = 9


def card_index_from_code(code: ActionCode) -> int | None:
    """Map a play-card action code to its hand index, else None."""
    play_map = {
        ActionCode.PLAY_CARD_0: 0,
        ActionCode.PLAY_CARD_1: 1,
        ActionCode.PLAY_CARD_2: 2,
    }
    return play_map.get(code)


ActionProvider = Callable[[Player, PlayerState, list[ActionCode]], ActionCode]
