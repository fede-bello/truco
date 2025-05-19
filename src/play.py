# %%
from models.deck import Deck
from models.player import Player
from models.mano import Mano
def play():
    players = [Player("Player 1"), Player("Player 2"), Player("Player 3"), Player("Player 4")]
    mano = Mano(players)
    print(mano.deck)
    mano.deal_cards()
    print(mano.deck)

play()
# %%
