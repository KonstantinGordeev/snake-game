import numpy as np
import cv2
import typing as tp
import sys
import json
from collections import deque

class SnakeGame:
    
    def __init__(self, config: tp.Dict[str, tp.Any]):
        self.config = config
        
        self.cell_size = self.init_param('CELL_SIZE', 20)
        self.board_size = self.init_param('BOARD_SIZE', 45)
        self.cur_speed = self.init_param('SPEED', 12)
        self.growth = self.init_param('GROWTH', 3)
        self.speed_mult = self.init_param('SPEED_MULTIPLIER', 1.007)
        self.sh_color = self.init_param('SH_COLOR', [0, 255, 0])
        self.sb_color = self.init_param('SB_COLOR', [0, 0, 255])
        self.f_color = self.init_param('F_COLOR', [0, 255, 255])
        self.bg_color = [0, 0, 0]
        
        self.snake_body = deque()
        self.cells_to_add = 0
        
        self.board = np.zeros((self.board_size, self.board_size, 3))
        start = np.random.choice(range(0, self.board_size), 2)
        self.snake_body.append(start)
        self.board[start[0], start[1]] = self.sh_color
        
        self.add_food()
        self.direction = np.random.randint(0, 4)
        
        self.score = 0
        
    def init_param(self, name: str, default_value: tp.Any):
        if name not in self.config:
            print(f'No parameter {name} in config, setting default value {default_value}', file=sys.stderr)
            self.config[name] = default_value
        return self.config[name]
    
    def add_food(self):
        candidates = set((i, j) for i in range(0, self.board_size) for j in range(0, self.board_size))
        for point in self.snake_body:
            point = tuple(point.tolist())
            if point in candidates:
                candidates.remove(point)
            
        point = list(candidates)[np.random.randint(0, len(candidates))]
        self.board[point] = self.f_color
        self.food_point = point
    
    def move(self):
        
        next_point = self.snake_body[-1].copy()
        if self.direction == 0:
            next_point[0] -= 1  # UP
        if self.direction == 1:
            next_point[0] += 1  # DOWN
        if self.direction == 2:
            next_point[1] -= 1  # LEFT
        if self.direction == 3:
            next_point[1] += 1  # RIGHT
        
        if not 0 <= next_point[0] < self.board_size or \
            not 0 <= next_point[1] < self.board_size:
            return False
        for point in self.snake_body:
            if (point == next_point).all():
                return False
        
        
        self.board[self.snake_body[-1][0], self.snake_body[-1][1]] = self.sb_color
        self.board[next_point[0], next_point[1]] = self.sh_color
        self.snake_body.append(next_point)
        
        if (next_point == self.food_point).all():
            self.cells_to_add += self.growth
            self.score += 1
            self.add_food()
            
        if self.cells_to_add > 0:
            self.cells_to_add -= 1
        else:
            self.board[self.snake_body[0][0], self.snake_body[0][1]] = self.bg_color
            self.snake_body.popleft()
            
        return True
            
    def upscale_board(self):
        return np.uint8(self.board.repeat(self.cell_size, 0).repeat(self.cell_size, 1))
    
    def display_board(self):
        board = self.upscale_board()
        cv2.imshow("Snake Game", board)
        key = cv2.waitKey(max(int(1000/self.cur_speed), 1))

        # Return the key pressed. It is -1 if no key is pressed. 
        return key
    
    def run(self):
        cv2.namedWindow("Snake Game", cv2.WINDOW_AUTOSIZE);
        cv2.imshow("Snake Game", self.upscale_board());
        
        # Ugly trick to get the window in focus.
        # Opens an image in fullscreen and then back to normal window
        cv2.setWindowProperty("Snake Game", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN);
        cv2.waitKey(2000)
        cv2.setWindowProperty("Snake Game", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_AUTOSIZE)
    
        while self.move():
            self.cur_speed *= self.speed_mult
            key = self.display_board()
            if key == 8 or key == 27:  # del and esc keys
                break
            elif key == ord("w") or key == 0:  # up arrow or W
                self.direction = 0
            elif key == ord("s") or key == 1:  # down arrow or S
                self.direction = 1
            elif key == ord("a") or key == 2:  # left arrow or A
                self.direction = 2
            elif key == ord("d") or key == 3:  # right arrow or D
                self.direction = 3
                
        print(f'Game over. Total score = {self.score}')
        
if __name__ == '__main__':
    config = json.load(open('config.json'))
    snake_game = SnakeGame(config)
    snake_game.run()