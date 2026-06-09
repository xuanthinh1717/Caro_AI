from ai.player_factory import create_player

from game.game_engine import GameEngine

class GameManager:

    def __init__(
        self,
        player_x_name,
        player_o_name
    ):

        self.engine = GameEngine()

        self.player_x = create_player(
            player_x_name
        )

        self.player_o = create_player(
            player_o_name
        )

    def current_player(self):

        if (
            self.engine.state.current_player
            == 1
        ):
            return self.player_x

        return self.player_o