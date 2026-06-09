import pygame

from ai.loader import load_ai_players


class MenuScreen:

    def __init__(self, screen):

        self.screen = screen

        self.ai_players = load_ai_players()

        self.player_options = (
            ["Human"]
            + [ai.name for ai in self.ai_players]
        )

        self.player_x_index = 0
        self.player_o_index = 0

        self.font = pygame.font.SysFont(
            None,
            36
        )

        self.small_font = pygame.font.SysFont(
            None,
            28
        )

    def draw(self):

        self.screen.fill((240, 220, 170))

        title = self.font.render(
            "CARO AI",
            True,
            (0, 0, 0)
        )

        self.screen.blit(
            title,
            (250, 60)
        )

        self._draw_option(
            self.screen,
            "Player X",
            self.player_options[
                self.player_x_index
            ],
            150
        )

        self._draw_option(
            self.screen,
            "Player O",
            self.player_options[
                self.player_o_index
            ],
            250
        )

        start_text = self.font.render(
            "START",
            True,
            (255, 255, 255)
        )

        pygame.draw.rect(
            self.screen,
            (50, 120, 50),
            self.start_button_rect()
        )

        self.screen.blit(
            start_text,
            (
                self.start_button_rect().x + 40,
                self.start_button_rect().y + 10
            )
        )

    def _draw_option(
        self,
        screen,
        label,
        value,
        y
    ):

        text = self.small_font.render(
            f"{label}: {value}",
            True,
            (0, 0, 0)
        )

        self.screen.blit(
            text,
            (180, y)
        )

        left_rect = pygame.Rect(
            120,
            y,
            40,
            40
        )

        right_rect = pygame.Rect(
            500,
            y,
            40,
            40
        )

        pygame.draw.rect(
            screen,
            (180, 180, 180),
            left_rect
        )

        pygame.draw.rect(
            screen,
            (180, 180, 180),
            right_rect
        )

        self.screen.blit(
            self.small_font.render(
                "<",
                True,
                (0, 0, 0)
            ),
            (132, y + 5)
        )

        self.screen.blit(
            self.small_font.render(
                ">",
                True,
                (0, 0, 0)
            ),
            (512, y + 5)
        )

    def start_button_rect(self):

        return pygame.Rect(
            250,
            380,
            150,
            60
        )

    def handle_event(
        self,
        event
    ):

        if event.type != pygame.MOUSEBUTTONDOWN:
            return None

        x, y = event.pos

        # Player X

        if (
            120 <= x <= 160
            and 150 <= y <= 190
        ):

            self.player_x_index = (
                self.player_x_index - 1
            ) % len(self.player_options)

        elif (
            500 <= x <= 540
            and 150 <= y <= 190
        ):

            self.player_x_index = (
                self.player_x_index + 1
            ) % len(self.player_options)

        # Player O

        elif (
            120 <= x <= 160
            and 250 <= y <= 290
        ):

            self.player_o_index = (
                self.player_o_index - 1
            ) % len(self.player_options)

        elif (
            500 <= x <= 540
            and 250 <= y <= 290
        ):

            self.player_o_index = (
                self.player_o_index + 1
            ) % len(self.player_options)

        elif self.start_button_rect().collidepoint(
            event.pos
        ):

            return {
                "player_x":
                    self.player_options[
                        self.player_x_index
                    ],

                "player_o":
                    self.player_options[
                        self.player_o_index
                    ]
            }

        return None