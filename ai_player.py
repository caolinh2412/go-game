from ai_algorithm import SearchStrategy
from typing import Optional, Tuple
from player import Player

class AIPlayer(Player):
    def __init__(self, color: int, strategy: SearchStrategy):
        super().__init__(color=color)
        self.strategy = strategy

    def get_move(self, go_state) -> Optional[Tuple[int, int]]: 
        return self.strategy.search(go_state)
