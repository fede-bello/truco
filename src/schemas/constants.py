from pathlib import Path
from typing import Literal

CardSuit = Literal["basto", "espadas", "oro", "copa"]
CardNumber = Literal[1, 2, 3, 4, 5, 6, 7, 10, 11, 12]

REY = 12

CARDS_DEALT_PER_PLAYER = 3

SUIT_TO_INDEX: dict[str, int] = {"basto": 0, "espadas": 1, "oro": 2, "copa": 3}
INDEX_TO_SUIT: dict[int, str] = {v: k for k, v in SUIT_TO_INDEX.items()}

BASE_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
