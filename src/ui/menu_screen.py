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

        # Define modern fonts
        self.title_font = pygame.font.SysFont("segoeui,arial,helvetica", 48, bold=True)
        self.subtitle_font = pygame.font.SysFont("segoeui,arial,helvetica", 18, italic=True)
        self.card_label_font = pygame.font.SysFont("segoeui,arial,helvetica", 16, bold=True)
        self.card_value_font = pygame.font.SysFont("segoeui,arial,helvetica", 24, bold=True)
        self.btn_font = pygame.font.SysFont("segoeui,arial,helvetica", 22, bold=True)
        self.start_font = pygame.font.SysFont("segoeui,arial,helvetica", 28, bold=True)
        self.small_font = pygame.font.SysFont("segoeui,arial,helvetica", 12, bold=True)

        # Define layout rects dynamically
        ww, wh = self.screen.get_size()
        
        # Player X Card: y=180, height=100
        self.card_x_rect = pygame.Rect(ww // 2 - 230, 180, 460, 100)
        self.btn_x_left = pygame.Rect(ww // 2 - 210, 210, 40, 40)
        self.btn_x_right = pygame.Rect(ww // 2 + 170, 210, 40, 40)
        
        # Player O Card: y=310, height=100
        self.card_o_rect = pygame.Rect(ww // 2 - 230, 310, 460, 100)
        self.btn_o_left = pygame.Rect(ww // 2 - 210, 340, 40, 40)
        self.btn_o_right = pygame.Rect(ww // 2 + 170, 340, 40, 40)
        
        # Start button: y=460, width=200, height=60
        self.btn_start = pygame.Rect(ww // 2 - 100, 460, 200, 60)

    def draw(self):
        ww, wh = self.screen.get_size()
        
        # Fill background (Sleek dark theme)
        self.screen.fill((24, 28, 36))
        
        # Title "CARO AI" with room for icon
        title_text = self.title_font.render("CARO AI", True, (240, 243, 246))
        title_rect = title_text.get_rect(center=(ww // 2 + 25, 80))
        self.screen.blit(title_text, title_rect)
        
        # Decorative grid icon
        icon_x = title_rect.x - 55
        icon_y = title_rect.y + 5
        icon_size = 40
        for i in (13, 27):
            # Vertical lines
            pygame.draw.line(self.screen, (34, 197, 94), (icon_x + i, icon_y), (icon_x + i, icon_y + icon_size), 3)
            # Horizontal lines
            pygame.draw.line(self.screen, (34, 197, 94), (icon_x, icon_y + i), (icon_x + icon_size, icon_y + i), 3)
        
        # Subtitle
        sub_text = self.subtitle_font.render("Chọn chế độ chơi để bắt đầu", True, (148, 163, 184))
        sub_rect = sub_text.get_rect(center=(ww // 2, 130))
        self.screen.blit(sub_text, sub_rect)
        
        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw Player X card
        self._draw_player_card(
            "PLAYER X (Đi trước)",
            self.player_options[self.player_x_index],
            self.card_x_rect,
            self.btn_x_left,
            self.btn_x_right,
            (239, 68, 68), # Red accent
            mouse_pos
        )
        
        # Draw Player O card
        self._draw_player_card(
            "PLAYER O",
            self.player_options[self.player_o_index],
            self.card_o_rect,
            self.btn_o_left,
            self.btn_o_right,
            (59, 130, 246), # Blue accent
            mouse_pos
        )
        
        # Draw Start Button
        start_hover = self.btn_start.collidepoint(mouse_pos)
        start_color = (74, 222, 128) if start_hover else (34, 197, 94)
        
        # Draw shadow
        shadow_rect = self.btn_start.move(2, 2)
        pygame.draw.rect(self.screen, (15, 23, 42), shadow_rect, border_radius=15)
        
        # Draw main start button
        pygame.draw.rect(self.screen, start_color, self.btn_start, border_radius=15)
        
        start_text = self.start_font.render("BẮT ĐẦU", True, (255, 255, 255))
        start_text_rect = start_text.get_rect(center=self.btn_start.center)
        self.screen.blit(start_text, start_text_rect)

    def _draw_player_card(
        self,
        label,
        value,
        card_rect,
        btn_left,
        btn_right,
        accent_color,
        mouse_pos
    ):
        # Card background
        pygame.draw.rect(self.screen, (30, 41, 59), card_rect, border_radius=12)
        
        # Highlight border
        pygame.draw.rect(self.screen, (51, 65, 85), card_rect, width=2, border_radius=12)
        
        # Determine player type label
        is_human = (value == "Human")
        type_text = "[NGƯỜI CHƠI]" if is_human else "[TRÍ TUỆ NHÂN TẠO]"
        type_color = (34, 197, 94) if is_human else (234, 179, 8)
        
        # Label (e.g. PLAYER X)
        lbl_surf = self.card_label_font.render(label, True, accent_color)
        lbl_rect = lbl_surf.get_rect(center=(card_rect.centerx, card_rect.y + 22))
        self.screen.blit(lbl_surf, lbl_rect)
        
        # Player type status label
        type_surf = self.small_font.render(type_text, True, type_color)
        type_rect = type_surf.get_rect(center=(card_rect.centerx, card_rect.y + 45))
        self.screen.blit(type_surf, type_rect)
        
        # Value (e.g. Human)
        val_surf = self.card_value_font.render(value, True, (240, 243, 246))
        val_rect = val_surf.get_rect(center=(card_rect.centerx, card_rect.y + 72))
        self.screen.blit(val_surf, val_rect)
        
        # Left button `<`
        l_hover = btn_left.collidepoint(mouse_pos)
        l_color = (71, 85, 105) if l_hover else (51, 65, 85)
        pygame.draw.rect(self.screen, l_color, btn_left, border_radius=8)
        l_text = self.btn_font.render("<", True, (240, 243, 246))
        l_text_rect = l_text.get_rect(center=btn_left.center)
        self.screen.blit(l_text, l_text_rect)
        
        # Right button `>`
        r_hover = btn_right.collidepoint(mouse_pos)
        r_color = (71, 85, 105) if r_hover else (51, 65, 85)
        pygame.draw.rect(self.screen, r_color, btn_right, border_radius=8)
        r_text = self.btn_font.render(">", True, (240, 243, 246))
        r_text_rect = r_text.get_rect(center=btn_right.center)
        self.screen.blit(r_text, r_text_rect)

    def start_button_rect(self):
        return self.btn_start

    def handle_event(
        self,
        event
    ):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return None

        # Player X Selection
        if self.btn_x_left.collidepoint(event.pos):
            self.player_x_index = (
                self.player_x_index - 1
            ) % len(self.player_options)
            return None
        elif self.btn_x_right.collidepoint(event.pos):
            self.player_x_index = (
                self.player_x_index + 1
            ) % len(self.player_options)
            return None

        # Player O Selection
        elif self.btn_o_left.collidepoint(event.pos):
            self.player_o_index = (
                self.player_o_index - 1
            ) % len(self.player_options)
            return None
        elif self.btn_o_right.collidepoint(event.pos):
            self.player_o_index = (
                self.player_o_index + 1
            ) % len(self.player_options)
            return None

        # Start Button
        elif self.btn_start.collidepoint(event.pos):
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