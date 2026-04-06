from typing import Tuple, Optional, List
from constants import EMPTY
from abc import ABC, abstractmethod
from go_board import GoBoard
from heuristic import Heuristic
from go_state import GoState

class SearchStrategy(ABC):
    @abstractmethod
    def search(self, game_state: GoState) -> Optional[Tuple[int, int]]:
        pass

class MinimaxAlgorithm(SearchStrategy):
    def __init__(self, depth: int, heuristic: Heuristic):
        self.depth_limit = depth
        self.heuristic = heuristic
        self.transposition_table = {}
        self.max_tt_size = 100000  # Giới hạn kích thước TT
        
    def search(self, game_state: GoState) -> Optional[Tuple[int, int]]:
        if game_state.is_game_over:
            return None
        
        current_player = game_state.current_player
        
        # 1. Lấy và sắp xếp nước đi
        actions = self._get_ordered_moves(game_state, current_player)
        
        # 2. Thêm nước đi Pass vào cuối
        actions.append(None) 

        best_move = None
        best_val = val_of_pass = float('-inf')
        alpha, beta = float('-inf'), float('inf')
        killer_moves = set()
        
        for action in actions:
            next_state = self._result(game_state, action)
            val = self.min_value(next_state, alpha, beta, self.depth_limit - 1, current_player, killer_moves)

            if action is None:
                val_of_pass = val
            elif val > best_val:
                best_val = val
                best_move = action
                killer_moves.add(action)
            
            alpha = max(alpha, best_val)
            if alpha >= beta:
                break

        # Quyết định Pass nếu chênh lệch quá nhỏ
        if best_move is not None and (best_val - val_of_pass) < 0.2:
            return None
        return best_move

    def _get_ordered_moves(self, state: GoState, player: int) -> List[Tuple[int, int]]:
        """Lấy danh sách nước đi đã được sắp xếp thông minh"""
        board = state.board
        legal_moves = board.get_legal_moves(player)
        
        if len(legal_moves) > 40:
            legal_moves = self._filter_promising_moves(legal_moves, board, player)
        
        legal_moves.sort(key=lambda m: self._evaluate_move_priority(m, board, board.size // 2, player), reverse=True)
        
        return legal_moves[:15] if len(legal_moves) > 15 else legal_moves

    def _filter_promising_moves(self, moves: List[Tuple[int, int]], board: GoBoard, player: int) -> List[Tuple[int, int]]:
        """Lọc ra những nước đi có tiềm năng (gần quân cờ đã có)"""
        size, grid = board.size, board.grid
        promising = []
        
        for r, c in moves:
            # Kiểm tra trong phạm vi 2 ô xung quanh
            if any(0 <= r + dr < size and 0 <= c + dc < size and 
                   grid[r + dr][c + dc] != EMPTY 
                   for dr in range(-2, 3) for dc in range(-2, 3) if abs(dr) + abs(dc) <= 2):
                promising.append((r, c))
        
        return promising if promising else moves[:20]

    def _alphabeta(self, state: GoState, alpha: float, beta: float, depth: int, root_player: int, killer_moves: set, is_maximizing: bool) -> float:
        """Hàm chung cho alpha-beta pruning, thay thế max_value và min_value"""
        state_hash = self._hash_state(state)
        tt_entry = self.transposition_table.get(state_hash)
        if tt_entry and tt_entry['depth'] >= depth:
            return tt_entry['value']
        
        if self._terminal_test(state, depth):
            return self._utility(state, root_player)

        v = float('-inf') if is_maximizing else float('inf')
        actions = self._reorder_with_killers(self._get_ordered_moves(state, state.current_player), killer_moves) + [None]

        for action in actions:
            next_state = self._result(state, action)
            child_val = self._alphabeta(next_state, alpha, beta, depth - 1, root_player, killer_moves, not is_maximizing)
            
            if is_maximizing:
                v = max(v, child_val)
                if v >= beta:
                    self._store_tt(state_hash, v, depth)
                    return v
                alpha = max(alpha, v)
            else:
                v = min(v, child_val)
                if v <= alpha:
                    self._store_tt(state_hash, v, depth)
                    return v
                beta = min(beta, v)
        
        self._store_tt(state_hash, v, depth)
        return v

    def max_value(self, state: GoState, alpha: float, beta: float, depth: int, root_player: int, killer_moves: set) -> float:
        return self._alphabeta(state, alpha, beta, depth, root_player, killer_moves, True)

    def min_value(self, state: GoState, alpha: float, beta: float, depth: int, root_player: int, killer_moves: set) -> float:
        return self._alphabeta(state, alpha, beta, depth, root_player, killer_moves, False)

    def _terminal_test(self, state: GoState, depth: int) -> bool:
        """Kiểm tra điều kiện dừng"""
        return depth == 0 or state.is_game_over

    def _utility(self, state: GoState, root_player: int) -> float:
        """Tính điểm Heuristic từ góc nhìn của root_player"""
        return self.heuristic.evaluate(state.board, root_player)

    def _result(self, state: GoState, action: Optional[Tuple[int, int]]) -> GoState:
        """Tạo trạng thái mới sau nước đi"""
        new_state = GoState(state.board.size)
        new_state.board = state.board.clone()
        new_state.current_player = state.current_player
        new_state.komi = state.komi
        new_state.consecutive_passes = state.consecutive_passes
        new_state.apply_move(action)
        return new_state

    def _evaluate_move_priority(self, move: Tuple[int, int], board: GoBoard, center: int, player: int) -> float:
        """Đánh giá độ ưu tiên của nước đi"""
        r, c = move
        priority = 0.0
        grid = board.grid
        size = board.size
        
        # 1. Ưu tiên nước đi gần nước đi trước
        if board.last_move:
            lr, lc = board.last_move
            dist_last = abs(r - lr) + abs(c - lc)
            if dist_last <= 2:
                priority += (3 - dist_last) * 100

        # 2. Đếm quân xung quanh
        opponent = 3 - player
        near_stones = near_opponent = 0
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < size and 0 <= nc < size:
                if grid[nr][nc] == player:
                    near_stones += 1
                elif grid[nr][nc] == opponent:
                    near_opponent += 1
        
        priority += near_stones * 30 + near_opponent * 25

        # 3. Ưu tiên trung tâm ở đầu game
        total_stones = sum(1 for row in grid for cell in row if cell != EMPTY)
        if total_stones < 10:
            dist_center = abs(r - center) + abs(c - center)
            priority -= dist_center * 5

        # 4. Tránh góc và cạnh
        if r in (0, size - 1) or c in (0, size - 1):
            priority -= 20

        # 5. Kiểm tra nước đi có cứu nhóm quân không
        priority += self._check_save_group(r, c, board, player) * 150
        
        # 6. Kiểm tra nước đi có bắt quân không
        priority += self._check_capture(r, c, board, player) * 120

        return priority

    def _check_group_threat(self, r: int, c: int, board: GoBoard, target_color: int, check_liberties: int = 1) -> int:
        """Kiểm tra nhóm quân có số liberty cụ thể (dùng cho save và capture)"""
        size, grid = board.size, board.grid
        count = 0
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == target_color:
                group = board._get_group(nr, nc)
                if board._count_group_liberties(group) == check_liberties:
                    count += len(group) if check_liberties == 1 else 1
        
        return count

    def _check_save_group(self, r: int, c: int, board: GoBoard, player: int) -> int:
        """Kiểm tra nước đi có cứu nhóm quân nguy hiểm không"""
        return 1 if self._check_group_threat(r, c, board, player, 1) > 0 else 0

    def _check_capture(self, r: int, c: int, board: GoBoard, player: int) -> int:
        """Kiểm tra nước đi có bắt được quân đối thủ không"""
        return min(self._check_group_threat(r, c, board, 3 - player, 1), 5)

    def _reorder_with_killers(self, moves: List[Tuple[int, int]], 
                              killer_moves: set) -> List[Tuple[int, int]]:
        """Sắp xếp lại với killer moves lên đầu"""
        return sorted(moves, key=lambda m: m not in killer_moves)

    def _hash_state(self, state: GoState) -> int:
        """Tạo hash cho state để dùng transposition table"""
        grid_tuple = tuple(tuple(row) for row in state.board.grid)
        return hash((grid_tuple, state.current_player))

    def _store_tt(self, state_hash: int, value: float, depth: int):
        """Lưu vào transposition table"""
        if len(self.transposition_table) >= self.max_tt_size:
            keys_to_remove = list(self.transposition_table.keys())[:1000]
            for key in keys_to_remove:
                del self.transposition_table[key]
        
        self.transposition_table[state_hash] = {
            'value': value,
            'depth': depth
        }