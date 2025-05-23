# %%
from models.player import Player
from models.game import Game

def play():
    team1 = [Player("Player 1")]
    team2 = [Player("Player 3")]
    game = Game(team1, team2)
    game.play_hand()

play()
# %%
