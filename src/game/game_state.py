from dataclasses import dataclass

from game.board import Board
from game.constants import (
    BOARD_SIZE,
    EMPTY,
    PLAYER_X,
    PLAYER_O
)
from game.move import Move


@dataclass
class GameState:
    board: Board
    current_player: int
    winner: int | None
    game_over: bool
    last_move: Move | None

    @classmethod
    def create_new(cls):
        return cls(
            board=Board(),
            current_player=PLAYER_X,
            winner=None,
            game_over=False,
            last_move=None
        )

    def clone(self):
        return GameState(
            board=self.board.clone(),
            current_player=self.current_player,
            winner=self.winner,
            game_over=self.game_over,
            last_move=self.last_move
        )

    def get_cell(
        self,
        row: int,
        col: int
    ):
        return self.board.get_cell(
            row,
            col
        )

    def get_grid(self):
        return self.board.get_grid()

    def get_valid_moves(self):

        moves = []

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):

                if (
                    self.board.get_cell(
                        row,
                        col
                    ) == EMPTY
                ):
                    moves.append(
                        Move(
                            row,
                            col
                        )
                    )

        return moves

    def get_candidate_moves(
        self,
        distance: int = 2
    ):

        # Bàn cờ rỗng -> cho phép đi mọi ô
        if self.piece_count() == 0:
            return self.get_valid_moves()

        candidates = set()

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):

                if (
                    self.board.get_cell(
                        row,
                        col
                    ) == EMPTY
                ):
                    continue

                for dr in range(
                    -distance,
                    distance + 1
                ):
                    for dc in range(
                        -distance,
                        distance + 1
                    ):

                        r = row + dr
                        c = col + dc

                        if (
                            0 <= r < BOARD_SIZE
                            and 0 <= c < BOARD_SIZE
                            and self.board.get_cell(
                                r,
                                c
                            ) == EMPTY
                        ):
                            candidates.add(
                                (
                                    r,
                                    c
                                )
                            )

        return [
            Move(row, col)
            for row, col in candidates
        ]

    def get_opponent(self):

        if self.current_player == PLAYER_X:
            return PLAYER_O

        return PLAYER_X

    def piece_count(self):

        count = 0

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):

                if (
                    self.board.get_cell(
                        row,
                        col
                    ) != EMPTY
                ):
                    count += 1

        return count

    def is_terminal(self):
        return self.game_over

    def simulate_move(
        self,
        move: Move
    ):
        from game.game_engine import GameEngine

        new_state = self.clone()

        GameEngine.apply_move(
            new_state,
            move
        )

        return new_state