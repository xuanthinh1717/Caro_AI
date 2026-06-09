import pygame

from game.constants import (
    BOARD_SIZE,
    EMPTY,
    PLAYER_X,
    PLAYER_O
)

CELL_SIZE = 40
MARGIN = 40

GRID_SIZE = BOARD_SIZE * CELL_SIZE

WINDOW_WIDTH = GRID_SIZE + MARGIN * 2

INFO_HEIGHT = 80

WINDOW_HEIGHT = (
    GRID_SIZE
    + MARGIN * 2
    + INFO_HEIGHT
)


class BoardView:

    def __init__(self, screen):

        self.screen = screen

        self.piece_font = pygame.font.SysFont(
            None,
            30
        )

        self.info_font = pygame.font.SysFont(
            None,
            28
        )

        self.small_font = pygame.font.SysFont(
            None,
            22
        )

    def draw_grid(self):

        self.screen.fill((240, 220, 170))

        for i in range(BOARD_SIZE + 1):

            pygame.draw.line(
                self.screen,
                (0, 0, 0),
                (MARGIN, MARGIN + i * CELL_SIZE),
                (MARGIN + GRID_SIZE,
                 MARGIN + i * CELL_SIZE)
            )

            pygame.draw.line(
                self.screen,
                (0, 0, 0),
                (MARGIN + i * CELL_SIZE, MARGIN),
                (MARGIN + i * CELL_SIZE,
                 MARGIN + GRID_SIZE)
            )

    def draw_last_move(self, last_move):

        if last_move is None:
            return

        rect = pygame.Rect(
            MARGIN + last_move.col * CELL_SIZE,
            MARGIN + last_move.row * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )

        pygame.draw.rect(
            self.screen,
            (255, 215, 0),
            rect,
            3
        )

    def draw_pieces(self, board):

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):

                value = board.get_cell(
                    row,
                    col
                )

                if value == EMPTY:
                    continue

                x = (
                    MARGIN
                    + col * CELL_SIZE
                    + CELL_SIZE // 2
                )

                y = (
                    MARGIN
                    + row * CELL_SIZE
                    + CELL_SIZE // 2
                )

                if value == PLAYER_X:

                    text = self.piece_font.render(
                        "X",
                        True,
                        (220, 50, 50)
                    )

                else:

                    text = self.piece_font.render(
                        "O",
                        True,
                        (50, 50, 220)
                    )

                rect = text.get_rect(
                    center=(x, y)
                )

                self.screen.blit(
                    text,
                    rect
                )

    def draw_hover(
        self,
        board,
        current_player,
        mouse_pos
    ):

        cell = self.mouse_to_cell(
            mouse_pos
        )

        if cell is None:
            return

        row, col = cell

        if not board.is_empty(
            row,
            col
        ):
            return

        x = (
            MARGIN
            + col * CELL_SIZE
            + CELL_SIZE // 2
        )

        y = (
            MARGIN
            + row * CELL_SIZE
            + CELL_SIZE // 2
        )

        symbol = "X"

        if current_player == PLAYER_O:
            symbol = "O"

        text = self.piece_font.render(
            symbol,
            True,
            (180, 180, 180)
        )

        rect = text.get_rect(
            center=(x, y)
        )

        self.screen.blit(
            text,
            rect
        )

    def draw_status(
        self,
        current_player,
        current_player_name,
        winner,
        game_over
    ):

        if game_over:

            if winner == PLAYER_X:
                status = "Winner: X"

            elif winner == PLAYER_O:
                status = "Winner: O"

            else:
                status = "Draw"

        else:

            symbol = "X"

            if current_player == PLAYER_O:
                symbol = "O"

            status = (
                f"Turn: "
                f"{current_player_name} "
                f"({symbol})"
            )

        text = self.info_font.render(
            status,
            True,
            (0, 0, 0)
        )

        self.screen.blit(
            text,
            (20, WINDOW_HEIGHT - 70)
        )

        help_text = self.small_font.render(
            "R = Restart   |   M = Menu",
            True,
            (60, 60, 60)
        )

        self.screen.blit(
            help_text,
            (20, WINDOW_HEIGHT - 35)
        )

    def render(
        self,
        board,
        current_player,
        current_player_name,
        winner,
        game_over,
        last_move=None,
        show_hover=True
    ):

        self.draw_grid()

        self.draw_last_move(
            last_move
        )

        self.draw_pieces(board)

        if show_hover:

            self.draw_hover(
                board,
                current_player,
                pygame.mouse.get_pos()
            )

        self.draw_status(
            current_player,
            current_player_name,
            winner,
            game_over
        )

    def mouse_to_cell(
        self,
        mouse_pos
    ):

        x, y = mouse_pos

        if (
            x < MARGIN
            or y < MARGIN
            or x >= MARGIN + GRID_SIZE
            or y >= MARGIN + GRID_SIZE
        ):
            return None

        col = int(
            (x - MARGIN)
            // CELL_SIZE
        )

        row = int(
            (y - MARGIN)
            // CELL_SIZE
        )

        return row, col