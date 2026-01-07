from unittest.mock import patch

from integration.setup import DeterministicActionProvider, MockDeck

from models.card import Card
from models.game import Game
from models.player import Player
from schemas.actions import ActionCode

# Cards
AS_ESPADA = Card(1, "espadas")
AS_BASTO = Card(1, "basto")
SIETE_ESPADA = Card(7, "espadas")
SIETE_ORO = Card(7, "oro")
TRES_ORO = Card(3, "oro")
DOS_ORO = Card(2, "oro")

# Loser cards
CUATRO_COPA = Card(4, "copa")
CINCO_COPA = Card(5, "copa")
SEIS_COPA = Card(6, "copa")
CUATRO_BASTO = Card(4, "basto")
CINCO_BASTO = Card(5, "basto")
SEIS_BASTO = Card(6, "basto")


def test_scenario_6_players():
    print("Starting 6-player scenario...")

    p_a1 = Player("A1")
    p_a2 = Player("A2")
    p_a3 = Player("A3")
    p_b1 = Player("B1")
    p_b2 = Player("B2")
    p_b3 = Player("B3")

    patcher = patch("models.round.Deck", side_effect=MockDeck)
    patcher.start()

    try:
        # --- Round 1: T1 wins normal (1 pt) ---
        # Starter: A1.
        # Deal order (Fixed): A1, B1, A2, B2, A3, B3, Muestra
        r1_deal = [
            [AS_ESPADA, AS_BASTO, TRES_ORO],  # A1
            [CUATRO_COPA, CINCO_COPA, SEIS_COPA],  # B1
            [CUATRO_BASTO, CINCO_BASTO, SEIS_BASTO],  # A2
            [CUATRO_COPA, CINCO_COPA, SEIS_COPA],  # B2
            [CUATRO_BASTO, CINCO_BASTO, SEIS_BASTO],  # A3
            [CUATRO_COPA, CINCO_COPA, SEIS_COPA],  # B3
            [Card(10, "oro")],  # Muestra
        ]

        r1_actions = [
            ("A1", ActionCode.PLAY_CARD_0),  # As Espada
            ("B1", ActionCode.PLAY_CARD_0),
            ("A2", ActionCode.PLAY_CARD_0),
            ("B2", ActionCode.PLAY_CARD_0),
            ("A3", ActionCode.PLAY_CARD_0),
            ("B3", ActionCode.PLAY_CARD_0),
            # Hand 1 done, A1 won.
            ("A1", ActionCode.PLAY_CARD_1),  # As Basto
            ("B1", ActionCode.PLAY_CARD_1),
            ("A2", ActionCode.PLAY_CARD_1),
            ("B2", ActionCode.PLAY_CARD_1),
            ("A3", ActionCode.PLAY_CARD_1),
            ("B3", ActionCode.PLAY_CARD_1),
            # Hand 2 done, A1 won. Round done.
        ]

        # --- Round 2: T2 wins with Truco (2 pts) ---
        # Starter: B1 (Rotated)
        # Pie T1: A1. Pie T2: B3.
        r2_deal = [
            [CUATRO_BASTO, CINCO_BASTO, SEIS_BASTO],  # A1
            [AS_ESPADA, AS_BASTO, TRES_ORO],  # B1
            [CUATRO_BASTO, CINCO_BASTO, SEIS_BASTO],  # A2
            [CUATRO_COPA, CINCO_COPA, SEIS_COPA],  # B2
            [CUATRO_BASTO, CINCO_BASTO, SEIS_BASTO],  # A3
            [CUATRO_COPA, CINCO_COPA, SEIS_COPA],  # B3
            [Card(11, "oro")],  # Muestra
        ]
        r2_actions = [
            ("B1", ActionCode.OFFER_TRUCO),
            ("A1", ActionCode.ACCEPT_TRUCO),  # Pie T1 (A1) accepts. Was A2.
            ("B1", ActionCode.PLAY_CARD_0),  # As Espada
            ("A2", ActionCode.PLAY_CARD_0),
            ("B2", ActionCode.PLAY_CARD_0),
            ("A3", ActionCode.PLAY_CARD_0),
            ("B3", ActionCode.PLAY_CARD_0),
            ("A1", ActionCode.PLAY_CARD_0),
            # Hand 1 winner B1
            ("B1", ActionCode.PLAY_CARD_1),  # As Basto
            ("A2", ActionCode.PLAY_CARD_1),
            ("B2", ActionCode.PLAY_CARD_1),
            ("A3", ActionCode.PLAY_CARD_1),
            ("B3", ActionCode.PLAY_CARD_1),
            ("A1", ActionCode.PLAY_CARD_1),
            # Hand 2 winner B1. Round winner T2.
        ]

        # Configure Deck and Action Provider
        all_deals = [r1_deal, r2_deal]
        deck_queue = []
        for r_deal in all_deals:
            deck_queue.extend(r_deal)

        MockDeck.set_draw_queue(deck_queue)

        all_actions = r1_actions + r2_actions
        action_provider = DeterministicActionProvider(all_actions)

        # Game Init
        game = Game([p_a1, p_a2, p_a3], [p_b1, p_b2, p_b3], action_provider)

        # Round 1
        print("Playing Round 1...")
        game.play_round()
        assert game.team1_score == 1
        assert game.team2_score == 0

        # Round 2
        print("Playing Round 2...")
        game.play_round()
        assert game.team1_score == 1
        assert game.team2_score == 2

        print("SUCCESS: 6-player scenario passed.")

    finally:
        patcher.stop()


if __name__ == "__main__":
    test_scenario_6_players()
