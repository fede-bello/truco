from models.player import Player
from models.hand import Hand

class Game:
    def __init__(self, team1: list[Player], team2: list[Player]):
        if len(team1) != len(team2):
            raise ValueError("Teams must have the same number of players")
        
        self.team1 = team1
        self.team2 = team2
        self.hand = Hand(team1, team2)

        self.team1_score = 0
        self.team2_score = 0

    def play_hand(self):
        self.hand.deal_cards()
        print(f"Cartas de cada jugador")
        for player in self.hand.team1:
            print(f"{player.name}: {player.cards}")
        for player in self.hand.team2:
            print(f"{player.name}: {player.cards}")
        
        self.hand.play_round()

