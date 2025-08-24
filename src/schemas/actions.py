"""Fixed integer action codes suitable for RL agents and UIs.

The mapping is stable and never changes:
- 0, 1, 2: Play card at index 0, 1, 2 respectively
- 3: Offer/advance Truco
- 4: Accept Truco
- 5: Reject Truco
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


def card_index_from_code(code: ActionCode) -> int | None:
    if code == ActionCode.PLAY_CARD_0:
        return 0
    if code == ActionCode.PLAY_CARD_1:
        return 1
    if code == ActionCode.PLAY_CARD_2:
        return 2
    return None


ActionProvider = Callable[[Player, PlayerState, list[ActionCode]], ActionCode]
