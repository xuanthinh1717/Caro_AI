import random

from ai.base import AIPlayer
from game.move import Move
from game.constants import (
    BOARD_SIZE,
    EMPTY
)


class RandomAI(AIPlayer):

    @property
    def name(self):
        return "Random AI"

    def choose_move(self, state):

        moves = []

        board = state.board

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):

                if board.get_cell(
                    row,
                    col
                ) == EMPTY:

                    moves.append(
                        Move(row, col)
                    )

        return random.choice(moves)