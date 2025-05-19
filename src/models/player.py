class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand = []

    def __str__(self):
        return f"{self.name}"
    
    def __repr__(self):
        return f"{self.name}"

    def add_card(self, card):
        if card not in self.hand:
            if len(self.hand) >= 3:
                raise ValueError("Player can't have more than 3 cards")
            self.hand.append(card)
        else:
            raise ValueError(f"Card {card} already in hand")

    def remove_card(self, card):
        if card in self.hand:  
            self.hand.remove(card)
        else:
            raise ValueError(f"Card {card} not in hand")
        

        