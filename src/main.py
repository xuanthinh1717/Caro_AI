import time
import pygame

from game.move import Move
from game.game_manager import GameManager

from ui.board_view import (
    BoardView,
    WINDOW_WIDTH,
    WINDOW_HEIGHT
)
from ui.menu_screen import MenuScreen


MENU = 0
GAME = 1

AI_MOVE_DELAY = 0.3


def main():

    pygame.init()

    screen = pygame.display.set_mode(
        (
            WINDOW_WIDTH,
            WINDOW_HEIGHT
        )
    )

    pygame.display.set_caption(
        "Caro AI"
    )

    menu = MenuScreen(screen)

    board_view = BoardView(screen)

    manager = None

    player_x_name = None
    player_o_name = None

    current_screen = MENU

    last_ai_move_time = 0

    clock = pygame.time.Clock()

    running = True

    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            # ==================
            # MENU
            # ==================

            if current_screen == MENU:

                result = menu.handle_event(
                    event
                )

                if result:

                    player_x_name = result[
                        "player_x"
                    ]

                    player_o_name = result[
                        "player_o"
                    ]

                    manager = GameManager(
                        player_x_name,
                        player_o_name
                    )

                    current_screen = GAME

            # ==================
            # GAME
            # ==================

            elif current_screen == GAME:

                # Restart / Menu

                if (
                    event.type
                    == pygame.KEYDOWN
                ):

                    if event.key == pygame.K_r:

                        manager = GameManager(
                            player_x_name,
                            player_o_name
                        )

                        last_ai_move_time = 0

                    elif event.key == pygame.K_m:

                        current_screen = MENU

                current_player = (
                    manager.current_player()
                )

                if (
                    current_player.is_human
                    and event.type
                    == pygame.MOUSEBUTTONDOWN
                    and not manager.engine.state.game_over
                ):

                    cell = board_view.mouse_to_cell(
                        event.pos
                    )

                    if cell:

                        row, col = cell

                        manager.engine.make_move(
                            Move(row, col)
                        )

        # ==================
        # GAME UPDATE
        # ==================

        if (
            current_screen == GAME
            and not manager.engine.state.game_over
        ):

            current_player = (
                manager.current_player()
            )

            if not current_player.is_human:

                current_time = time.time()

                if (
                    current_time
                    - last_ai_move_time
                    >= AI_MOVE_DELAY
                ):

                    move = current_player.choose_move(
                        manager.engine.state.clone()
                    )

                    manager.engine.make_move(
                        move
                    )

                    last_ai_move_time = (
                        current_time
                    )

        # ==================
        # RENDER
        # ==================

        if current_screen == MENU:

            menu.draw()

        elif current_screen == GAME:

            current_player = (
                manager.current_player()
            )

            board_view.render(
                manager.engine.state.board,
                manager.engine.state.current_player,
                current_player.name,
                manager.engine.state.winner,
                manager.engine.state.game_over,
                getattr(
                    manager.engine,
                    "last_move",
                    None
                ),
                current_player.is_human
            )

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()