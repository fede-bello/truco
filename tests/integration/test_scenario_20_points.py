import logging
import sys
from unittest.mock import patch

from integration.setup import DeterministicActionProvider, MockDeck

from models.card import Card
from models.game import Game
from models.player import Player
from schemas.actions import ActionCode

# Configure logging
logging.getLogger("models.round").setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logging.getLogger("models.round").addHandler(handler)


# Cards
AS_ESPADA = Card(1, "espadas")
AS_BASTO = Card(1, "basto")
SIETE_ESPADA = Card(7, "espadas")
SIETE_ORO = Card(7, "oro")
TRES_ORO = Card(3, "oro")
DOS_ORO = Card(2, "oro")
AS_ORO = Card(1, "oro")
AS_COPA = Card(1, "copa")

CUATRO_COPA = Card(4, "copa")
CINCO_COPA = Card(5, "copa")
SEIS_COPA = Card(6, "copa")
CUATRO_BASTO = Card(4, "basto")
CINCO_BASTO = Card(5, "basto")
SEIS_BASTO = Card(6, "basto")
CUATRO_ORO = Card(4, "oro")
CINCO_ORO = Card(5, "oro")
SEIS_ORO = Card(6, "oro")
CUATRO_ESPADA = Card(4, "espadas")
CINCO_ESPADA = Card(5, "espadas")
SEIS_ESPADA = Card(6, "espadas")


