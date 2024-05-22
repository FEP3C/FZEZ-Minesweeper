import random
import pygame
import sys
import time
import os
from pygame.locals import *
from tkinter import Tk, messagebox

# Initialize Pygame
pygame.init()

# Constants
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

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Fuzhou No.2 High School Minesweeper')

# Load fonts
menu_font = pygame.font.Font(None, MENU_FONT_SIZE)
game_font = pygame.font.Font(None, GAME_FONT_SIZE)

# Global variables
grid, flags, revealed, mines = [], [], [], []
first_click = True
start_time = None
game_over = False
mines_left = 0
COLUMNS = 0
ROWS = 0
difficulty = 'medium'
MINES_COUNT = 0
high_scores = {}

def read_high_scores():
    global high_scores
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, 'r') as file:
            for line in file:
                level, score = line.strip().split(':')
                high_scores[level] = int(score) if score != 'inf' else INITIAL_HIGH_SCORE
    else:
        high_scores = {'easy': INITIAL_HIGH_SCORE, 'medium': INITIAL_HIGH_SCORE, 'hard': INITIAL_HIGH_SCORE}

def write_high_scores():
    with open(HIGHSCORE_FILE, 'w') as file:
        for level, score in high_scores.items():
            file.write(f'{level}:{score if score != INITIAL_HIGH_SCORE else "inf"}\n')

def create_grid():
    global grid, mines, flags, revealed, first_click, start_time, game_over, mines_left
    grid = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]
    flags = [[False for _ in range(COLUMNS)] for _ in range(ROWS)]
    revealed = [[False for _ in range(COLUMNS)] for _ in range(ROWS)]
    mines = []
    first_click = True
    start_time = None
    game_over = False
    mines_left = MINES_COUNT

    while len(mines) < MINES_COUNT:
        x, y = random.randint(0, COLUMNS - 1), random.randint(0, ROWS - 1)
        if (x, y) not in mines:
            mines.append((x, y))
            grid[y][x] = -1

    for y in range(ROWS):
        for x in range(COLUMNS):
            if grid[y][x] == -1:
                continue
            count = sum((grid[y + dy][x + dx] == -1)
                        for dx in [-1, 0, 1] for dy in [-1, 0, 1]
                        if 0 <= x + dx < COLUMNS and 0 <= y + dy < ROWS)
            grid[y][x] = count

