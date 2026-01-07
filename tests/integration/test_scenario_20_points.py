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

    try:
        # Strategy: 9 Rounds of Vale 4 (4 points each).
        # Alternating wins: T1, T2, T1, T2, T1, T2, T1, T2, T1.
        # Scores: 4-0, 4-4, 8-4, 8-8, 12-8, 12-12, 16-12, 16-16, 20-16.

        # Generic "God hand" vs "Trash hand" deals
        # Using unique cards for each player to avoid duplicate card objects in hands
        god_hand_1 = [AS_ESPADA, AS_BASTO, SIETE_ESPADA]
        god_hand_2 = [SIETE_ORO, TRES_ORO, DOS_ORO]
        trash_hand_1 = [CUATRO_COPA, CINCO_COPA, SEIS_COPA]
        trash_hand_2 = [CUATRO_BASTO, CINCO_BASTO, SEIS_BASTO]
        flor_hand = [AS_ESPADA, SIETE_ESPADA, CUATRO_ESPADA]  # 3 of same suit
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

        # Function to generate a round deal where A1 has a Flor
        def make_flor_deal() -> list[list[Card]]:
            return [
                list(flor_hand),
                list(trash_hand_1),
                list(trash_hand_2),
                list(god_hand_2),
                list(muestra),
            ]  # A1, B1, A2, B2

        def get_pies(starter_name: str) -> tuple[str, str]:
            # Returns (Pie_T1_Name, Pie_T2_Name)
            players = ["A1", "B1", "A2", "B2"]
            start_idx = players.index(starter_name)
            rotation = players[start_idx:] + players[:start_idx]

            pie_t1 = None
            for p in reversed(rotation):
                if p in ["A1", "A2"]:
                    pie_t1 = p
                    break

            pie_t2 = None
            for p in reversed(rotation):
                if p in ["B1", "B2"]:
                    pie_t2 = p
                    break
            return pie_t1, pie_t2

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

            pie_t1, pie_t2 = get_pies(starter_name)

            # Helper to get opponent pie
            def get_opp_pie(bidder_name):
                return pie_t2 if bidder_name in t1_players else pie_t1

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
                # Opponent Pie accepts
                l1 = get_opp_pie(w1)
                actions.append((l1, ActionCode.ACCEPT_TRUCO))

                if target_level >= 2:
                    # W1 plays a card
                    actions.append((w1, ActionCode.PLAY_CARD_0))
                    played_in_trick_1.append(w1)
                    current_idx += 1

                    # We need to simulate play until L1's turn if necessary.
                    while rotated[current_idx] != l1:
                        actions.append((rotated[current_idx], ActionCode.PLAY_CARD_0))
                        played_in_trick_1.append(rotated[current_idx])
                        current_idx += 1

                    # Now it is L1's turn. L1 bids Retruco.
                    actions.append((l1, ActionCode.OFFER_TRUCO))

                    # Determine responder (Winner Pie)
                    w_pie = get_opp_pie(l1)

                    if target_level >= 3:
                        # W_Pie counters with Vale 4 IMMEDIATELY
                        actions.append((w_pie, ActionCode.OFFER_TRUCO))
                        # Opponent Pie (L_Final_Pie) accepts
                        l_final_pie = get_opp_pie(w_pie)
                        actions.append((l_final_pie, ActionCode.ACCEPT_TRUCO))
                    else:
                        # W_Pie accepts Retruco
                        actions.append((w_pie, ActionCode.ACCEPT_TRUCO))

                    # L1 plays a card. (Wait, if L1 just bid Retruco, it's still L1's turn to play).
                    actions.append((l1, ActionCode.PLAY_CARD_0))
                    played_in_trick_1.append(l1)

            # Finish trick 1 if anyone hasn't played
            remaining_in_trick_1 = [p for p in rotated if p not in played_in_trick_1]
            for p in remaining_in_trick_1:
                actions.append((p, ActionCode.PLAY_CARD_0))

            # --- Trick 2 ---
            h2_starter = "A1" if winning_team_idx == 0 else "B1"
            h2_start_idx = players.index(h2_starter)
            h2_order = players[h2_start_idx:] + players[:h2_start_idx]

            for p in h2_order:
                actions.append((p, ActionCode.PLAY_CARD_1))

            return actions

        def make_flor_actions(starter_name: str) -> list[tuple[str, ActionCode]]:
            # Rotation: B1 -> A2 -> B2 -> A1
            actions = []
            actions.append(("B1", ActionCode.PLAY_CARD_0))
            actions.append(("A2", ActionCode.PLAY_CARD_0))
            actions.append(("B2", ActionCode.PLAY_CARD_0))
            # A1 says Flor, then plays card 0
            actions.append(("A1", ActionCode.FLOR))
            actions.append(("A1", ActionCode.PLAY_CARD_0))

            # Trick 2 (A1 wins T1 with As Espada)
            actions.append(("A1", ActionCode.PLAY_CARD_1))
            actions.append(("B1", ActionCode.PLAY_CARD_1))
            actions.append(("A2", ActionCode.PLAY_CARD_1))
            actions.append(("B2", ActionCode.PLAY_CARD_1))
            # Trick 3 (B2 wins T2)
            actions.append(("B2", ActionCode.PLAY_CARD_0))
            actions.append(("A1", ActionCode.PLAY_CARD_0))
            actions.append(("B1", ActionCode.PLAY_CARD_0))
            actions.append(("A2", ActionCode.PLAY_CARD_0))
            return actions

        all_deals = []
        all_actions = []

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

        # Add R14 with Flor
        all_deals.extend(make_flor_deal())
        all_actions.extend(make_flor_actions("B1"))  # Starter is B1 per rotation

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

        # R14: 24-15 (Flor + 1 truco pt)
        game.play_round()
        assert game.team1_score == 24
        assert game.team2_score == 15

        print("SUCCESS: 20-point varied scenario passed.")

    finally:
        patcher.stop()


if __name__ == "__main__":
    test_scenario_20_points()
