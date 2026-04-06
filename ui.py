import pygame
from constants import *

class UI:
    def __init__(self):
        self.grid_spacing_x = GRID_SPACING_X
        self.grid_spacing_y = GRID_SPACING_Y
        self.start_x = PADDING_X
        self.start_y = PADDING_Y
        self.stone_radius = STONE_RADIUS
        self.star_points = [(2, 2), (2, 6), (4, 4), (6, 2), (6, 6)]

        try:
            self.font_title = pygame.font.Font(None, 32)
            self.font_score = pygame.font.Font(None, 48)
            self.font_label = pygame.font.Font(None, 24)
        except:
            default_font = pygame.font.get_default_font()
            self.font_title = pygame.font.Font(default_font, 32)
            self.font_score = pygame.font.Font(default_font, 48)
            self.font_label = pygame.font.Font(default_font, 24)

    def _grid_to_pixel(self, row, col):
        x = self.start_x + col * self.grid_spacing_x
        y = self.start_y + row * self.grid_spacing_y
        return int(x), int(y)

    def draw_board(self, surface):
        surface.fill(BOARD_COLOR)

        for i in range(GRID_DIM):
            x = self.start_x + i * self.grid_spacing_x
            pygame.draw.line(surface, LINE_COLOR, (x, self.start_y), (x, self.start_y + (GRID_DIM - 1) * self.grid_spacing_y), 1)

        for i in range(GRID_DIM):
            y = self.start_y + i * self.grid_spacing_y
            pygame.draw.line(surface, LINE_COLOR, (self.start_x, y), (self.start_x + (GRID_DIM - 1) * self.grid_spacing_x, y), 1)

        for row, col in self.star_points:
            center = self._grid_to_pixel(row, col)
            pygame.draw.circle(surface, STAR_POINT_COLOR, center, STAR_POINT_RADIUS)

    def draw_stones(self, surface, board_grid, last_move):
        for row in range(GRID_DIM):
            for col in range(GRID_DIM):
                stone = board_grid[row][col]
                if stone == EMPTY:
                    continue

                center = self._grid_to_pixel(row, col)

                if stone == BLACK_STONE:
                    pygame.draw.circle(surface, BLACK, center, self.stone_radius)
                elif stone == WHITE_STONE:
                    pygame.draw.circle(surface, WHITE, center, self.stone_radius)
                    pygame.draw.circle(surface, BLACK, center, self.stone_radius, 1)

                if (row, col) == last_move:
                    pygame.draw.circle(surface, LAST_MOVE_MARKER_COLOR, center, LAST_MOVE_MARKER_RADIUS)

    def convert_mouse_to_grid(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        col = round((mouse_x - self.start_x) / self.grid_spacing_x)
        row = round((mouse_y - self.start_y) / self.grid_spacing_y)

        if 0 <= row < GRID_DIM and 0 <= col < GRID_DIM:
            return int(row), int(col)
        return None, None

    def draw_hover_highlight(self, surface, hover_pos):
        if not hover_pos:
            return
        row, col = hover_pos
        center = self._grid_to_pixel(row, col)
        pygame.draw.circle(surface, HIGHLIGHT_COLOR, center, self.stone_radius, 2)

    def draw_score_panel(self, surface, captures, current_turn):
        panel_x_start = BOARD_WIDTH
        panel_width = WINDOW_WIDTH - BOARD_WIDTH
        panel_center_x = panel_x_start + (panel_width // 2)

        draw_text(surface, "CURRENT TURN", self.font_title, MENU_TEXT_COLOR, (panel_center_x, 40))
        
        turn_color = BLACK if current_turn == BLACK_STONE else WHITE
        stone_center = (panel_center_x, 80)
        pygame.draw.circle(surface, turn_color, stone_center, 20)
        if current_turn == WHITE_STONE:
            pygame.draw.circle(surface, BLACK, stone_center, 20, 2)

        line_y = 150
        pygame.draw.line(surface, MENU_BUTTON_COLOR, (panel_x_start + 20, line_y), (WINDOW_WIDTH - 20, line_y), 2)

        draw_text(surface, "BLACK PLAYER", self.font_title, MENU_TEXT_COLOR, (panel_center_x, 170))
        pygame.draw.circle(surface, BLACK, (panel_center_x, 210), 12)
        draw_text(surface, "Captures:", self.font_label, MENU_TEXT_COLOR, (panel_center_x, 245))
        # Sử dụng get(key, 0) để tránh lỗi nếu key chưa khởi tạo trong dict
        draw_text(surface, str(captures.get(BLACK_STONE, 0)), self.font_score, MENU_TEXT_COLOR, (panel_center_x, 285))

        line_y = 375
        pygame.draw.line(surface, MENU_BUTTON_COLOR, (panel_x_start + 20, line_y), (WINDOW_WIDTH - 20, line_y), 2)

        draw_text(surface, "WHITE PLAYER", self.font_title, MENU_TEXT_COLOR, (panel_center_x, 365))
        white_icon_center = (panel_center_x, 405)
        pygame.draw.circle(surface, WHITE, white_icon_center, 12)
        pygame.draw.circle(surface, BLACK, white_icon_center, 12, 1)
        draw_text(surface, "Captures:", self.font_label, MENU_TEXT_COLOR, (panel_center_x, 440))
        draw_text(surface, str(captures.get(WHITE_STONE, 0)), self.font_score, MENU_TEXT_COLOR, (panel_center_x, 480))
    
    def draw_final_result(self, surface, black_score, white_score, winner=None):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) 
        surface.blit(overlay, (0, 0))

        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT // 2
        
        draw_text(surface, "GAME OVER", self.font_score, LAST_MOVE_MARKER_COLOR, (center_x, center_y - 150))

        winner_text = "DRAW"
        winner_pos = (center_x, center_y - 80)
        
        # Xác định người thắng để hiển thị text
        final_winner = winner
        if final_winner is None:
            if black_score > white_score:
                final_winner = 1 # Black
            elif white_score > black_score:
                final_winner = 2 # White

        if final_winner == 1: # Black wins
            winner_text = "BLACK WINS"
            outline_surface = self.font_score.render(winner_text, True, WHITE)
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if dx != 0 or dy != 0:
                        rect = outline_surface.get_rect(center=(winner_pos[0] + dx, winner_pos[1] + dy))
                        surface.blit(outline_surface, rect)
            draw_text(surface, winner_text, self.font_score, BLACK, winner_pos)

        elif final_winner == 2: # White wins
            winner_text = "WHITE WINS"
            draw_text(surface, winner_text, self.font_score, WHITE, winner_pos)
        else:
            draw_text(surface, winner_text, self.font_score, MENU_TEXT_COLOR, winner_pos)

        score_text_b = f"Black: {black_score:.1f}"
        score_text_w = f"White: {white_score:.1f}"

        score_b_pos = (center_x, center_y + 20)
        outline_score_b = self.font_title.render(score_text_b, True, WHITE)
        
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx != 0 or dy != 0:
                    rect = outline_score_b.get_rect(center=(score_b_pos[0] + dx, score_b_pos[1] + dy))
                    surface.blit(outline_score_b, rect)
        
        draw_text(surface, score_text_b, self.font_title, BLACK, score_b_pos)
        draw_text(surface, score_text_w, self.font_title, WHITE, (center_x, center_y + 70))
        draw_text(surface, "(Komi 6.5 included)", self.font_label, MENU_TEXT_COLOR, (center_x, center_y + 120))

def draw_text(surface, text, font, color, center_pos):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=center_pos)
    surface.blit(text_surface, text_rect)

