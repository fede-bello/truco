from pydantic import BaseModel, ConfigDict

from models.card import Card
from schemas.round_state import RoundState


class PlayerState(BaseModel):
    """Represents the current state of a player in the game.

    This schema encapsulates all the information a player needs to know
    about the current game state, including their cards and the round state.

    Attributes:
        round_state: The current state of the round.
        player_cards: The cards currently in the player's hand.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    round_state: RoundState
    player_cards: list[Card]
