from models.player import Player
from models.round import Round

class Game:
    def __init__(self, player1: Player, player2: Player):
        if player1 == player2:
            raise ValueError("Players must be different")
        
        self.players = [player1, player2]

        self.team1_score = 0
        self.team2_score = 0

    def play_round(self):
        round = Round(self.player1, self.player2)
        round.deal_cards()
        round.play_round()

