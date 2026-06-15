from game.constants import (
    PLAYER_X,
    PLAYER_O,
    WIN_LENGTH,
    BOARD_SIZE,
    EMPTY
)

from game.game_state import GameState
from game.move import Move


class GameEngine:

    DIRECTIONS = [
        (1, 0),
        (0, 1),
        (1, 1),
        (1, -1)
    ]

    def __init__(self):
        self.state = GameState.create_new()

    def make_move(
        self,
        move: Move
    ) -> bool:

        return GameEngine.apply_move(
            self.state,
            move
        )

    @staticmethod
    def apply_move(
        state: GameState,
        move: Move
    ) -> bool:

        if state.game_over:
            return False

        success = state.board.place_piece(
            move.row,
            move.col,
            state.current_player
        )

        if not success:
            return False

        state.last_move = move

        if GameEngine.check_winner(
            state,
            move.row,
            move.col,
            state.current_player
        ):
            state.winner = state.current_player
            state.game_over = True
            return True

        if GameEngine.is_board_full(
            state
        ):
            state.game_over = True
            return True

        GameEngine.switch_player(
            state
        )

        return True

    @staticmethod
    def switch_player(
        state: GameState
    ):

        if state.current_player == PLAYER_X:
            state.current_player = PLAYER_O
        else:
            state.current_player = PLAYER_X

    @staticmethod
    def is_board_full(
        state: GameState
    ):

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):

                if (
                    state.board.get_cell(
                        row,
                        col
                    ) == EMPTY
                ):
                    return False

        return True

    @staticmethod
    def check_winner(
        state: GameState,
        row: int,
        col: int,
        player: int
    ) -> bool:

        for dr, dc in GameEngine.DIRECTIONS:

            count = 1

            count += GameEngine.count_direction(
                state,
                row,
                col,
                dr,
                dc,
                player
            )

            count += GameEngine.count_direction(
                state,
                row,
                col,
                -dr,
                -dc,
                player
            )

            if count >= WIN_LENGTH:
                return True

        return False

    @staticmethod
    def count_direction(
        state: GameState,
        row,
        col,
        dr,
        dc,
        player
    ):

        count = 0

        r = row + dr
        c = col + dc

        while (
            0 <= r < BOARD_SIZE
            and 0 <= c < BOARD_SIZE
            and state.board.get_cell(
                r,
                c
            ) == player
        ):
            count += 1
            r += dr
            c += dc

        return count