import random
import pygame
import sys
import time
import os
from pygame.locals import *
from tkinter import Tk, messagebox

class MinesweeperGame:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    DARK_GRAY = (169, 169, 169)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    
    WIDTH, HEIGHT = 800, 600
    TILE_SIZE = 20
    MENU_FONT_SIZE = 36
    GAME_FONT_SIZE = 24
    HEADER_HEIGHT = 40
    HIGHSCORE_FILE = 'highscores.txt'
    INITIAL_HIGH_SCORE = float('inf')

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('Fuzhou No.2 High School Minesweeper')
        self.menu_font = pygame.font.Font(None, self.MENU_FONT_SIZE)
        self.game_font = pygame.font.Font(None, self.GAME_FONT_SIZE)
        self.grid = []
        self.flags = []
        self.revealed = []
        self.mines = []
        self.first_click = True
        self.start_time = None
        self.game_over = False
        self.mines_left = 0
        self.COLUMNS = 0
        self.ROWS = 0
        self.difficulty = 'medium'
        self.MINES_COUNT = 0
        self.high_scores = {}
        self.read_high_scores()

    def read_high_scores(self):
        if os.path.exists(self.HIGHSCORE_FILE):
            with open(self.HIGHSCORE_FILE, 'r') as file:
                for line in file:
                    level, score = line.strip().split(':')
                    self.high_scores[level] = int(score) if score != 'inf' else self.INITIAL_HIGH_SCORE
        else:
            self.high_scores = {'easy': self.INITIAL_HIGH_SCORE, 'medium': self.INITIAL_HIGH_SCORE, 'hard': self.INITIAL_HIGH_SCORE}

    def write_high_scores(self):
        with open(self.HIGHSCORE_FILE, 'w') as file:
            for level, score in self.high_scores.items():
                file.write(f'{level}:{score if score != self.INITIAL_HIGH_SCORE else "inf"}\n')

    def create_grid(self):
        self.grid = [[0 for _ in range(self.COLUMNS)] for _ in range(self.ROWS)]
        self.flags = [[False for _ in range(self.COLUMNS)] for _ in range(self.ROWS)]
        self.revealed = [[False for _ in range(self.COLUMNS)] for _ in range(self.ROWS)]
        self.mines = []
        self.first_click = True
        self.start_time = None
        self.game_over = False
        self.mines_left = self.MINES_COUNT

        while len(self.mines) < self.MINES_COUNT:
            x, y = random.randint(0, self.COLUMNS - 1), random.randint(0, self.ROWS - 1)
            if (x, y) not in self.mines:
                self.mines.append((x, y))
                self.grid[y][x] = -1

        for y in range(self.ROWS):
            for x in range(self.COLUMNS):
                if self.grid[y][x] == -1:
                    continue
                count = sum((self.grid[y + dy][x + dx] == -1)
                            for dx in [-1, 0, 1] for dy in [-1, 0, 1]
                            if 0 <= x + dx < self.COLUMNS and 0 <= y + dy < self.ROWS)
                self.grid[y][x] = count

    def draw_grid(self):
        for y in range(self.ROWS):
            for x in range(self.COLUMNS):
                rect = pygame.Rect(x * self.TILE_SIZE, y * self.TILE_SIZE + self.HEADER_HEIGHT, self.TILE_SIZE, self.TILE_SIZE)
                if self.revealed[y][x]:
                    if self.grid[y][x] == -1:
                        pygame.draw.rect(self.screen, self.RED, rect)
                    else:
                        pygame.draw.rect(self.screen, self.WHITE, rect)
                        if self.grid[y][x] > 0:
                            text = self.game_font.render(str(self.grid[y][x]), True, self.BLACK)
                            self.screen.blit(text, (x * self.TILE_SIZE + 5, y * self.TILE_SIZE + self.HEADER_HEIGHT))
                else:
                    pygame.draw.rect(self.screen, self.GRAY, rect)
                    if self.flags[y][x]:
                        pygame.draw.circle(self.screen, self.RED, rect.center, self.TILE_SIZE // 4)
                pygame.draw.rect(self.screen, self.BLACK, rect, 1)

    def reveal_tile(self, x, y):
        if self.revealed[y][x] or self.flags[y][x]:
            return
        self.revealed[y][x] = True
        if self.grid[y][x] == -1:
            return
        if self.grid[y][x] == 0:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.COLUMNS and 0 <= ny < self.ROWS:
                        self.reveal_tile(nx, ny)

        def check_win(self):
        for y in range(self.ROWS):
            for x in range(self.COLUMNS):
                if self.grid[y][x] != -1 and not self.revealed[y][x]:
                    return False
        return True

    def show_message_box(self, message):
        root = Tk()
        root.withdraw()
        result = messagebox.askyesno("Game Over", message)
        root.destroy()
        return result

    def draw_menu(self):
        self.screen.fill(self.BLUE)
        title_text = self.menu_font.render('Choose Difficulty', True, self.WHITE)
        self.screen.blit(title_text, (self.WIDTH // 2 - title_text.get_width() // 2, self.HEIGHT // 4))

        easy_text = self.menu_font.render('1. Easy', True, self.WHITE)
        easy_rect = self.screen.blit(easy_text, (self.WIDTH // 2 - easy_text.get_width() // 2, self.HEIGHT // 2 - 60))

        medium_text = self.menu_font.render('2. Medium', True, self.WHITE)
        medium_rect = self.screen.blit(medium_text, (self.WIDTH // 2 - medium_text.get_width() // 2, self.HEIGHT // 2))

        hard_text = self.menu_font.render('3. Hard', True, self.WHITE)
        hard_rect = self.screen.blit(hard_text, (self.WIDTH // 2 - hard_text.get_width() // 2, self.HEIGHT // 2 + 60))

        highscore_title = self.menu_font.render('High Scores', True, self.WHITE)
        self.screen.blit(highscore_title, (self.WIDTH // 2 - highscore_title.get_width() // 2, self.HEIGHT // 2 + 150))

        easy_score_text = self.game_font.render(f'Easy: {self.high_scores["easy"]}s', True, self.WHITE)
        self.screen.blit(easy_score_text, (self.WIDTH // 2 - easy_score_text.get_width() // 2, self.HEIGHT // 2 + 200))

        medium_score_text = self.game_font.render(f'Medium: {self.high_scores["medium"]}s', True, self.WHITE)
        self.screen.blit(medium_score_text, (self.WIDTH // 2 - medium_score_text.get_width() // 2, self.HEIGHT // 2 + 230))

        hard_score_text = self.game_font.render(f'Hard: {self.high_scores["hard"]}s', True, self.WHITE)
        self.screen.blit(hard_score_text, (self.WIDTH // 2 - hard_score_text.get_width() // 2, self.HEIGHT // 2 + 260))

        pygame.display.flip()

        return easy_rect, medium_rect, hard_rect

    def set_difficulty(self, level):
        if level == 'easy':
            self.COLUMNS, self.ROWS = 10, 10
            self.MINES_COUNT = 10
        elif level == 'medium':
            self.COLUMNS, self.ROWS = 20, 15
            self.MINES_COUNT = 40
        elif level == 'hard':
            self.COLUMNS, self.ROWS = 30, 20
            self.MINES_COUNT = 99
        self.difficulty = level

    def main_menu(self):
        in_menu = True
        while in_menu:
            easy_rect, medium_rect, hard_rect = self.draw_menu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.set_difficulty('easy')
                        in_menu = False
                    elif event.key == pygame.K_2:
                        self.set_difficulty('medium')
                        in_menu = False
                    elif event.key == pygame.K_3:
                        self.set_difficulty('hard')
                        in_menu = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if easy_rect.collidepoint(event.pos):
                        self.set_difficulty('easy')
                        in_menu = False
                    elif medium_rect.collidepoint(event.pos):
                        self.set_difficulty('medium')
                        in_menu = False
                    elif hard_rect.collidepoint(event.pos):
                        self.set_difficulty('hard')
                        in_menu = False

    def game_loop(self):
        self.create_grid()
        running = True
        while running:
            self.screen.fill(self.DARK_GRAY)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    x, y = event.pos
                    x //= self.TILE_SIZE
                    y = (y - self.HEADER_HEIGHT) // self.TILE_SIZE
                    if 0 <= x < self.COLUMNS and 0 <= y < self.ROWS:
                        if event.button == 1:
                            if self.first_click:
                                self.first_click = False
                                self.start_time = time.time()
                                while (x, y) in self.mines:
                                    self.create_grid()
                            if self.grid[y][x] == -1:
                                self.game_over = True
                            else:
                                self.reveal_tile(x, y)
                                if self.check_win():
                                    self.game_over = True
                        elif event.button == 3:
                            if not self.revealed[y][x]:
                                self.flags[y][x] = not self.flags[y][x]
                                self.mines_left += -1 if self.flags[y][x] else 1

            self.draw_grid()
            if self.start_time:
                elapsed_time = int(time.time() - self.start_time)
                timer_text = self.game_font.render(f'Time: {elapsed_time}', True, self.WHITE)
                self.screen.blit(timer_text, (10, 10))

            mines_left_text = self.game_font.render(f'Mines left: {self.mines_left}', True, self.WHITE)
            self.screen.blit(mines_left_text, (self.WIDTH - 150, 10))

            if self.game_over:
                elapsed_time = int(time.time() - self.start_time)
                if self.check_win():
                    if elapsed_time < self.high_scores[self.difficulty]:
                        self.high_scores[self.difficulty] = elapsed_time
                        self.write_high_scores()
                    message = "You Win! Do you want to play again?"
                else:
                    message = "Game Over! Do you want to play again?"

                if self.show_message_box(message):
                    self.main_menu()
                    self.game_loop()
                else:
                    running = False

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def run(self):
        self.main_menu()
        self.game_loop()

if __name__ == '__main__':
    game = MinesweeperGame()
    game.run()

