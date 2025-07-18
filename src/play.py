# %%
from models.game import Game
from models.player import Player


def play() -> None:
    player_1 = Player("Player 1")
    player_2 = Player("Player 2")
    game = Game(player_1, player_2)
    game.play_round()


play()
# %%