def draw_grid():
    for y in range(ROWS):
        for x in range(COLUMNS):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE + HEADER_HEIGHT, TILE_SIZE, TILE_SIZE)
            if revealed[y][x]:
                if grid[y][x] == -1:
                    pygame.draw.rect(screen, RED, rect)
                else:
                    pygame.draw.rect(screen, WHITE, rect)
                    if grid[y][x] > 0:
                        text = game_font.render(str(grid[y][x]), True, BLACK)
                        screen.blit(text, (x * TILE_SIZE + 5, y * TILE_SIZE + HEADER_HEIGHT))
            else:
                pygame.draw.rect(screen, GRAY, rect)
                if flags[y][x]:
                    pygame.draw.circle(screen, RED, rect.center, TILE_SIZE // 4)
            pygame.draw.rect(screen, BLACK, rect, 1)

def reveal_tile(x, y):
    if revealed[y][x] or flags[y][x]:
        return
    revealed[y][x] = True
    if grid[y][x] == -1:
        return
    if grid[y][x] == 0:
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < COLUMNS and 0 <= ny < ROWS:
                    reveal_tile(nx, ny)

def check_win():
    for y in range(ROWS):
        for x in range(COLUMNS):
            if grid[y][x] != -1 and not revealed[y][x]:
                return False
    return True

def show_message_box(message):
    root = Tk()
    root.withdraw()
    result = messagebox.askyesno("Game Over", message)
    root.destroy()
    return result

def draw_menu():
    screen.fill(BLUE)
    title_text = menu_font.render('Choose Difficulty', True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))

    easy_text = menu_font.render('1. Easy', True, WHITE)
    easy_rect = screen.blit(easy_text, (WIDTH // 2 - easy_text.get_width() // 2, HEIGHT // 2 - 60))

    medium_text = menu_font.render('2. Medium', True, WHITE)
    medium_rect = screen.blit(medium_text, (WIDTH // 2 - medium_text.get_width() // 2, HEIGHT // 2))

    hard_text = menu_font.render('3. Hard', True, WHITE)
    hard_rect = screen.blit(hard_text, (WIDTH // 2 - hard_text.get_width() // 2, HEIGHT // 2 + 60))

    highscore_title = menu_font.render('High Scores', True, WHITE)
    screen.blit(highscore_title, (WIDTH // 2 - highscore_title.get_width() // 2, HEIGHT // 2 + 150))

    easy_score_text = game_font.render(f'Easy: {high_scores["easy"]}s', True, WHITE)
    screen.blit(easy_score_text, (WIDTH // 2 - easy_score_text.get_width() // 2, HEIGHT // 2 + 200))

    medium_score_text = game_font.render(f'Medium: {high_scores["medium"]}s', True, WHITE)
    screen.blit(medium_score_text, (WIDTH // 2 - medium_score_text.get_width() // 2, HEIGHT // 2 + 230))

    hard_score_text = game_font.render(f'Hard: {high_scores["hard"]}s', True, WHITE)
    screen.blit(hard_score_text, (WIDTH // 2 - hard_score_text.get_width() // 2, HEIGHT // 2 + 260))

    pygame.display.flip()
    
    return easy_rect, medium_rect, hard_rect

def set_difficulty(level):
    global MINES_COUNT, COLUMNS, ROWS, difficulty
    if level == 'easy':
        COLUMNS, ROWS = 10, 10
        MINES_COUNT = 10
    elif level == 'medium':
        COLUMNS, ROWS = 20, 15
        MINES_COUNT = 40
    elif level == 'hard':
        COLUMNS, ROWS = 30, 20
        MINES_COUNT = 99
    difficulty = level

def main():
    global first_click, start_time, game_over, mines_left

    read_high_scores()

    in_menu = True
    while in_menu:
        easy_rect, medium_rect, hard_rect = draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    set_difficulty('easy')
                    in_menu = False
                elif event.key == pygame.K_2:
                    set_difficulty('medium')
                    in_menu = False
                elif event.key == pygame.K_3:
                    set_difficulty('hard')
                    in_menu = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if easy_rect.collidepoint(event.pos):
                    set_difficulty('easy')
                    in_menu = False
                elif medium_rect.collidepoint(event.pos):
                    set_difficulty('medium')
                    in_menu = False
                elif hard_rect.collidepoint(event.pos):
                    set_difficulty('hard')
                    in_menu = False

    create_grid()
    running = True
    while running:
        screen.fill(DARK_GRAY)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x, y = event.pos
                x //= TILE_SIZE
                y = (y - HEADER_HEIGHT) // TILE_SIZE
                if 0 <= x < COLUMNS and 0 <= y < ROWS:
                    if event.button == 1:
                        if first_click:
                            first_click = False
                            start_time = time.time()
                            while (x, y) in mines:
                                create_grid()
                        if grid[y][x] == -1:
                            game_over = True
                        else:
                            reveal_tile(x, y)
                            if check_win():
                                game_over = True
                    elif event.button == 3:
                        if not revealed[y][x]:
                            flags[y][x] = not flags[y][x]
                            mines_left += -1 if flags[y][x] else 1

        draw_grid()

        if start_time:
            elapsed_time = int(time.time() - start_time)
            timer_text = game_font.render(f'Time: {elapsed_time}', True, WHITE)
            screen.blit(timer_text, (10, 10))

        mines_left_text = game_font.render(f'Mines left: {mines_left}', True, WHITE)
        screen.blit(mines_left_text, (WIDTH - 150, 10))

        if game_over:
            elapsed_time = int(time.time() - start_time)
            if check_win():
                if elapsed_time < high_scores[difficulty]:
                    high_scores[difficulty] = elapsed_time
                    write_high_scores()
                message = "You Win! Do you want to play again?"
            else:
                message = "Game Over! Do you want to play again?"

            if show_message_box(message):
                main()
            else:
                running = False

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
