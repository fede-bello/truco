from typing import TypedDict

class TeamInfo(TypedDict):
    points: int = 0


class RoundInfo(TypedDict):
    team1: TeamInfo = TeamInfo()
    team2: TeamInfo = TeamInfo()
