from player import Player
from typing import Optional, Tuple

class HumanPlayer(Player):
    def __init__(self, color):
        super().__init__(color=color)
            
    def get_move(self, go_state) -> Optional[Tuple[int, int]]:
        return None
