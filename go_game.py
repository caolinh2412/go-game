import pygame
import sys
from go_state import GoState  # Import GoState để quản lý trạng thái
from human_player import HumanPlayer
from ai_player import AIPlayer
from constants import *
from ui import UI, draw_text

class GoGame:
    def __init__(self, screen, game_mode, ai_strategy=None, human_color=None):
        self.screen = screen
        self.game_mode = game_mode
        self.running = True
        self.clock = pygame.time.Clock()
        self.state = GoState(size=GRID_DIM) 
        self.board = self.state.board 
        
        self.ui = UI()
        self.board_surface = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT))
        self.black_final_score = 0.0
        self.white_final_score = 0.0

        if game_mode == "P_VS_P":
            self.player1 = HumanPlayer(BLACK_STONE)
            self.player2 = HumanPlayer(WHITE_STONE)
        else: 
            ai_color = WHITE_STONE if human_color == BLACK_STONE else BLACK_STONE
            self.player1 = HumanPlayer(human_color) 
            self.player2 = AIPlayer(color=ai_color, strategy=ai_strategy) 

        self.hover_pos = None
        self.pass_button_rect = pygame.Rect(BOARD_WIDTH + 10, WINDOW_HEIGHT - 70, WINDOW_WIDTH - BOARD_WIDTH - 20, 50)

    def run(self):
        while self.running:
            self.handle_events()
         
            if self.state.is_game_over:
                self._calculate_final_score()
                
            self.draw()

            if self.game_mode == "P_VS_AI" and self.state.current_player == self.player2.color and not self.state.is_game_over:
                ai_move = self.player2.get_move(self.state)
                self._execute_ai_move(ai_move)
            
                if self.state.is_game_over:
                    self._calculate_final_score()
                    
                self.draw()

            self.clock.tick(30)
            
    def _execute_ai_move(self, ai_move):
        """Thực hiện nước đi của AI thông qua State"""
        self.state.apply_move(ai_move)

    def handle_events(self):

        is_human_turn = False
        if self.game_mode == "P_VS_P":
            is_human_turn = True 
        elif self.game_mode == "P_VS_AI":
             if self.state.current_player == self.player1.color:
                 is_human_turn = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_hover(event, is_human_turn)

            elif event.type == pygame.MOUSEBUTTONDOWN and not self.state.is_game_over:
                mouse_pos = pygame.mouse.get_pos()
                
                if self.pass_button_rect.collidepoint(mouse_pos) and is_human_turn:
                    self._player_pass()
                    
                elif is_human_turn:
                    if mouse_pos[0] < BOARD_WIDTH:
                        self._player_move(mouse_pos)
                        
    def _player_pass(self):
        """Người chơi pass"""
        self.state.apply_move(None) # Truyền None để báo hiệu Pass
        self.hover_pos = None
       
    def _handle_mouse_hover(self, event, is_human_turn):
        """Xử lý hover chuột"""
        if not (is_human_turn and not self.state.is_game_over):
            self.hover_pos = None
            return

        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[0] >= BOARD_WIDTH:
            self.hover_pos = None
            return

        row, col = self.ui.convert_mouse_to_grid(mouse_pos)
    
        if row is not None and self.board.is_valid_move(row, col, self.state.current_player):
            self.hover_pos = (row, col)
        else:
            self.hover_pos = None

    def _player_move(self, mouse_pos):
        """Người chơi đi nước"""
        row, col = self.ui.convert_mouse_to_grid(mouse_pos)
        if row is None or col is None:
            return

        move = (row, col)
        if self.board.is_valid_move(row, col, self.state.current_player):
            self.state.apply_move(move)
            self.hover_pos = None
    
    def _calculate_final_score(self):
        """Lấy điểm từ State"""
        b_score, w_score = self.state.get_scores()
        
        self.black_final_score = b_score
        self.white_final_score = w_score + self.state.komi 

    def draw(self):
        """Vẽ giao diện game"""
        self.screen.fill(BG_COLOR)
        self.ui.draw_board(self.board_surface)
        
        # Vẽ quân cờ và highlight
        self.ui.draw_stones(self.board_surface, self.board.grid, self.board.last_move)
        self.ui.draw_hover_highlight(self.board_surface, self.hover_pos)
        self.screen.blit(self.board_surface, (0, 0))
       
        # Vẽ bảng điểm: Truyền captured_stones và current_player
        self.ui.draw_score_panel(self.screen, self.board.captured_stones, self.state.current_player)
        
        # Vẽ nút Pass
        mouse_x, mouse_y = pygame.mouse.get_pos()
        color = MENU_BUTTON_HOVER_COLOR if self.pass_button_rect.collidepoint(mouse_x, mouse_y) else MENU_BUTTON_COLOR
        pygame.draw.rect(self.screen, color, self.pass_button_rect, border_radius=5)
        draw_text(self.screen, "PASS", self.ui.font_title, MENU_TEXT_COLOR, self.pass_button_rect.center)
        
        # Vẽ kết quả nếu game over
        if self.state.is_game_over:
            self.ui.draw_final_result(self.screen, self.black_final_score, self.white_final_score, self.state.winner) 

        pygame.display.update()