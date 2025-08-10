from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict

from models.card import Card
from models.player import Player

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


@dataclass
class RoundProgress:
    """Mutable state tracking the progress of a round's tricks.

    Attributes:
        current_starter: Player who leads the next trick.
        player_1_wins: Number of tricks won by player 1 so far.
        player_2_wins: Number of tricks won by player 2 so far.
        first_trick_tied: Whether the first trick resulted in a tie.
        first_trick_winner: Winner of the first trick, if not tied.
    """

    current_starter: Player
    player_1_wins: int
    player_2_wins: int
    first_trick_tied: bool
    first_trick_winner: Player | None
