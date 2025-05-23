from models.deck import Deck
from models.player import Player
from models.card import Card

class Round:
    def __init__(self, players: list[Player]):
        self.players = players
        self.deck = Deck()

        self.muestra: Card = None

    def deal_cards(self):
        for player in self.players:
            player.hand = self.deck.draw(3)
        
        self.muestra = self.deck.draw(1)[0]

    def play_card(self, player: Player, card: Card):
        player.play_card(card)

