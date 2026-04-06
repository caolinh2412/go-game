from __future__ import annotations
from typing import Tuple, Set, List
from constants import EMPTY, BLACK_STONE, WHITE_STONE

class GoBoard:  
    def __init__(self, size):
        self.size = size
        self.grid = [[EMPTY for _ in range(size)] for _ in range(size)]
        self.captured_stones = {BLACK_STONE: 0, WHITE_STONE: 0}
        self.last_move = None
        self.previous_grid = None 

    def is_valid_move(self, row, col, player):
        if not (0 <= row < self.size and 0 <= col < self.size):
            return False
        if self.grid[row][col] != EMPTY:
            return False
        
        test_board = self.clone()
        test_board.grid[row][col] = player
        test_board._process_captures(row, col, player)
        
        group = test_board._get_group(row, col)
        if test_board._count_group_liberties(group) == 0:
            return False
        
        if self.previous_grid and test_board.grid == self.previous_grid:
            return False
            
        return True

    def place_stone(self, row, col, player):
        self.previous_grid = [row[:] for row in self.grid]
        self.grid[row][col] = player
        self.last_move = (row, col)
        self._process_captures(row, col, player)

    def calculate_territory(self) -> Tuple[int, int]:
        black_territory = white_territory = 0
        visited = [[False] * self.size for _ in range(self.size)]

        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == EMPTY and not visited[r][c]:
                    region_size, owners = self._flood_fill_territory(r, c, visited)
                    if len(owners) == 1:
                        owner = owners.pop()
                        if owner == BLACK_STONE:
                            black_territory += region_size
                        elif owner == WHITE_STONE:
                            white_territory += region_size
        
        return black_territory, white_territory

    def _flood_fill_territory(self, start_r: int, start_c: int, visited: List[List[bool]]) -> Tuple[int, Set[int]]:
        stack = [(start_r, start_c)]
        visited[start_r][start_c] = True
        region_size = 0
        surrounding_colors = set()
        
        while stack:
            r, c = stack.pop()
            region_size += 1
            
            for nr, nc in self._get_neighbors(r, c):
                neighbor_val = self.grid[nr][nc]
                if neighbor_val == EMPTY:
                    if not visited[nr][nc]:
                        visited[nr][nc] = True
                        stack.append((nr, nc))
                else:
                    surrounding_colors.add(neighbor_val)
                        
        return region_size, surrounding_colors

    def _process_captures(self, row, col, player):
        opponent = 3 - player
        neighbors = self._get_neighbors(row, col)
        for r, c in neighbors:
            if self.grid[r][c] == opponent:
                group = self._get_group(r, c)
                if self._count_group_liberties(group) == 0:
                    self._remove_group(group, player)

    def _get_group(self, row, col):
        color = self.grid[row][col]
        group = set()
        stack = [(row, col)]
        while stack:
            r, c = stack.pop()
            if (r, c) in group:
                continue
            group.add((r, c))
            for nr, nc in self._get_neighbors(r, c):
                if self.grid[nr][nc] == color:
                    stack.append((nr, nc))
        return group

    def _count_group_liberties(self, group):
        liberties = set()
        for r, c in group:
            for nr, nc in self._get_neighbors(r, c):
                if self.grid[nr][nc] == EMPTY:
                    liberties.add((nr, nc))
        return len(liberties)

    def _remove_group(self, group, capturer):
        for r, c in group:
            self.grid[r][c] = EMPTY
            self.captured_stones[capturer] += 1

    def _get_neighbors(self, row, col):
        """Lấy các ô lân cận (4 hướng)"""
        return [(row + dr, col + dc) for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                if 0 <= row + dr < self.size and 0 <= col + dc < self.size]

    def get_legal_moves(self, player):
        return [(r, c) for r in range(self.size) for c in range(self.size)
                if self.is_valid_move(r, c, player)]

    def clone(self):
        new_b = GoBoard(self.size)
        new_b.grid = [row[:] for row in self.grid]
        new_b.captured_stones = self.captured_stones.copy()
        new_b.last_move = self.last_move
        if self.previous_grid:
            new_b.previous_grid = [row[:] for row in self.previous_grid]
        return new_b