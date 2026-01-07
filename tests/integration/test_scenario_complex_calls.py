from unittest.mock import patch

from integration.setup import DeterministicActionProvider, MockDeck

from models.card import Card
from models.game import Game
from models.player import Player
from schemas.actions import ActionCode


def test_scenario_basic_envido_flor():
    print("Starting basic envido/flor scenario...")

    p_a1 = Player("A1")
    p_a2 = Player("A2")
    p_b1 = Player("B1")
    p_b2 = Player("B2")

    patcher = patch("models.round.Deck", side_effect=MockDeck)
    patcher.start()

    try:
        # --- Round 1: Envido Rejection, T1 Wins (2-0) ---
        # Starter A1. Order: A1, B1, A2, B2.
        # Team B Pie: B2.
        r1_deal = [
            [Card(1, "espadas"), Card(1, "basto"), Card(7, "espadas")],  # A1
            [Card(4, "oro"), Card(5, "oro"), Card(6, "oro")],  # B1
            [Card(1, "oro"), Card(7, "oro"), Card(12, "oro")],  # A2
            [Card(4, "copa"), Card(5, "copa"), Card(6, "copa")],  # B2
            [Card(12, "basto")],
        ]
        r1_actions = [
            ("A1", ActionCode.OFFER_ENVIDO),
            ("B2", ActionCode.REJECT_ENVIDO),  # B2 is Pie for Team B
            ("A1", ActionCode.PLAY_CARD_0),
            ("B1", ActionCode.PLAY_CARD_0),
            ("A2", ActionCode.PLAY_CARD_0),
            ("B2", ActionCode.PLAY_CARD_0),
            ("A1", ActionCode.PLAY_CARD_1),
            ("B1", ActionCode.PLAY_CARD_1),
            ("A2", ActionCode.PLAY_CARD_1),
            ("B2", ActionCode.PLAY_CARD_1),
        ]

        # --- Round 2: Envido Accepted, T2 Wins (0-2) ---
        # Starter B1. Order: B1, A2, B2, A1. (A1 was starter R1).
        # Team A Pie: A1.
        r2_deal = [
            [Card(6, "espadas"), Card(7, "espadas"), Card(3, "espadas")],  # A1
            [Card(4, "basto"), Card(1, "espadas"), Card(1, "basto")],  # B1
            [Card(6, "oro"), Card(7, "oro"), Card(12, "oro")],  # A2
            [Card(4, "copa"), Card(5, "copa"), Card(6, "copa")],  # B2
            [Card(10, "basto")],
        ]
        r2_actions = [
            ("B1", ActionCode.OFFER_ENVIDO),
            ("A1", ActionCode.ACCEPT_ENVIDO),  # A1 is Pie for Team A
            ("B1", ActionCode.PLAY_CARD_0),
            ("A2", ActionCode.PLAY_CARD_0),
            ("B2", ActionCode.PLAY_CARD_0),
            ("A1", ActionCode.PLAY_CARD_0),
            ("B1", ActionCode.PLAY_CARD_1),
            ("A2", ActionCode.PLAY_CARD_1),
            ("B2", ActionCode.PLAY_CARD_1),
            ("A1", ActionCode.PLAY_CARD_1),
        ]

        # --- Round 3: Flor cancels Envido, T1 Wins (2-0).
        # Starter A2. Order: A2, B2, A1, B1.
        # Team A Pie: A1. Team B Pie: B1.
        r3_deal = [
            [Card(1, "basto"), Card(2, "basto"), Card(3, "basto")],  # A1 (Flor)
            [Card(4, "oro"), Card(5, "oro"), Card(6, "oro")],  # B1
            [Card(4, "copa"), Card(5, "copa"), Card(6, "copa")],  # A2
            [Card(4, "basto"), Card(5, "basto"), Card(6, "basto")],  # B2
            [Card(12, "espadas")],
        ]
        r3_actions = [
            ("A2", ActionCode.PLAY_CARD_0),
            ("B2", ActionCode.OFFER_ENVIDO),
            ("A1", ActionCode.FLOR),  # A1 is Pie for Team A
            ("B2", ActionCode.PLAY_CARD_0),
            ("A1", ActionCode.PLAY_CARD_0),
            ("B1", ActionCode.PLAY_CARD_0),
            ("A1", ActionCode.PLAY_CARD_1),
            ("B1", ActionCode.PLAY_CARD_1),
            ("A2", ActionCode.PLAY_CARD_1),
            ("B2", ActionCode.PLAY_CARD_1),
        ]

        deck_queue = r1_deal + r2_deal + r3_deal
        MockDeck.set_draw_queue(deck_queue)
        action_provider = DeterministicActionProvider(r1_actions + r2_actions + r3_actions)

        game = Game([p_a1, p_a2], [p_b1, p_b2], action_provider)

        print("Executing R1...")
        game.play_round()
        print("Executing R2...")
        game.play_round()
        print("Executing R3...")
        game.play_round()

        print(f"Final Scores: T1={game.team1_score}, T2={game.team2_score}")
        assert game.team1_score == 8
        assert game.team2_score == 1

        print("SUCCESS: scenario passed.")

    finally:
        patcher.stop()


if __name__ == "__main__":
    test_scenario_basic_envido_flor()
