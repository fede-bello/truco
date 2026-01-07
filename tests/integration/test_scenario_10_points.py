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


def test_scenario_10_points():
    print("Starting 10-point scenario...")

    p_a1 = Player("A1")
    p_a2 = Player("A2")
    p_b1 = Player("B1")
    p_b2 = Player("B2")

    # We patch models.round.Deck to be our MockDeck
    patcher = patch("models.round.Deck", side_effect=MockDeck)
    patcher.start()

    try:
        # --- Round 1: T1 wins with Truco (2 pts) ---
        # Starter: A1. Order: A1, B1, A2, B2.
        # Team 2 Pie is B2.
        r1_deal = [
            [AS_ESPADA, AS_BASTO, TRES_ORO],  # A1
            [CUATRO_COPA, CINCO_COPA, SEIS_COPA],  # B1
            [CUATRO_BASTO, CINCO_BASTO, SEIS_BASTO],  # A2
            [CUATRO_COPA, CINCO_COPA, SEIS_COPA],  # B2
            [Card(10, "oro")],  # Muestra
        ]
        r1_actions = [
            ("A1", ActionCode.OFFER_TRUCO),
            ("B2", ActionCode.ACCEPT_TRUCO),  # Pie B2 responds
            ("A1", ActionCode.PLAY_CARD_0),
            ("B1", ActionCode.PLAY_CARD_0),
            ("A2", ActionCode.PLAY_CARD_0),
            ("B2", ActionCode.PLAY_CARD_0),
            ("A1", ActionCode.PLAY_CARD_1),
            ("B1", ActionCode.PLAY_CARD_1),
            ("A2", ActionCode.PLAY_CARD_1),
            ("B2", ActionCode.PLAY_CARD_1),
        ]

        # --- Round 2: T2 wins normal (1 pt) ---
        # Starter: B1.
        r2_deal = [
            [CUATRO_COPA, CINCO_COPA, SEIS_COPA],  # A1
            [AS_ESPADA, AS_BASTO, TRES_ORO],  # B1
            [CUATRO_BASTO, CINCO_BASTO, SEIS_BASTO],  # A2
            [CUATRO_COPA, CINCO_COPA, SEIS_COPA],  # B2
            [Card(10, "oro")],  # Muestra
        ]
        r2_actions = [
            ("B1", ActionCode.PLAY_CARD_0),
            ("A2", ActionCode.PLAY_CARD_0),
            ("B2", ActionCode.PLAY_CARD_0),
            ("A1", ActionCode.PLAY_CARD_0),
            ("B1", ActionCode.PLAY_CARD_1),
            ("A2", ActionCode.PLAY_CARD_1),
            ("B2", ActionCode.PLAY_CARD_1),
            ("A1", ActionCode.PLAY_CARD_1),
        ]

        # --- Round 3: T1 wins Retruco (3 pts) ---
        # Starter: A2. Order: A2, B2, A1, B1.
        # T2 Pie: B1. T1 Pie: A1.
        r3_deal = [
            [AS_ESPADA, AS_BASTO, TRES_ORO],  # A1
            [CUATRO_COPA, CINCO_COPA, SEIS_COPA],  # B1
            [SIETE_ESPADA, SIETE_ORO, DOS_ORO],  # A2
            [CUATRO_BASTO, CINCO_BASTO, SEIS_BASTO],  # B2
            [Card(10, "oro")],
        ]
        r3_actions = [
            ("A2", ActionCode.PLAY_CARD_0),
            ("B2", ActionCode.PLAY_CARD_0),
            ("A1", ActionCode.PLAY_CARD_0),
            ("B1", ActionCode.PLAY_CARD_0),
            ("A1", ActionCode.OFFER_TRUCO),
            ("B1", ActionCode.ACCEPT_TRUCO),  # Pie T2 (B1)
            ("A1", ActionCode.PLAY_CARD_1),
            ("B1", ActionCode.OFFER_TRUCO),  # Retruco
            ("A1", ActionCode.ACCEPT_TRUCO),  # Pie T1 (A1)
            ("B1", ActionCode.PLAY_CARD_1),
            ("A2", ActionCode.PLAY_CARD_1),
            ("B2", ActionCode.PLAY_CARD_1),
        ]

        # --- Round 4: T1 wins Vale 4 (4 pts) ---
        # Starter: B2. Order: B2, A1, B1, A2.
        # T1 Pie: A2. T2 Pie: B1.
        r4_deal = [
            [AS_ESPADA, AS_BASTO, TRES_ORO],  # A1
            [CUATRO_COPA, CINCO_COPA, SEIS_COPA],  # B1
            [SIETE_ESPADA, SIETE_ORO, DOS_ORO],  # A2
            [CUATRO_BASTO, CINCO_BASTO, SEIS_BASTO],  # B2
            [Card(12, "oro")],
        ]
        r4_actions = [
            ("B2", ActionCode.OFFER_TRUCO),
            ("A2", ActionCode.ACCEPT_TRUCO),  # Pie T1 (A2)
            ("B2", ActionCode.PLAY_CARD_0),
            ("A1", ActionCode.OFFER_TRUCO),  # Retruco
            ("B1", ActionCode.ACCEPT_TRUCO),  # Pie T2 (B1)
            ("A1", ActionCode.PLAY_CARD_0),
            ("B1", ActionCode.OFFER_TRUCO),  # Vale 4
            ("A2", ActionCode.ACCEPT_TRUCO),  # Pie T1 (A2)
            ("B1", ActionCode.PLAY_CARD_0),
            ("A2", ActionCode.PLAY_CARD_0),
            ("A1", ActionCode.PLAY_CARD_1),
            ("B1", ActionCode.PLAY_CARD_1),
            ("A2", ActionCode.PLAY_CARD_1),
            ("B2", ActionCode.PLAY_CARD_1),
        ]

        # --- Round 5: T1 wins (1 pt) ---
        # Starter: A1.
        r5_deal = [
            [AS_ESPADA, AS_BASTO, TRES_ORO],  # A1
            [CUATRO_COPA, CINCO_COPA, SEIS_COPA],  # B1
            [CUATRO_BASTO, CINCO_BASTO, SEIS_BASTO],  # A2
            [CUATRO_COPA, CINCO_COPA, SEIS_COPA],  # B2
            [Card(12, "oro")],
        ]
        r5_actions = [
            ("A1", ActionCode.PLAY_CARD_0),
            ("B1", ActionCode.PLAY_CARD_0),
            ("A2", ActionCode.PLAY_CARD_0),
            ("B2", ActionCode.PLAY_CARD_0),
            ("A1", ActionCode.PLAY_CARD_1),
            ("B1", ActionCode.PLAY_CARD_1),
            ("A2", ActionCode.PLAY_CARD_1),
            ("B2", ActionCode.PLAY_CARD_1),
        ]

        # Configure Deck
        deck_queue = []
        for r_deal in [r1_deal, r2_deal, r3_deal, r4_deal, r5_deal]:
            deck_queue.extend(r_deal)
        MockDeck.set_draw_queue(deck_queue)

        # Configure Actions
        all_actions = r1_actions + r2_actions + r3_actions + r4_actions + r5_actions
        action_provider = DeterministicActionProvider(all_actions)

        game = Game([p_a1, p_a2], [p_b1, p_b2], action_provider)

        print("Playing Round 1...")
        game.play_round()
        assert game.team1_score == 2
        assert game.team2_score == 0

        print("Playing Round 2...")
        game.play_round()
        assert game.team1_score == 2
        assert game.team2_score == 1

        print("Playing Round 3...")
        game.play_round()
        assert game.team1_score == 5
        assert game.team2_score == 1

        print("Playing Round 4...")
        game.play_round()
        assert game.team1_score == 9
        assert game.team2_score == 1

        print("Playing Round 5...")
        game.play_round()
        assert game.team1_score == 10
        assert game.team2_score == 1

        print("SUCCESS: 10-point scenario passed.")

    finally:
        patcher.stop()


if __name__ == "__main__":
    test_scenario_10_points()
