import pygame
import random
import sys
import time

# 初始化Pygame
pygame.init()

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (169, 169, 169)
RED = (255, 0, 0)

# 定义屏幕大小和方块大小
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 20
COLUMNS = WIDTH // TILE_SIZE
ROWS = (HEIGHT - 40) // TILE_SIZE
MINES_COUNT = 40

# 初始化屏幕
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('福州二中扫雷游戏')

# 加载字体
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# 定义全局变量
grid = []
flags = []
revealed = []
mines = []
first_click = True
start_time = None
game_over = False
mines_left = MINES_COUNT

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

    # 随机放置地雷
    while len(mines) < MINES_COUNT:
        x, y = random.randint(0, COLUMNS - 1), random.randint(0, ROWS - 1)
        if (x, y) not in mines:
            mines.append((x, y))
            grid[y][x] = -1

    # 计算周围地雷数量
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
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE + 40, TILE_SIZE, TILE_SIZE)
            if revealed[y][x]:
                if grid[y][x] == -1:
                    pygame.draw.rect(screen, RED, rect)
                else:
                    pygame.draw.rect(screen, WHITE, rect)
                    if grid[y][x] > 0:
                        text = font.render(str(grid[y][x]), True, BLACK)
                        screen.blit(text, (x * TILE_SIZE + 5, y * TILE_SIZE + 40))
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

def main():
    global first_click, start_time, game_over, mines_left

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
                y = (y - 40) // TILE_SIZE
                if 0 <= x < COLUMNS and 0 <= y < ROWS:
                    if event.button == 1:  # 左键
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
                    elif event.button == 3:  # 右键
                        if not revealed[y][x]:
                            flags[y][x] = not flags[y][x]
                            mines_left += -1 if flags[y][x] else 1

        draw_grid()

        if start_time:
            elapsed_time = int(time.time() - start_time)
            timer_text = small_font.render(f'Time: {elapsed_time}', True, WHITE)
            screen.blit(timer_text, (10, 10))

        mines_left_text = small_font.render(f'Mines left: {mines_left}', True, WHITE)
        screen.blit(mines_left_text, (WIDTH - 150, 10))

        if game_over:
            if check_win():
                game_over_text = font.render('You Win!', True, WHITE)
            else:
                game_over_text = font.render('Game Over', True, WHITE)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
