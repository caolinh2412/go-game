from __future__ import annotations
from typing import List, Tuple, Optional
from go_board import GoBoard
from constants import BLACK_STONE, WHITE_STONE

class GoState:
    def __init__(self, size):
        self.board = GoBoard(size)
        self.current_player = BLACK_STONE 
        self.is_game_over = False
        self.winner = None
        self.consecutive_passes = 0
        self.komi = 6.5
        self.final_result_text = "" 

    def get_scores(self) -> Tuple[float, float]:
        """Tính điểm tổng kết: Lãnh thổ + Số tù binh đã bắt"""
        black_terr, white_terr = self.board.calculate_territory()
        return (black_terr + self.board.captured_stones[BLACK_STONE],
                white_terr + self.board.captured_stones[WHITE_STONE])

    def apply_move(self, move):
        if move is None:
            self.consecutive_passes += 1
        else:
            self.consecutive_passes = 0
            row, col = move
            if self.board.is_valid_move(row, col, self.current_player):
                self.board.place_stone(row, col, self.current_player)
            else:
                return

        if self.consecutive_passes >= 2:
            self.is_game_over = True
            self._determine_winner()
        
        self.current_player = 3 - self.current_player

    def player_resign(self, player):
        self.is_game_over = True
        self.winner = 3 - player
        self._determine_winner(force_end=True)

    def _determine_winner(self, force_end=False):
        b_score, w_score = self.get_scores()
        w_score += self.komi
        
        if not force_end:
            self.winner = BLACK_STONE if b_score > w_score else WHITE_STONE

        winner_str = "Black" if self.winner == BLACK_STONE else "White"
        self.final_result_text = f"{winner_str} Wins! (B:{b_score} - W:{w_score})"