from typing import Literal

from models.card import Card
from models.player import Player
from pydantic import BaseModel, ConfigDict

TRUCO_STATE = Literal["nada", "truco", "retruco", "vale4"]


class RoundState(BaseModel):
    """Represents the current state of a round in the game.

    Attributes:
        truco_state: The current truco bidding state.
        cards_played_this_round: Dictionary mapping player names to cards they've played.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    truco_state: TRUCO_STATE
    cards_played_this_round: dict[Player, Card]
