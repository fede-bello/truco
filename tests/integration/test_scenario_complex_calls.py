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

    # --- Round 1: Envido Rejection, T1 Wins (2-0) ---
    # Starter A1. Order: A1, B1, A2, B2.
    # Muestra: 12 Basto.
    r1_deal = [
        [Card(1, "espadas"), Card(1, "basto"), Card(7, "espadas")],  # A1 (Very Strong)
        [Card(4, "oro"), Card(5, "oro"), Card(6, "oro")],  # B1
        [Card(1, "oro"), Card(7, "oro"), Card(12, "oro")],  # A2
        [Card(4, "copa"), Card(5, "copa"), Card(6, "copa")],  # B2
        [Card(12, "basto")],
    ]
    # Hand 1: A1 plays 1 espada (13) -> wins.
    # Hand 2: A1 starts, plays 1 basto (12) -> wins. Round ends.
    r1_actions = [
        ("A1", ActionCode.OFFER_ENVIDO),
        ("B1", ActionCode.REJECT_ENVIDO),  # T1 gets 1 pt.
        ("A1", ActionCode.PLAY_CARD_0),
        ("B1", ActionCode.PLAY_CARD_0),
        ("A2", ActionCode.PLAY_CARD_0),
        ("B2", ActionCode.PLAY_CARD_0),
        # Hand 1 winner A1. Hand 2 starter A1.
        ("A1", ActionCode.PLAY_CARD_1),
        ("B1", ActionCode.PLAY_CARD_1),
        ("A2", ActionCode.PLAY_CARD_1),
        ("B2", ActionCode.PLAY_CARD_1),
    ]

    # --- Round 2: Envido Accepted, T2 Wins (0-2) ---
    # Starter B1. Order: B1, A2, B2, A1.
    # Muestra: 10 Basto (PIEZA). Piece suit: Basto. Pieces: 2, 4, 5, 11, 12 of Basto.
    # B1: 4 Basto (29), 6 copa (6), 3 oro (3). Envido = 35.
    # A1: 6 espadas, 7 espadas, 3 espadas. Envido = 33.
    r2_deal = [
        [Card(6, "espadas"), Card(7, "espadas"), Card(3, "espadas")],  # A1
        [Card(4, "basto"), Card(1, "espadas"), Card(1, "basto")],  # B1 (Bidding Player)
        [Card(6, "oro"), Card(7, "oro"), Card(12, "oro")],  # A2
        [Card(4, "copa"), Card(5, "copa"), Card(6, "copa")],  # B2
        [Card(10, "basto")],
    ]
    # Hand 1: B1 plays 4 Basto (Pieza 17) -> wins.
    # Hand 2: B1 starts, plays 1 espada (13) -> wins. Round ends.
    r2_actions = [
        ("B1", ActionCode.OFFER_ENVIDO),
        ("A2", ActionCode.ACCEPT_ENVIDO),  # T2 wins Envido (2 pts).
        ("B1", ActionCode.PLAY_CARD_0),
        ("A2", ActionCode.PLAY_CARD_0),
        ("B2", ActionCode.PLAY_CARD_0),
        ("A1", ActionCode.PLAY_CARD_0),
        # Hand 1 winner B1. Hand 2 starter B1.
        ("B1", ActionCode.PLAY_CARD_1),
        ("A2", ActionCode.PLAY_CARD_1),
        ("B2", ActionCode.PLAY_CARD_1),
        ("A1", ActionCode.PLAY_CARD_1),
    ]

    # --- Round 3: Flor cancels Envido, T1 Wins (2-0). Total T1: 6, T2: 3 ---
    # Starter A2. Order: A2, B2, A1, B1.
    # Muestra: 12 Espadas.
    r3_deal = [
        [Card(1, "basto"), Card(2, "basto"), Card(3, "basto")],  # A1 (Flor + Very Strong)
        [Card(4, "oro"), Card(5, "oro"), Card(6, "oro")],  # B1
        [Card(4, "copa"), Card(5, "copa"), Card(6, "copa")],  # A2 (Hand)
        [Card(4, "basto"), Card(5, "basto"), Card(6, "basto")],  # B2
        [Card(12, "espadas")],
    ]
    # A2 (Hand) plays Card 0.
    # B2 (Opponent) offers Envido.
    # A1 (Responder) says Flor.
    r3_actions = [
        ("A2", ActionCode.PLAY_CARD_0),
        ("B2", ActionCode.OFFER_ENVIDO),
        ("A1", ActionCode.FLOR),  # Cancels Envido. T1 gets 3 pts.
        ("B2", ActionCode.PLAY_CARD_0),
        ("A1", ActionCode.PLAY_CARD_0),  # 1 basto wins (12 mata)
        ("B1", ActionCode.PLAY_CARD_0),
        # Winner Hand 1: A1. Starter Hand 2: A1. Order: A1, B1, A2, B2.
        ("A1", ActionCode.PLAY_CARD_1),  # 2 basto wins
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
    print(f"R1 Scores: T1={game.team1_score}, T2={game.team2_score}")
    assert game.team1_score == 2
    assert game.team2_score == 0

    print("Executing R2...")
    game.play_round()
    print(f"R2 Scores: T1={game.team1_score}, T2={game.team2_score}")
    # R1: T1=2, T2=0.
    # R2: T1 gets 2 (Envido), T2 gets 1 (Cards).
    # Total: T1=4, T2=1.
    assert game.team1_score == 4
    assert game.team2_score == 1

    print("Executing R3...")
    game.play_round()
    print(f"R3 Scores: T1={game.team1_score}, T2={game.team2_score}")
    # R1+R2: T1=4, T2=1.
    # R3: T1 gets 3 (Flor) + 1 (Cards).
    # Total: T1=8, T2=1.
    assert game.team1_score == 8
    assert game.team2_score == 1

    print(f"Final Scores: T1={game.team1_score}, T2={game.team2_score}")
    # R1: T1=2 (1 Envido + 1 Card)
    # R2: T2=3 (2 Envido + 1 Card)
    # R3: T1=4 (3 Flor + 1 Card)
    # Total T1: 6. T2: 3.
    assert game.team1_score == 8
    assert game.team2_score == 1

    print("SUCCESS: scenario passed.")
    patcher.stop()


if __name__ == "__main__":
    test_scenario_basic_envido_flor()
