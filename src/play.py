# %%
from logging_config import get_logger
from models.game import Game
from models.player import Player

logger = get_logger(__name__)


def play() -> None:
    player_1 = Player("Player 1")
    player_2 = Player("Player 2")
    game = Game(player_1, player_2)
    game.play_round()

    logger.info("Team 1 score: %s", game.team1_score)
    logger.info("Team 2 score: %s", game.team2_score)


play()
# %%
