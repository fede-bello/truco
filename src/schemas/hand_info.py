from pydantic import BaseModel, Field


class TeamInfo(BaseModel):
    points: int = 0


class RoundInfo(BaseModel):
    team1: TeamInfo = Field(default_factory=TeamInfo)
    team2: TeamInfo = Field(default_factory=TeamInfo)