def main_menu(screen):
    try:
        title_font = pygame.font.Font(None, 80)
        button_font = pygame.font.Font(None, 50)
    except:
        default_font = pygame.font.get_default_font()
        title_font = pygame.font.Font(default_font, 80)
        button_font = pygame.font.Font(default_font, 50)

    button_1 = pygame.Rect(0, 0, 400, 80)
    button_1.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60)

    button_2 = pygame.Rect(0, 0, 400, 80)
    button_2.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60)
    
    button_black = pygame.Rect(0, 0, 180, 80)
    button_black.center = (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 60)
    
    button_white = pygame.Rect(0, 0, 180, 80)
    button_white.center = (WINDOW_WIDTH // 2 + 100, WINDOW_HEIGHT // 2 + 60)
    
    button_back = pygame.Rect(0, 0, 180, 50)
    button_back.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 180)

    clock = pygame.time.Clock()
    running = True
    menu_state = "MODE_SELECTION" 

    while running:
        screen.fill(BG_COLOR)
        mouse_x, mouse_y = pygame.mouse.get_pos()

        draw_text(screen, "GO GAME", title_font, MENU_TITLE_COLOR, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))

        if menu_state == "MODE_SELECTION":
            color_1 = MENU_BUTTON_HOVER_COLOR if button_1.collidepoint(mouse_x, mouse_y) else MENU_BUTTON_COLOR
            pygame.draw.rect(screen, color_1, button_1, border_radius=10)
            draw_text(screen, "2 PLAYER", button_font, MENU_TEXT_COLOR, button_1.center)

            color_2 = MENU_BUTTON_HOVER_COLOR if button_2.collidepoint(mouse_x, mouse_y) else MENU_BUTTON_COLOR
            pygame.draw.rect(screen, color_2, button_2, border_radius=10)
            draw_text(screen, "PLAY WITH AI", button_font, MENU_TEXT_COLOR, button_2.center)
            
        elif menu_state == "COLOR_SELECTION":
            draw_text(screen, "CHOOSE YOUR COLOR", button_font, MENU_TITLE_COLOR, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))

            color_black = MENU_BUTTON_HOVER_COLOR if button_black.collidepoint(mouse_x, mouse_y) else MENU_BUTTON_COLOR
            pygame.draw.rect(screen, color_black, button_black, border_radius=10)
            draw_text(screen, "BLACK", button_font, BLACK, button_black.center)

            color_white = MENU_BUTTON_HOVER_COLOR if button_white.collidepoint(mouse_x, mouse_y) else MENU_BUTTON_COLOR
            pygame.draw.rect(screen, color_white, button_white, border_radius=10)
            draw_text(screen, "WHITE", button_font, WHITE, button_white.center)
            pygame.draw.rect(screen, BLACK, button_white, 2, border_radius=10) 

            color_back = MENU_BUTTON_HOVER_COLOR if button_back.collidepoint(mouse_x, mouse_y) else MENU_BUTTON_COLOR
            pygame.draw.rect(screen, color_back, button_back, border_radius=10)
            draw_text(screen, "BACK", button_font, MENU_TEXT_COLOR, button_back.center)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return None, None

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if menu_state == "MODE_SELECTION":
                    if button_1.collidepoint(mouse_x, mouse_y):
                        return "P_VS_P", None 
                    elif button_2.collidepoint(mouse_x, mouse_y):
                        menu_state = "COLOR_SELECTION" 
                        
                elif menu_state == "COLOR_SELECTION":
                    if button_black.collidepoint(mouse_x, mouse_y):
                        return "P_VS_AI", BLACK_STONE
                    elif button_white.collidepoint(mouse_x, mouse_y):
                        return "P_VS_AI", WHITE_STONE
                    elif button_back.collidepoint(mouse_x, mouse_y):
                        menu_state = "MODE_SELECTION"

        pygame.display.update()
        clock.tick(30)