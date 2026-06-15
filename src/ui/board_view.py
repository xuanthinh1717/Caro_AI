import pygame
import math
import time

from game.constants import (
    BOARD_SIZE,
    EMPTY,
    PLAYER_X,
    PLAYER_O
)

CELL_SIZE = 40
MARGIN = 40

GRID_SIZE = BOARD_SIZE * CELL_SIZE

# Modern Desktop Layout: 600px Board + 240px Sidebar + Spacing margins
WINDOW_WIDTH = GRID_SIZE + MARGIN * 3 + 240 # 40 + 600 + 40 + 240 + 40 = 960

WINDOW_HEIGHT = GRID_SIZE + MARGIN * 2 # 40 + 600 + 40 = 680


class BoardView:

    def __init__(self, screen):

        self.screen = screen

        # Define modern fonts using standard system fonts
        self.piece_font = pygame.font.SysFont("segoeui,arial,helvetica", 28, bold=True)
        self.info_font = pygame.font.SysFont("segoeui,arial,helvetica", 24, bold=True)
        self.button_font = pygame.font.SysFont("segoeui,arial,helvetica", 16, bold=True)
        self.small_font = pygame.font.SysFont("segoeui,arial,helvetica", 14, bold=True)
        
        # Modal specific fonts
        self.modal_title_font = pygame.font.SysFont("segoeui,arial,helvetica", 32, bold=True)
        self.modal_text_font = pygame.font.SysFont("segoeui,arial,helvetica", 20, bold=False)

        ww, wh = self.screen.get_size()
        
        # Sidebar coordinates (x starts after board + middle margin)
        self.sidebar_rect = pygame.Rect(GRID_SIZE + MARGIN * 2, MARGIN, 240, GRID_SIZE)
        
        # Sidebar control buttons
        self.btn_restart = pygame.Rect(self.sidebar_rect.x + 15, self.sidebar_rect.bottom - 110, 210, 45)
        self.btn_menu = pygame.Rect(self.sidebar_rect.x + 15, self.sidebar_rect.bottom - 55, 210, 45)
        
        # Modal coordinates
        self.modal_rect = pygame.Rect(ww // 2 - 210, wh // 2 - 130, 420, 260)
        self.btn_modal_restart = pygame.Rect(ww // 2 - 175, wh // 2 + 50, 150, 45)
        self.btn_modal_menu = pygame.Rect(ww // 2 + 25, wh // 2 + 50, 150, 45)

    def draw_grid(self):
        # Draw a beautiful solid background for the board area
        board_rect = pygame.Rect(
            MARGIN - 8,
            MARGIN - 8,
            GRID_SIZE + 16,
            GRID_SIZE + 16
        )
        # Fill board background
        pygame.draw.rect(self.screen, (32, 38, 48), board_rect, border_radius=12)
        # Draw border outline
        pygame.draw.rect(self.screen, (51, 65, 85), board_rect, width=2, border_radius=12)

        # Draw grid lines
        for i in range(BOARD_SIZE + 1):
            pygame.draw.line(
                self.screen,
                (50, 60, 75),
                (MARGIN, MARGIN + i * CELL_SIZE),
                (MARGIN + GRID_SIZE, MARGIN + i * CELL_SIZE),
                1
            )

            pygame.draw.line(
                self.screen,
                (50, 60, 75),
                (MARGIN + i * CELL_SIZE, MARGIN),
                (MARGIN + i * CELL_SIZE, MARGIN + GRID_SIZE),
                1
            )

    def draw_last_move(self, last_move):
        if last_move is None:
            return

        # Draw a semi-transparent gold background highlight
        gold_surf = pygame.Surface((CELL_SIZE - 2, CELL_SIZE - 2), pygame.SRCALPHA)
        gold_surf.fill((250, 204, 21, 60)) # Alpha 60
        self.screen.blit(
            gold_surf,
            (
                MARGIN + last_move.col * CELL_SIZE + 1,
                MARGIN + last_move.row * CELL_SIZE + 1
            )
        )

        # Draw gold border highlight
        rect = pygame.Rect(
            MARGIN + last_move.col * CELL_SIZE,
            MARGIN + last_move.row * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )
        pygame.draw.rect(
            self.screen,
            (250, 204, 21),
            rect,
            2
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

                cx = (
                    MARGIN
                    + col * CELL_SIZE
                    + CELL_SIZE // 2
                )

                cy = (
                    MARGIN
                    + row * CELL_SIZE
                    + CELL_SIZE // 2
                )

                if value == PLAYER_X:
                    offset = 10
                    # Diagonal 1
                    pygame.draw.line(
                        self.screen,
                        (244, 63, 94),
                        (cx - CELL_SIZE // 2 + offset, cy - CELL_SIZE // 2 + offset),
                        (cx + CELL_SIZE // 2 - offset, cy + CELL_SIZE // 2 - offset),
                        5
                    )
                    # Diagonal 2
                    pygame.draw.line(
                        self.screen,
                        (244, 63, 94),
                        (cx + CELL_SIZE // 2 - offset, cy - CELL_SIZE // 2 + offset),
                        (cx - CELL_SIZE // 2 + offset, cy + CELL_SIZE // 2 - offset),
                        5
                    )
                else:
                    radius = CELL_SIZE // 2 - 8
                    pygame.draw.circle(
                        self.screen,
                        (6, 182, 212),
                        (cx, cy),
                        radius,
                        5
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

        cx = (
            MARGIN
            + col * CELL_SIZE
            + CELL_SIZE // 2
        )

        cy = (
            MARGIN
            + row * CELL_SIZE
            + CELL_SIZE // 2
        )

        hover_color = (100, 116, 139) # Muted slate for hover preview
        offset = 10
        radius = CELL_SIZE // 2 - 8

        if current_player == PLAYER_X:
            # Diagonal 1
            pygame.draw.line(
                self.screen,
                hover_color,
                (cx - CELL_SIZE // 2 + offset, cy - CELL_SIZE // 2 + offset),
                (cx + CELL_SIZE // 2 - offset, cy + CELL_SIZE // 2 - offset),
                2
            )
            # Diagonal 2
            pygame.draw.line(
                self.screen,
                hover_color,
                (cx + CELL_SIZE // 2 - offset, cy - CELL_SIZE // 2 + offset),
                (cx - CELL_SIZE // 2 + offset, cy + CELL_SIZE // 2 - offset),
                2
            )
        else:
            pygame.draw.circle(
                self.screen,
                hover_color,
                (cx, cy),
                radius,
                2
            )

    def draw_button(self, rect, text, bg_color, text_color):
        # Draw background with rounded corners
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
        # Draw outline
        pygame.draw.rect(self.screen, (148, 163, 184), rect, width=1, border_radius=8)
        
        # Render text
        text_surf = self.button_font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def draw_sidebar(
        self,
        current_player,
        current_player_name,
        winner,
        game_over,
        player_x_name,
        player_o_name
    ):
        # Fill sidebar area background
        pygame.draw.rect(self.screen, (30, 41, 59), self.sidebar_rect, border_radius=12)
        # Sidebar border
        pygame.draw.rect(self.screen, (51, 65, 85), self.sidebar_rect, width=2, border_radius=12)
        
        # 1. Main Title
        title_surf = self.piece_font.render("GOMOKU AI", True, (240, 243, 246))
        title_rect = title_surf.get_rect(center=(self.sidebar_rect.centerx, 75))
        self.screen.blit(title_surf, title_rect)
        
        # Decor line
        pygame.draw.line(
            self.screen, 
            (51, 65, 85), 
            (self.sidebar_rect.x + 20, 105), 
            (self.sidebar_rect.right - 20, 105), 
            2
        )
        
        # Get mouse position for button hover
        mouse_pos = pygame.mouse.get_pos()
        
        # 2. Player X Card
        card_x = pygame.Rect(self.sidebar_rect.x + 15, 120, 210, 85)
        is_x_turn = (not game_over and current_player == PLAYER_X)
        card_x_border_color = (244, 63, 94) if is_x_turn else (51, 65, 85)
        card_x_border_width = 3 if is_x_turn else 1
        
        pygame.draw.rect(self.screen, (15, 23, 42), card_x, border_radius=8)
        pygame.draw.rect(self.screen, card_x_border_color, card_x, width=card_x_border_width, border_radius=8)
        
        lbl_x = self.small_font.render("PLAYER X", True, (244, 63, 94))
        self.screen.blit(lbl_x, (card_x.x + 15, card_x.y + 12))
        
        name_x = self.button_font.render(player_x_name, True, (240, 243, 246))
        self.screen.blit(name_x, (card_x.x + 15, card_x.y + 35))
        
        # Draw a mini X indicator
        pygame.draw.line(self.screen, (244, 63, 94), (card_x.right - 35, card_x.y + 32), (card_x.right - 20, card_x.y + 47), 3)
        pygame.draw.line(self.screen, (244, 63, 94), (card_x.right - 20, card_x.y + 32), (card_x.right - 35, card_x.y + 47), 3)
        
        # 3. Player O Card
        card_o = pygame.Rect(self.sidebar_rect.x + 15, 220, 210, 85)
        is_o_turn = (not game_over and current_player == PLAYER_O)
        card_o_border_color = (6, 182, 212) if is_o_turn else (51, 65, 85)
        card_o_border_width = 3 if is_o_turn else 1
        
        pygame.draw.rect(self.screen, (15, 23, 42), card_o, border_radius=8)
        pygame.draw.rect(self.screen, card_o_border_color, card_o, width=card_o_border_width, border_radius=8)
        
        lbl_o = self.small_font.render("PLAYER O", True, (6, 182, 212))
        self.screen.blit(lbl_o, (card_o.x + 15, card_o.y + 12))
        
        name_o = self.button_font.render(player_o_name, True, (240, 243, 246))
        self.screen.blit(name_o, (card_o.x + 15, card_o.y + 35))
        
        # Draw a mini O indicator
        pygame.draw.circle(self.screen, (6, 182, 212), (card_o.right - 27, card_o.y + 40), 9, 3)
        
        # 4. Current status / AI thinking
        status_card = pygame.Rect(self.sidebar_rect.x + 15, 320, 210, 140)
        pygame.draw.rect(self.screen, (15, 23, 42), status_card, border_radius=8)
        pygame.draw.rect(self.screen, (51, 65, 85), status_card, width=1, border_radius=8)
        
        if not game_over:
            # Check if current player is AI (starts with AI name or is not "Human")
            is_ai = ("AI" in current_player_name or current_player_name != "Human")
            
            lbl_status = self.small_font.render("TRẠNG THÁI", True, (148, 163, 184))
            self.screen.blit(lbl_status, (status_card.x + 15, status_card.y + 12))
            
            if is_ai:
                thinking_surf = self.button_font.render("AI đang tính toán...", True, (234, 179, 8))
                self.screen.blit(thinking_surf, (status_card.x + 15, status_card.y + 40))
                
                # Concentric pulsing loading circles
                t = time.time()
                pulse = 10 + 3 * math.sin(t * 8)
                color = (6, 182, 212) if current_player == PLAYER_O else (244, 63, 94)
                
                dot_cx = status_card.centerx
                dot_cy = status_card.y + 95
                
                for r in range(3, 0, -1):
                    alpha_val = int(50 / r)
                    glow_surf = pygame.Surface((pulse * r * 2, pulse * r * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, color + (alpha_val,), (int(pulse * r), int(pulse * r)), int(pulse * r))
                    self.screen.blit(glow_surf, (int(dot_cx - pulse * r), int(dot_cy - pulse * r)))
            else:
                your_turn_surf = self.button_font.render("Đến lượt bạn!", True, (34, 197, 94))
                self.screen.blit(your_turn_surf, (status_card.x + 15, status_card.y + 40))
                
                prompt_surf = self.small_font.render("Chọn ô trên bàn cờ...", True, (148, 163, 184))
                self.screen.blit(prompt_surf, (status_card.x + 15, status_card.y + 70))
        else:
            lbl_status = self.small_font.render("TRẬN ĐẤU KẾT THÚC", True, (148, 163, 184))
            self.screen.blit(lbl_status, (status_card.x + 15, status_card.y + 12))
            
            end_msg = "Hòa cuộc!"
            end_color = (148, 163, 184)
            if winner == PLAYER_X:
                end_msg = "Player X Thắng!"
                end_color = (244, 63, 94)
            elif winner == PLAYER_O:
                end_msg = "Player O Thắng!"
                end_color = (6, 182, 212)
                
            end_surf = self.info_font.render(end_msg, True, end_color)
            self.screen.blit(end_surf, (status_card.x + 15, status_card.y + 45))

        # 5. Control Buttons
        restart_hover = self.btn_restart.collidepoint(mouse_pos)
        restart_color = (74, 222, 128) if restart_hover else (34, 197, 94)
        self.draw_button(self.btn_restart, "Chơi lại", restart_color, (255, 255, 255))

        menu_hover = self.btn_menu.collidepoint(mouse_pos)
        menu_color = (100, 116, 139) if menu_hover else (71, 85, 105)
        self.draw_button(self.btn_menu, "Quay lại Menu", menu_color, (255, 255, 255))

    def draw_status(self, current_player, current_player_name, winner, game_over):
        # Keep for backward compatibility if called elsewhere, but empty since we use draw_sidebar
        pass

    def draw_victory_modal(self, winner, player_x_name, player_o_name):
        ww, wh = self.screen.get_size()
        
        # 1. Semi-transparent dark background overlay
        overlay = pygame.Surface((ww, wh), pygame.SRCALPHA)
        overlay.fill((15, 23, 42, 210)) # Dark slate with alpha 210
        self.screen.blit(overlay, (0, 0))
        
        # 2. Draw modal dialog box
        pygame.draw.rect(self.screen, (15, 23, 42), self.modal_rect.inflate(8, 8), border_radius=16) # Shadow
        pygame.draw.rect(self.screen, (30, 41, 59), self.modal_rect, border_radius=16) # Modal body
        pygame.draw.rect(self.screen, (71, 85, 105), self.modal_rect, width=2, border_radius=16) # Border
        
        # 3. Draw content texts
        if winner == PLAYER_X:
            title_text = "CHIẾN THẮNG!"
            title_color = (244, 63, 94) # Pink/Red
            msg_text = f"Người chơi X ({player_x_name}) đã thắng!"
        elif winner == PLAYER_O:
            title_text = "CHIẾN THẮNG!"
            title_color = (6, 182, 212) # Blue
            msg_text = f"Người chơi O ({player_o_name}) đã thắng!"
        else:
            title_text = "HÒA NHAU!"
            title_color = (148, 163, 184) # Gray
            msg_text = "Trận đấu kết thúc với tỷ số hòa!"
            
        # Modal Title
        title_surf = self.modal_title_font.render(title_text, True, title_color)
        title_rect = title_surf.get_rect(center=(self.modal_rect.centerx, self.modal_rect.y + 45))
        self.screen.blit(title_surf, title_rect)
        
        # Modal Message
        msg_surf = self.modal_text_font.render(msg_text, True, (240, 243, 246))
        msg_rect = msg_surf.get_rect(center=(self.modal_rect.centerx, self.modal_rect.y + 105))
        self.screen.blit(msg_surf, msg_rect)
        
        # Instruction helper
        helper_surf = self.small_font.render("Bấm một nút bên dưới để tiếp tục", True, (148, 163, 184))
        helper_rect = helper_surf.get_rect(center=(self.modal_rect.centerx, self.modal_rect.y + 145))
        self.screen.blit(helper_surf, helper_rect)
        
        # 4. Draw interactive buttons inside modal
        mouse_pos = pygame.mouse.get_pos()
        
        # Modal Restart button
        restart_hover = self.btn_modal_restart.collidepoint(mouse_pos)
        restart_color = (74, 222, 128) if restart_hover else (34, 197, 94)
        self.draw_button(self.btn_modal_restart, "Chơi lại", restart_color, (255, 255, 255))
        
        # Modal Menu button
        menu_hover = self.btn_modal_menu.collidepoint(mouse_pos)
        menu_color = (100, 116, 139) if menu_hover else (71, 85, 105)
        self.draw_button(self.btn_modal_menu, "Về Menu", menu_color, (255, 255, 255))

    def render(
        self,
        board,
        current_player,
        current_player_name,
        winner,
        game_over,
        last_move=None,
        show_hover=True,
        player_x_name="X",
        player_o_name="O"
    ):
        # Fill background (Sleek dark theme)
        self.screen.fill((24, 28, 36))

        # Draw board grid
        self.draw_grid()

        # Highlight last move
        self.draw_last_move(
            last_move
        )

        # Draw placed pieces
        self.draw_pieces(board)

        # Draw hover preview of current player's piece
        if show_hover and not game_over:
            self.draw_hover(
                board,
                current_player,
                pygame.mouse.get_pos()
            )

        # Draw right sidebar
        self.draw_sidebar(
            current_player,
            current_player_name,
            winner,
            game_over,
            player_x_name,
            player_o_name
        )

        # Draw victory modal overlay if game is over
        if game_over:
            self.draw_victory_modal(
                winner,
                player_x_name,
                player_o_name
            )

    def handle_event(self, event, game_over):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return None

        # Check hits when game is over (Modal buttons)
        if game_over:
            if self.btn_modal_restart.collidepoint(event.pos):
                return "restart"
            elif self.btn_modal_menu.collidepoint(event.pos):
                return "menu"
        # Check hits when game is active (Sidebar buttons)
        else:
            if self.btn_restart.collidepoint(event.pos):
                return "restart"
            elif self.btn_menu.collidepoint(event.pos):
                return "menu"

        return None

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