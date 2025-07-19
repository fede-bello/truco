from typing import Literal

from pydantic import BaseModel

TRUCO_STATE = Literal["nada", "truco", "retruco", "vale4"]


class RoundState(BaseModel):
    truco_state: TRUCO_STATE
