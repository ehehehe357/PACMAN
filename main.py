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
pacman_dir = (1, 0)     # hướng đang đi / đang nhìn
want_dir = None         # hướng người chơi vừa bấm, chờ rẽ
moving = False          # False cho đến khi bấm phím đầu tiên
STEP_MS = 140           # thời gian mỗi ô (ms): nhỏ hơn = nhanh hơn
last_step = 0
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
    global pacman_dir, want_dir, moving, last_step

    map_data = get_map(mode, map_id)
    wall_surf = build_wall_surface(map_data)
    pacman_pos = list(map_data.p_start)
    ghost_pos = list(map_data.g_start)
    pacman_dir = (1, 0)     # hướng đang đi / đang nhìn
    want_dir = None         # hướng người chơi vừa bấm, chờ rẽ
    moving = False          # False cho đến khi bấm phím đầu tiên
    last_step = pygame.time.get_ticks()
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


def can_go(pos, d):
    """Ô phía trước theo hướng d có đi được không (không phải tường/cửa nhà ma)."""
    return map_data.cell(pos[0] + d[0], pos[1] + d[1]) not in ('%', '-')


def step_pacman():
    """Chạy mỗi STEP_MS: rẽ nếu được, rồi đi tiếp, gặp tường thì đứng yên."""
    global pacman_pos, pacman_dir, want_dir, score
    if not moving:
        return
    if want_dir and can_go(pacman_pos, want_dir):
        pacman_dir = want_dir
        want_dir = None
    if can_go(pacman_pos, pacman_dir):
        pacman_pos = [pacman_pos[0] + pacman_dir[0], pacman_pos[1] + pacman_dir[1]]
        score += map_data.eat(pacman_pos[0], pacman_pos[1])


def handle_play_key(key):
    global want_dir, moving
    if key == pygame.K_ESCAPE:
        back_to_menu()
        return
    if key in MOVES:
        want_dir = MOVES[key]
        moving = True


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

    # MỚI: cập nhật vị trí Pacman theo thời gian
    if state == "PLAYING":
        now = pygame.time.get_ticks()
        if now - last_step >= STEP_MS:
            last_step = now
            step_pacman()

    if state == "MENU":
        menu.draw()
    else:
        screen.fill(COLORS['BG'])
        draw_map(screen, map_data, wall_surf)
        for i, pos in enumerate(ghost_pos):
            draw_g(screen, pos, GHOST_ARTS[i % len(GHOST_ARTS)])
        draw_p(screen, pacman_pos, pacman_dir)      # MỚI: thêm pacman_dir
        draw_hud(screen, map_data, mode_text, map_text, score,
                 font_big, font_small, font_score)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()