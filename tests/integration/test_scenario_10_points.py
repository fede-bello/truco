from unittest.mock import patch

from integration.setup import DeterministicActionProvider, MockDeck

from models.card import Card
from models.game import Game
from models.player import Player
from schemas.actions import ActionCode

# Cards (Power order rough guide: 1E, 1B, 7E, 7O, 3, 2, 1, 12, 11, 10, 7, 6, 5, 4)
# We will use simple clear winners.
# Winner cards
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

    # --- Setup ---
    # Team 1: P1 (A1), P3 (A2)
    # Team 2: P2 (B1), P4 (B2)
    # Order: A1, B1, A2, B2

    p_a1 = Player("A1")
    p_a2 = Player("A2")
    p_b1 = Player("B1")
    p_b2 = Player("B2")

    # We patch models.round.Deck to be our MockDeck
    patcher = patch("models.round.Deck", side_effect=MockDeck)
    patcher.start()

    # --- Round 1: T1 wins with Truco (2 pts) ---
    # Starter: A1
    # A1 deals Truco -> B1 Accepts.
    # A1 wins hand 1, A1 wins hand 2.

    # Queue for Round 1
    # Deal: A1, B1, A2, B2, Muestra
    r1_deal = [
        [AS_ESPADA, AS_BASTO, TRES_ORO],  # A1 (God hand)
        [CUATRO_COPA, CINCO_COPA, SEIS_COPA],  # B1 (Trash)
        [CUATRO_BASTO, CINCO_BASTO, SEIS_BASTO],  # A2 (Trash)
        [CUATRO_COPA, CINCO_COPA, SEIS_COPA],  # B2 (Trash)
        [Card(10, "oro")],  # Muestra (irrelevant for this match)
    ]

    # Actions Round 1
    # Order: A1 -> Truco -> B1 -> Accept -> A1 (Play 0) -> B1 (Play 0) -> A2 (Play 0) -> B2 (Play 0)
    # Winner Hand 1: A1 (As Espada)
    # Next Starter: A1
    # A1 (Play 1) -> B1 (Play 1) -> A2 (Play 1) -> B2 (Play 1)
    # Winner Hand 2: A1 (As Basto) -> T1 Wins Round

    r1_actions = [
        ("A1", ActionCode.OFFER_TRUCO),
        ("B1", ActionCode.ACCEPT_TRUCO),
        ("A1", ActionCode.PLAY_CARD_0),  # As Espada
        ("B1", ActionCode.PLAY_CARD_0),  # 4 Copa
        ("A2", ActionCode.PLAY_CARD_0),  # 4 Basto
        ("B2", ActionCode.PLAY_CARD_0),  # 4 Copa
        # Hand 1 done, A1 won.
        ("A1", ActionCode.PLAY_CARD_1),  # As Basto
        ("B1", ActionCode.PLAY_CARD_1),  # 5 Copa
        ("A2", ActionCode.PLAY_CARD_1),  # 5 Basto
        ("B2", ActionCode.PLAY_CARD_1),  # 5 Copa
        # Hand 2 done, A1 won. Round done.
    ]

    # --- Round 2: T2 wins normal (1 pt) ---
    # Starter: B1 (Rotated)
    # B1 wins Hand 1, B1 wins Hand 2
    r2_deal = [
        [CUATRO_COPA, CINCO_COPA, SEIS_COPA],  # A1
        [AS_ESPADA, AS_BASTO, TRES_ORO],  # B1 (God hand)
        [CUATRO_BASTO, CINCO_BASTO, SEIS_BASTO],  # A2
        [CUATRO_COPA, CINCO_COPA, SEIS_COPA],  # B2
        [Card(10, "oro")],  # Muestra
    ]
    r2_actions = [
        ("B1", ActionCode.PLAY_CARD_0),  # As Espada
        ("A2", ActionCode.PLAY_CARD_0),
        ("B2", ActionCode.PLAY_CARD_0),
        ("A1", ActionCode.PLAY_CARD_0),
        # Hand 1 winner B1
        ("B1", ActionCode.PLAY_CARD_1),  # As Basto
        ("A2", ActionCode.PLAY_CARD_1),
        ("B2", ActionCode.PLAY_CARD_1),
        ("A1", ActionCode.PLAY_CARD_1),
        # Hand 2 winner B1. Round winner T2.
    ]

    # --- Round 3: T1 wins Retruco (3 pts) ---
    # Starter: A2
    # A2 plays -> B2 plays -> A1 bids Truco -> B1 Bids Retruco -> A1 Accepts
    # T1 wins the cards.
    r3_deal = [
        [AS_ESPADA, AS_BASTO, TRES_ORO],  # A1
        [CUATRO_COPA, CINCO_COPA, SEIS_COPA],  # B1
        [SIETE_ESPADA, SIETE_ORO, DOS_ORO],  # A2 (Decent)
        [CUATRO_BASTO, CINCO_BASTO, SEIS_BASTO],  # B2
        [Card(10, "oro")],
    ]
    # Flow:
    # A2 plays 7E. B2 plays 4. A1 plays As E. B1 plays 4. -> A1 wins (Team 1)
    # A1 bids Truco. B1 ACCEPT. A1 Plays As B.
    # B1 bids Retruco. A1 Accept. B1 Plays 5.
    # A2 plays 7O. B2 plays 5. -> A1 wins.
    r3_actions = [
        ("A2", ActionCode.PLAY_CARD_0),  # 7E
        ("B2", ActionCode.PLAY_CARD_0),  # 4
        ("A1", ActionCode.PLAY_CARD_0),  # As E
        ("B1", ActionCode.PLAY_CARD_0),  # 4
        # Winner A1
        ("A1", ActionCode.OFFER_TRUCO),
        ("B1", ActionCode.ACCEPT_TRUCO),  # Must accept/reject first
        ("A1", ActionCode.PLAY_CARD_1),  # As B
        ("B1", ActionCode.OFFER_TRUCO),  # Retruco on B1's turn
        ("A2", ActionCode.ACCEPT_TRUCO),  # Responder is next(B1) -> A2
        ("B1", ActionCode.PLAY_CARD_1),  # B1 plays
        ("A2", ActionCode.PLAY_CARD_1),
        ("B2", ActionCode.PLAY_CARD_1),
        # Winner A1. T1 wins.
    ]

    # --- Round 4: T1 wins Vale 4 (4 pts) ---
    # Starter: B2
    # B2 Truco -> A1 Accept -> B2 plays
    # A1 Retruco -> B1 Accept -> A1 plays
    # B1 Vale 4 -> A2 Accept -> B1 plays
    # A2 plays.
    # T1 wins the hands.
    r4_deal = [
        [AS_ESPADA, AS_BASTO, TRES_ORO],  # A1
        [CUATRO_COPA, CINCO_COPA, SEIS_COPA],  # B1
        [SIETE_ESPADA, SIETE_ORO, DOS_ORO],  # A2
        [CUATRO_BASTO, CINCO_BASTO, SEIS_BASTO],  # B2
        [Card(12, "oro")],  # Muestra (neutral for B1's Copas)
    ]
    r4_actions = [
        ("B2", ActionCode.OFFER_TRUCO),
        ("A1", ActionCode.ACCEPT_TRUCO),
        ("B2", ActionCode.PLAY_CARD_0),
        ("A1", ActionCode.OFFER_TRUCO),  # Retruco
        ("B1", ActionCode.ACCEPT_TRUCO),  # Responder to A1 is B1 (next player).
        ("A1", ActionCode.PLAY_CARD_0),  # Wins with As E
        ("B1", ActionCode.OFFER_TRUCO),  # Vale 4
        ("A2", ActionCode.ACCEPT_TRUCO),  # Responder next(B1) = A2.
        ("B1", ActionCode.PLAY_CARD_0),
        ("A2", ActionCode.PLAY_CARD_0),
        # A1 winner
        ("A1", ActionCode.PLAY_CARD_1),  # As B
        ("B1", ActionCode.PLAY_CARD_1),
        ("A2", ActionCode.PLAY_CARD_1),
        ("B2", ActionCode.PLAY_CARD_1),
    ]

    # Total Score T1: 2 + 0 + 3 + 4 = 9. T2: 1.

    # --- Round 5: T1 wins (1 pt) to Finish ---
    # Starter: A1
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
        # A1 wins
        ("A1", ActionCode.PLAY_CARD_1),
        ("B1", ActionCode.PLAY_CARD_1),
        ("A2", ActionCode.PLAY_CARD_1),
        ("B2", ActionCode.PLAY_CARD_1),
    ]

    # Configure Deck and Action Provider
    all_deals = [r1_deal, r2_deal, r3_deal, r4_deal, r5_deal]
    # We need to flatten the deals correctly depending on how MockDeck works.
    # MockDeck pops one list per draw().
    # Round calls draw(3) x 4, then draw(1).
    # So for each round we need 5 entries in MockDeck queue.

    deck_queue = []
    for r_deal in all_deals:
        # r_deal has 5 lists: A1, B1, A2, B2, Muestra
        deck_queue.extend(r_deal)

    MockDeck.set_draw_queue(deck_queue)

    all_actions = r1_actions + r2_actions + r3_actions + r4_actions + r5_actions
    action_provider = DeterministicActionProvider(all_actions)

    # Game Init
    game = Game([p_a1, p_a2], [p_b1, p_b2], action_provider)

    # --- Execution & Assertions ---

    # Round 1
    print("Playing Round 1...")
    game.play_round()

    # Assertions R1
    assert game.team1_score == 2, f"R1: Expected T1=2, got {game.team1_score}"
    assert game.team2_score == 0, f"R1: Expected T2=0, got {game.team2_score}"

    # Round 2
    print("Playing Round 2...")
    game.play_round()
    assert game.team1_score == 2, f"R2: T1 should be 2, got {game.team1_score}"
    assert game.team2_score == 1, f"R2: T2 should be 1, got {game.team2_score}"

    # Round 3
    print("Playing Round 3...")
    game.play_round()
    assert game.team1_score == 5, f"R3: T1 should be 5, got {game.team1_score}"
    assert game.team2_score == 1, f"R3: T2 should be 1, got {game.team2_score}"

    # Round 4
    print("Playing Round 4...")
    game.play_round()
    assert game.team1_score == 9, f"R4: T1 should be 9, got {game.team1_score}"
    assert game.team2_score == 1, f"R4: T2 should be 1, got {game.team2_score}"

    # Round 5
    print("Playing Round 5...")
    game.play_round()
    assert game.team1_score >= 10, f"R5: T1 should win with >=10, got {game.team1_score}"
    assert game.team1_score == 10
    assert game.team2_score == 1

    print("SUCCESS: 10-point scenario passed.")
    patcher.stop()
