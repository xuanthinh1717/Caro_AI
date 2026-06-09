from game.constants import BOARD_SIZE, EMPTY


class Board:

    def __init__(self):
        self.grid = [
            [EMPTY for _ in range(BOARD_SIZE)]
            for _ in range(BOARD_SIZE)
        ]

    def is_valid_position(self, row: int, col: int) -> bool:
        return (
            0 <= row < BOARD_SIZE
            and 0 <= col < BOARD_SIZE
        )

    def is_empty(self, row: int, col: int) -> bool:
        return self.grid[row][col] == EMPTY

    def place_piece(
        self,
        row: int,
        col: int,
        player: int
    ) -> bool:

        if not self.is_valid_position(row, col):
            return False

        if not self.is_empty(row, col):
            return False

        self.grid[row][col] = player
        return True

    def get_cell(self, row: int, col: int) -> int:
        return self.grid[row][col]

    def reset(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                self.grid[row][col] = EMPTY

    def clone(self):
        new_board = Board()

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                new_board.grid[row][col] = self.grid[row][col]

        return new_board
    def get_grid(self):
        return [row[:] for row in self.grid]