def test_scenario_20_points():
    print("Starting 20-point scenario...")

    p_a1 = Player("A1")
    p_a2 = Player("A2")
    p_b1 = Player("B1")
    p_b2 = Player("B2")

    patcher = patch("models.round.Deck", side_effect=MockDeck)
    patcher.start()

    # Strategy: 9 Rounds of Vale 4 (4 points each).
    # Alternating wins: T1, T2, T1, T2, T1, T2, T1, T2, T1.
    # Scores: 4-0, 4-4, 8-4, 8-8, 12-8, 12-12, 16-12, 16-16, 20-16.

    # Generic "God hand" vs "Trash hand" deals
    # Using unique cards for each player to avoid duplicate card objects in hands
    god_hand_1 = [AS_ESPADA, AS_BASTO, SIETE_ESPADA]
    god_hand_2 = [SIETE_ORO, TRES_ORO, DOS_ORO]
    trash_hand_1 = [CUATRO_COPA, CINCO_COPA, SEIS_COPA]
    trash_hand_2 = [CUATRO_BASTO, CINCO_BASTO, SEIS_BASTO]
    # Muestra neutral
    muestra = [Card(12, "oro")]  # Rey oro

    # Function to generate a round deal where 'winner_team_idx' (0=T1, 1=T2) gets god hands
    def make_deal(winner_team_idx: int) -> list[list[Card]]:
        if winner_team_idx == 0:
            return [
                list(god_hand_1),
                list(trash_hand_1),
                list(god_hand_2),
                list(trash_hand_2),
                list(muestra),
            ]  # A1, B1, A2, B2
        else:
            return [
                list(trash_hand_1),
                list(god_hand_1),
                list(trash_hand_2),
                list(god_hand_2),
                list(muestra),
            ]  # A1, B1, A2, B2

    # Function to generate actions with a specific truco escalation level
    # target_level: 0=None, 1=Truco, 2=Retruco, 3=Vale 4
    def make_actions(
        starter_name: str, winning_team_idx: int, target_level: int = 3
    ) -> list[tuple[str, ActionCode]]:
        players = ["A1", "B1", "A2", "B2"]
        start_idx = players.index(starter_name)
        rotated = players[start_idx:] + players[:start_idx]

        t1_players = ["A1", "A2"]
        t2_players = ["B1", "B2"]
        winners = t1_players if winning_team_idx == 0 else t2_players

        actions = []

        # --- Trick 1 ---
        current_idx = 0
        played_in_trick_1 = []

        # Winners want to bid. They will bid on their first turn in trick 1 if target_level > 0.
        # We need to play cards until a winner's turn.
        while rotated[current_idx] not in winners:
            actions.append((rotated[current_idx], ActionCode.PLAY_CARD_0))
            played_in_trick_1.append(rotated[current_idx])
            current_idx += 1

        # Now it's a winner's turn (W1)
        w1 = rotated[current_idx]

        if target_level >= 1:
            # W1 bids Truco
            actions.append((w1, ActionCode.OFFER_TRUCO))
            # Next player (L1) accepts
            l1 = players[(players.index(w1) + 1) % 4]
            actions.append((l1, ActionCode.ACCEPT_TRUCO))

            if target_level >= 2:
                # W1 plays a card, then L1 bids Retruco
                actions.append((w1, ActionCode.PLAY_CARD_0))
                played_in_trick_1.append(w1)
                current_idx += 1

                # L1 bids Retruco
                actions.append((l1, ActionCode.OFFER_TRUCO))
                # Next player (W2) accepts
                w2 = players[(players.index(l1) + 1) % 4]
                actions.append((w2, ActionCode.ACCEPT_TRUCO))

                if target_level >= 3:
                    # L1 plays a card, then W2 bids Vale 4
                    actions.append((l1, ActionCode.PLAY_CARD_0))
                    played_in_trick_1.append(l1)
                    current_idx += 1

                    # W2 bids Vale 4
                    actions.append((w2, ActionCode.OFFER_TRUCO))
                    # Next player (L2) accepts
                    l2 = players[(players.index(w2) + 1) % 4]
                    actions.append((l2, ActionCode.ACCEPT_TRUCO))

        # Finish trick 1 if anyone hasn't played
        remaining_in_trick_1 = [p for p in rotated if p not in played_in_trick_1]
        for p in remaining_in_trick_1:
            actions.append((p, ActionCode.PLAY_CARD_0))

        # --- Trick 2 ---
        # With our god hands, T1/T2 (winners) always win trick 1.
        # Winner of Hand 1 starts Hand 2.
        # In our deals, AS_ESPADA is in god_hand_1, SIETE_ORO in god_hand_2.
        # If winning_team_idx == 0, A1 wins Trick 1.
        # If winning_team_idx == 1, B1 wins Trick 1.
        h2_starter = "A1" if winning_team_idx == 0 else "B1"
        h2_start_idx = players.index(h2_starter)
        h2_order = players[h2_start_idx:] + players[:h2_start_idx]

        for p in h2_order:
            actions.append((p, ActionCode.PLAY_CARD_1))

        return actions

    all_deals = []
    all_actions = []

    # Sequence of rounds to reach 20 points with variety:
    # R1: T1 win, No Truco (1 pt) -> 1-0 (Starter A1)
    # R2: T2 win, Truco (2 pts) -> 1-2 (Starter B1)
    # R3: T1 win, Retruco (3 pts) -> 4-2 (Starter A2)
    # R4: T2 win, Vale 4 (4 pts) -> 4-6 (Starter B2)
    # R5: T1 win, No Truco (1 pt) -> 5-6 (Starter A1)
    # R6: T2 win, Retruco (3 pts) -> 5-9 (Starter B1)
    # R7: T1 win, Vale 4 (4 pts) -> 9-9 (Starter A2)
    # R8: T2 win, Truco (2 pts) -> 9-11 (Starter B2)
    # R9: T1 win, Vale 4 (4 pts) -> 13-11 (Starter A1)
    # R10: T2 win, Vale 4 (4 pts) -> 13-15 (Starter B1)
    # R11: T1 win, Vale 4 (4 pts) -> 17-15 (Starter A2)
    # R12: T1 win, Truco (2 pts) -> 19-15 (Starter B2)
    # R13: T1 win, No Truco (1 pt) -> 20-15 (Starter A1)

    scenario = [
        ("A1", 0, 0),  # Starter, WinnerTeam, TargetLevel
        ("B1", 1, 1),
        ("A2", 0, 2),
        ("B2", 1, 3),
        ("A1", 0, 0),
        ("B1", 1, 2),
        ("A2", 0, 3),
        ("B2", 1, 1),
        ("A1", 0, 3),
        ("B1", 1, 3),
        ("A2", 0, 3),
        ("B2", 0, 1),
        ("A1", 0, 0),
    ]

    for start_name, win_idx, level in scenario:
        all_deals.extend(make_deal(win_idx))
        all_actions.extend(make_actions(start_name, win_idx, level))

    MockDeck.set_draw_queue(all_deals)
    action_provider = DeterministicActionProvider(all_actions)

    game = Game([p_a1, p_a2], [p_b1, p_b2], action_provider)

    print("Playing 20-point match with varying Truco levels...")

    # R1: 1-0
    game.play_round()
    assert game.team1_score == 1

    # R2: 1-2
    game.play_round()
    assert game.team2_score == 2

    # R3: 4-2
    game.play_round()
    assert game.team1_score == 4

    # R4: 4-6
    game.play_round()
    assert game.team2_score == 6

    # R5: 5-6
    game.play_round()
    assert game.team1_score == 5

    # R6: 5-9
    game.play_round()
    assert game.team2_score == 9

    # R7: 9-9
    game.play_round()
    assert game.team1_score == 9
    assert game.team2_score == 9

    # R8: 9-11
    game.play_round()
    assert game.team2_score == 11

    # R9: 13-11
    game.play_round()
    assert game.team1_score == 13

    # R10: 13-15
    game.play_round()
    assert game.team2_score == 15

    # R11: 17-15
    game.play_round()
    assert game.team1_score == 17

    # R12: 19-15
    game.play_round()
    assert game.team1_score == 19

    # R13: 20-15
    game.play_round()
    assert game.team1_score == 20
    assert game.team2_score == 15

    print("SUCCESS: 20-point varied scenario passed.")
    patcher.stop()
