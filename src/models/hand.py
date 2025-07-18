from models.player import Player
from models.card import Card
class Hand:
    def __init__(self, team1: list[Player], team2: list[Player]):
        self.team1 = team1
        self.team2 = team2

    def _choose_card(self, player: Player) -> Card:
        for i, card in enumerate(player.cards):
            print(f"{i}: {card}", flush=True)
        card_index = int(input(f"Choose a card to play for {player.name}: "))
        return player.play_card(card_index)

    def play_hand(self, starting_team: list[Player]) -> tuple[list[Player], int]:
        """
        Have all players play one card each from their hands.
        
        Returns:
            tuple[list[Player], int]: The winning team and the index of the winning player in that team.
        """
        highest_card = None
        winning_team = None
        winning_player_index = None
        
        for i in range(len(self.team1)):
            for team in [self.team1, self.team2]:
                player = team[i]
                card = self._choose_card(player)

                if highest_card is None or card > highest_card:
                    highest_card = card
                    winning_team = team
                    winning_player_index = i

        print(f"Highest card: {highest_card}")
        print(f"Winning team: {winning_team}")
        
        return winning_team, winning_player_index