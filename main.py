import sys
import pygame

from ui.menu import Menu, load_font, FONT_MAIN
from ui.display import draw_p, draw_g, build_wall_surface, draw_map, draw_hud
from ui.pixel_assets import (
    COLORS, SIZE, LE_TREN, LE_DUOI,
    GHOST_RED, GHOST_PINK, GHOST_BLUE, GHOST_ORANGE,
)
from maps.map_loader import load_map, map_path

pygame.init()
WIDTH, HEIGHT = 600, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pacman Arcade")
clock = pygame.time.Clock()

MODE_NAMES = {1: "Discovery Mode", 2: "Survival Mode", 3: "Counter-Attack Mode"}
MAP_NAMES = {1: "Tiny Maze", 2: "Medium Maze", 3: "Big Maze"}
GHOST_ARTS = [GHOST_RED, GHOST_PINK, GHOST_BLUE, GHOST_ORANGE]

font_big = load_font(FONT_MAIN, 24)
font_small = load_font(FONT_MAIN, 16)
font_score = load_font(FONT_MAIN, 22)

menu = Menu(screen, WIDTH, HEIGHT)
state = "MENU"          # "MENU" hoặc "PLAYING"

# Dữ liệu của ván chơi hiện tại
map_data = None
wall_surf = None
pacman_pos = [0, 0]
ghost_pos = []
score = 0
mode_text = ""
map_text = ""

# CHỈ ĐỂ TEST HIỂN THỊ: phím mũi tên di chuyển Pacman (xoá khi AI đã điều khiển)
MOVES = {pygame.K_UP: (0, -1), pygame.K_DOWN: (0, 1),
         pygame.K_LEFT: (-1, 0), pygame.K_RIGHT: (1, 0)}


def get_map(mode, map_id):
    """BƯỚC A: đọc map tĩnh. Mode 1 = không ma, mode 2/3 = có ma."""
    name = "tinyMaze.txt" if mode == 1 else "tinyMaze_ghost.txt"
    return load_map(map_path(name))


def start_game(mode, map_id):
    global state, screen, map_data, wall_surf, pacman_pos, ghost_pos
    global score, mode_text, map_text

    map_data = get_map(mode, map_id)
    wall_surf = build_wall_surface(map_data)
    pacman_pos = list(map_data.p_start)
    ghost_pos = list(map_data.g_start)
    score = 0
    mode_text = MODE_NAMES[mode]
    map_text = MAP_NAMES[map_id]

    # Cửa sổ co giãn theo kích thước map
    screen = pygame.display.set_mode(
        (map_data.cols * SIZE, LE_TREN + map_data.rows * SIZE + LE_DUOI)
    )
    state = "PLAYING"


def back_to_menu():
    global state, screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    menu.screen = screen              # menu phải dùng lại surface mới
    menu.current_state = 1
    menu.selected_index = 0
    state = "MENU"


def handle_play_key(key):
    global pacman_pos, score
    if key == pygame.K_ESCAPE:
        back_to_menu()
        return
    dx, dy = MOVES.get(key, (0, 0))
    nx, ny = pacman_pos[0] + dx, pacman_pos[1] + dy
    if (dx or dy) and map_data.cell(nx, ny) not in ('%', '-'):
        pacman_pos = [nx, ny]
        score += map_data.eat(nx, ny)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif state == "MENU":
            result = menu.handle_input(event)
            if result == "EXIT":
                running = False
            elif isinstance(result, dict) and result["action"] == "START_GAME":
                start_game(result["mode"], result["map"])
        elif state == "PLAYING" and event.type == pygame.KEYDOWN:
            handle_play_key(event.key)

    if state == "MENU":
        menu.draw()
    else:
        screen.fill(COLORS['BG'])
        draw_map(screen, map_data, wall_surf)
        for i, pos in enumerate(ghost_pos):
            draw_g(screen, pos, GHOST_ARTS[i % len(GHOST_ARTS)])
        draw_p(screen, pacman_pos)
        draw_hud(screen, map_data, mode_text, map_text, score,
                 font_big, font_small, font_score)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()