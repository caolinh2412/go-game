from abc import ABC, abstractmethod
from typing import Tuple, Optional 

class Player(ABC):
    def __init__(self, color: int):
        self.color = color
    @abstractmethod
    def get_move(self, go_state) -> Optional[Tuple[int, int]]: 
        pass
