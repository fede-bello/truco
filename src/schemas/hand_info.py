from pydantic import BaseModel


class TeamInfo(BaseModel):
    points: int = 0


class RoundInfo(BaseModel):
    team1: TeamInfo = TeamInfo()
    team2: TeamInfo = TeamInfo()
