from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict

from models.card import Card
from models.player import Player

TRUCO_STATE = Literal["nada", "truco", "retruco", "vale4"]
ENVIDO_STATE = Literal["nada", "envido", "querido", "no_quiero"]

TRUCO_STATE_TO_INDEX: dict[str, int] = {"nada": 0, "truco": 1, "retruco": 2, "vale4": 3}


class RoundState(BaseModel):
    """Represents the current state of a round in the game.

    Attributes:
        truco_state: The current truco bidding state.
        cards_played_this_round: Dictionary mapping player names to cards they've played.
        flor_calls: List of players who called Flor.
        player_initial_hands: Dictionary mapping players to their original 3-card hand.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    truco_state: TRUCO_STATE
    envido_state: ENVIDO_STATE = "nada"
    cards_played_this_round: dict[Player, Card]
    flor_calls: list[Player] = []
    player_initial_hands: dict[Player, list[Card]] = {}
    envido_bidder: Player | None = None
    envido_points: dict[int, int] = {1: 0, 2: 0}  # Team points from Envido


@dataclass
class RoundProgress:
    """Mutable state tracking the progress of a round's tricks.

    Attributes:
        current_starter: Player who leads the next trick.
        team_1_wins: Number of tricks won by team 1 so far.
        team_2_wins: Number of tricks won by team 2 so far.
        first_trick_tied: Whether the first trick resulted in a tie.
        first_trick_winner: Winner of the first trick, if not tied.
    """

    current_starter: Player
    team_1_wins: int
    team_2_wins: int
    first_trick_tied: bool
    first_trick_winner: Player | None
