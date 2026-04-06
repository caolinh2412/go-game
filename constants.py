import os

# Kích thước lưới
GRID_DIM = 9

# Kích thước CỦA BÀN CỜ (không đổi)
BOARD_WIDTH = 600 
BOARD_HEIGHT = 600 

# Kích thước của cửa sổ Pygame
WINDOW_WIDTH = 800   
WINDOW_HEIGHT = 600  

# Lề
PADDING_X = 30
PADDING_Y = 30

GRID_SPACING_X = (BOARD_WIDTH - 2 * PADDING_X) / (GRID_DIM - 1) 
GRID_SPACING_Y = (BOARD_HEIGHT - 2 * PADDING_Y) / (GRID_DIM - 1) 

# Kích thước Quân cờ
STONE_RADIUS = int(min(GRID_SPACING_X, GRID_SPACING_Y) / 2 * 0.9)

# Màu cơ bản
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Màu bàn cờ & Game
BG_COLOR = (40, 40, 40)    
BOARD_COLOR = (218, 165, 32) 
LINE_COLOR = BLACK     
STAR_POINT_COLOR = BLACK 
STAR_POINT_RADIUS = 4
HIGHLIGHT_COLOR = (0, 255, 0)      
LAST_MOVE_MARKER_COLOR = (255, 0, 0)
LAST_MOVE_MARKER_RADIUS = 5        

# Màu Menu
MENU_TITLE_COLOR = WHITE 
MENU_BUTTON_COLOR = (70, 70, 70)  
MENU_BUTTON_HOVER_COLOR = (100, 100, 100) 
MENU_TEXT_COLOR = WHITE 
MENU_BG_COLOR = (50, 50, 50)

# Trạng thái ô trên bàn cờ
EMPTY = 0
BLACK_STONE = 1
WHITE_STONE = 2