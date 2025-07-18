# %%
from models.player import Player
from models.game import Game

def play():
    player1 = Player("Player 1")
    player2 = Player("Player 2")
    game = Game(player1, player2)
    game.play_round()

play()
# %%
