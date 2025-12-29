from unittest.mock import patch

from integration.setup import DeterministicActionProvider, MockDeck

from models.card import Card
from models.game import Game
from models.player import Player
from schemas.actions import ActionCode

# Cards (Power order rough guide: 1E, 1B, 7E, 7O, 3, 2, 1, 12, 11, 10, 7, 6, 5, 4)
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


def test_scenario_2_players():
    print("Starting 2-player scenario...")

    # --- Setup ---
    # Team 1: P1
    # Team 2: P2
    # Order: P1, P2

    p1 = Player("P1")
    p2 = Player("P2")

    # We patch models.round.Deck to be our MockDeck
    patcher = patch("models.round.Deck", side_effect=MockDeck)
    patcher.start()

    # --- Round 1: P1 wins normal (1 pt) ---
    # Starter: P1
    # P1 wins hand 1, P1 wins hand 2.
    r1_deal = [
        [AS_ESPADA, AS_BASTO, TRES_ORO],  # P1
        [CUATRO_COPA, CINCO_COPA, SEIS_COPA],  # P2
        [Card(10, "oro")],  # Muestra
    ]

    r1_actions = [
        ("P1", ActionCode.PLAY_CARD_0),  # As Espada
        ("P2", ActionCode.PLAY_CARD_0),  # 4 Copa
        # Hand 1 done, P1 won.
        ("P1", ActionCode.PLAY_CARD_1),  # As Basto
        ("P2", ActionCode.PLAY_CARD_1),  # 5 Copa
        # Hand 2 done, P1 won. Round done.
    ]

    # --- Round 2: P2 wins with Truco (2 pts) ---
    # Starter: P2 (Rotated)
    # P2 bids Truco -> P1 Accepts.
    # P2 wins hand 1, P2 wins hand 2.
    r2_deal = [
        [CUATRO_BASTO, CINCO_BASTO, SEIS_BASTO],  # P1
        [SIETE_ESPADA, SIETE_ORO, DOS_ORO],  # P2
        [Card(11, "oro")],  # Muestra
    ]
    r2_actions = [
        ("P2", ActionCode.OFFER_TRUCO),
        ("P1", ActionCode.ACCEPT_TRUCO),
        ("P2", ActionCode.PLAY_CARD_0),  # 7 Espada
        ("P1", ActionCode.PLAY_CARD_0),  # 4 Basto
        # Hand 1 winner P2
        ("P2", ActionCode.PLAY_CARD_1),  # 7 Oro
        ("P1", ActionCode.PLAY_CARD_1),  # 5 Basto
        # Hand 2 winner P2. Round winner T2.
    ]

    # --- Round 3: P1 wins with Vale 4 (4 pts) ---
    # Starter: P1
    r3_deal = [
        [AS_ESPADA, AS_BASTO, SIETE_ESPADA],  # P1
        [CUATRO_COPA, CINCO_COPA, SEIS_COPA],  # P2
        [Card(12, "oro")],  # Muestra
    ]
    r3_actions = [
        ("P1", ActionCode.OFFER_TRUCO),  # Truco
        ("P2", ActionCode.ACCEPT_TRUCO),
        ("P1", ActionCode.PLAY_CARD_0),  # As E
        ("P2", ActionCode.OFFER_TRUCO),  # Retruco
        ("P1", ActionCode.ACCEPT_TRUCO),
        ("P2", ActionCode.PLAY_CARD_0),  # 4 Copa
        # P1 won 1st hand
        ("P1", ActionCode.OFFER_TRUCO),  # Vale 4
        ("P2", ActionCode.ACCEPT_TRUCO),
        ("P1", ActionCode.PLAY_CARD_1),  # As B
        ("P2", ActionCode.PLAY_CARD_1),  # 5 Copa
    ]

    # Total Score T1: 1 + 0 + 4 = 5. T2: 2.

    # Configure Deck and Action Provider
    all_deals = [r1_deal, r2_deal, r3_deal]
    deck_queue = []
    for r_deal in all_deals:
        deck_queue.extend(r_deal)

    MockDeck.set_draw_queue(deck_queue)

    all_actions = r1_actions + r2_actions + r3_actions
    action_provider = DeterministicActionProvider(all_actions)

    # Game Init
    game = Game([p1], [p2], action_provider)

    # --- Execution & Assertions ---

    # Round 1
    print("Playing Round 1...")
    game.play_round()
    assert game.team1_score == 1, f"R1: Expected T1=1, got {game.team1_score}"
    assert game.team2_score == 0, f"R1: Expected T2=0, got {game.team2_score}"

    # Round 2
    print("Playing Round 2...")
    game.play_round()
    assert game.team1_score == 1, f"R2: T1 should be 1, got {game.team1_score}"
    assert game.team2_score == 2, f"R2: T2 should be 2, got {game.team2_score}"

    # Round 3
    print("Playing Round 3...")
    game.play_round()
    assert game.team1_score == 5, f"R3: T1 should be 5, got {game.team1_score}"
    assert game.team2_score == 2, f"R3: T2 should be 2, got {game.team2_score}"

    print("SUCCESS: 2-player scenario passed.")
    patcher.stop()
