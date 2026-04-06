import pygame
import sys
from constants import *
from go_game import GoGame
from ui import main_menu
from ai_algorithm import MinimaxAlgorithm
from heuristic import GoHeuristic 

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("GO GAME")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    selected_mode, human_color = main_menu(screen) 

    if selected_mode:
        ai_strategy = None
       
        if selected_mode == "P_VS_AI":
            # 1. Khởi tạo đối tượng Heuristic 
            ai_heuristic = GoHeuristic() 
            
            # 2. Định cấu hình chiến lược AI 
            ai_strategy = MinimaxAlgorithm(
                heuristic=ai_heuristic, 
                depth=3
            ) 
        
        #3: Truyền chiến lược AI và màu cờ đã chọn vào GoGame
        GoGame(
            screen=screen, 
            game_mode=selected_mode, 
            ai_strategy=ai_strategy,
            human_color=human_color 
        ).run()

    pygame.quit()
    sys.exit()                    