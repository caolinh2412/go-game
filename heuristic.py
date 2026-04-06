from abc import ABC, abstractmethod
from go_board import GoBoard
from constants import EMPTY

W_TERRITORY = 8.0
W_CAPTURE   = 10.0
W_KOMI      = 6.5
W_INFLUENCE = 2.0
W_LINK      = 0.1
W_DANGER    = 15.0
W_BAD_SHAPE = 3.0

W_MOVE_COST = 0.5

INFL_OFFSETS = []
for r in range(-2, 3):
    for c in range(-2, 3):
        d = abs(r) + abs(c)
        if 0 < d <= 2: INFL_OFFSETS.append((r, c, 1.0 if d == 1 else 0.5))

class Heuristic(ABC):
    @abstractmethod
    def evaluate(self, board: GoBoard, player_color: int) -> float: pass

class GoHeuristic(Heuristic):
    def evaluate(self, board: GoBoard, player: int) -> float:
        score = 0.0
        size, grid = board.size, board.grid
        opp = 3 - player

        b_terr, w_terr = board.calculate_territory()
        terr_diff = (b_terr - w_terr) if player == 1 else (w_terr - b_terr)
        cap_diff = board.captured_stones.get(player, 0) - board.captured_stones.get(opp, 0)
        
        score += (terr_diff * W_TERRITORY) + (cap_diff * W_CAPTURE)
        score += W_KOMI if player == 2 else -W_KOMI

        score += self._analyze_potential(board, player) * W_INFLUENCE

        # Trừ điểm đánh nhiều quân mà không tăng đất thì điểm càng thấp
        player_stones = 0
        for r in range(size):
            for c in range(size):
                if grid[r][c] == player:
                    player_stones += 1
        score -= player_stones * W_MOVE_COST

        checked_groups = set()
        
        POS_SCORES = {0: -1.0, 1: 0.5, 2: 2.0, 3: 1.5, 'center': 1.0}

        for r in range(size):
            for c in range(size):
                p = grid[r][c]
                if p == EMPTY: continue
                
                mult = 1 if p == player else -1.2
                
                d_edge = min(r, c, size - 1 - r, size - 1 - c)
                pos_score = POS_SCORES.get(d_edge, POS_SCORES['center'])
                score += pos_score * mult

                neighbors = []
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == p:
                        neighbors.append((nr, nc))
                
                score += len(neighbors) * W_LINK * mult

                if len(neighbors) == 4:
                    score -= W_BAD_SHAPE * mult

                if (r, c) not in checked_groups:
                    group = board._get_group(r, c)
                    checked_groups.update(group)
                    libs = board._count_group_liberties(group)
                    
                    if libs < 3:
                        score -= (3 - libs) * W_DANGER * mult
                    elif libs >= 4:
                        score += 1.0 * mult

        return score

    def _analyze_potential(self, board: GoBoard, player: int) -> float:
        score = 0.0
        size, grid = board.size, board.grid
        opp = 3 - player
        
        POS_W = {2: 1.0, 3: 0.8, 'default': 0.5}

        for r in range(size):
            for c in range(size):
                if grid[r][c] != EMPTY: continue
                
                inf_diff = 0.0
                for dr, dc, w in INFL_OFFSETS:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < size and 0 <= nc < size:
                        st = grid[nr][nc]
                        if st == player: inf_diff += w
                        elif st == opp:  inf_diff -= w
                
                if abs(inf_diff) > 0.5:
                    d_edge = min(r, c, size-1-r, size-1-c)
                    pos_val = POS_W.get(d_edge, POS_W['default'])
                    
                    score += (1.0 if inf_diff > 0 else -1.0) * pos_val
        return score