# %%
from models.deck import Deck
from models.player import Player
from models.round import Round
def play():
    players = [Player("Player 1"), Player("Player 2"), Player("Player 3"), Player("Player 4")]
    round = Round(players)
    print(round.deck)
    round.deal_cards()
    print(round.deck)

play()
# %%
