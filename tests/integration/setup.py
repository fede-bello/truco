import sys
from collections import deque
from pathlib import Path

# Ensure src is in python path
sys.path.append(Path(__file__).parent.parent / "src")

from models.card import Card
from models.player import Player
from schemas.actions import ActionCode
from schemas.player_state import PlayerState


class MockDeck:
    """A mock deck that deals pre-determined cards."""

    # Global queue of 'hands' or 'cards' to be dealt.
    # We can structure this as a list of lists of cards to be returned by successive draw() calls.
    _draw_queue: deque[list[Card]] = deque()

    def __init__(self) -> None:
        pass

    def draw(self, n: int) -> list[Card]:
        if not MockDeck._draw_queue:
            raise ValueError("MockDeck ran out of pre-configured cards to draw!")

        cards = MockDeck._draw_queue.popleft()
        if len(cards) != n:
            raise ValueError(f"MockDeck expected to draw {n} cards but queue had {len(cards)}")
        return cards

    @classmethod
    def set_draw_queue(cls, queue: list[list[Card]]) -> None:
        cls._draw_queue = deque(queue)


class DeterministicActionProvider:
    """A provider that yields actions from a pre-configured script."""

    def __init__(self, script: list[tuple[str, ActionCode]]) -> None:
        """Args:
        script: A dictionary mapping player names to a list of actions they should take.
                Or simpler: just a single list of actions if we expect a strict global order?

                Better approach for robustness: A queue of expected calls.
                Or even better for this specific request:
                We can just use a single queue of actions if we trust the game order.
                BUT, user said "Hardcodes ... players actions etc".

                The most robust way is to have a queue per player (or a global queue if we are strict).
                Let's use a global queue of (PlayerName, Action) tuples to also verify the order!
        """
        self.action_queue = deque(script)
        # Optionally allow a simple list of codes if we don't care about verifying player name here (but we should)

    def set_script(self, script: list[tuple[str, ActionCode]]):
        self.action_queue = deque(script)

    def __call__(
        self, player: Player, player_state: PlayerState, available_actions: list[ActionCode]
    ) -> ActionCode:
        print(f"DEBUG: Request action for {player.name}. Queue len: {len(self.action_queue)}")
        if not self.action_queue:
            print("DEBUG: Empty queue! History of last few pops?")
            raise ValueError(f"ActionQueue empty! Player {player.name} needed an action.")

        expected_player_name, action = self.action_queue.popleft()
        print(
            f"DEBUG: Popped action ({expected_player_name}, {action}) for request by {player.name}"
        )

        if expected_player_name != player.name:
            # We can log a warning or raise an error. For an integration test, strict is good.
            # But the 'Game' interleaves players. If our script is wrong, this helps debug.
            raise ValueError(
                f"Expected action from {expected_player_name}, but {player.name} was asked."
            )

        if action not in available_actions:
            raise ValueError(
                f"Deterministic action {action} not in available: {available_actions} for {player.name}"
            )

        return action
