import pygame

from ui.menu import load_font, FONT_MAIN
from ui.display import build_wall_surface, draw_map, draw_hud, draw_p, draw_g
from ui.pixel_assets import (
    COLORS, SIZE, LE_TREN, LE_DUOI,
    GHOST_RED, GHOST_PINK, GHOST_BLUE, GHOST_ORANGE,
)
from maps.map_loader import get_map

MODE_NAMES = {1: "Discovery Mode", 2: "Survival Mode", 3: "Counter-Attack Mode"}
MAP_NAMES = {1: "Tiny Maze", 2: "Medium Maze", 3: "Big Maze"}

STEP_MS = 150
MOVES = {
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0),
}

GHOST_ARTS = [GHOST_RED, GHOST_PINK, GHOST_BLUE, GHOST_ORANGE]

class GameScreen:
    def __init__(self):
        self.font_big = load_font(FONT_MAIN, 24)
        self.font_small = load_font(FONT_MAIN, 16)
        self.font_score = load_font(FONT_MAIN, 22)

        self.map_data = None
        self.wall_surf = None
        self.pacman_pos = [0, 0]
        self.pacman_dir = (1, 0)
        self.moving = False
        self.ghost_pos = []
        self.score = 0
        self.mode_text = ""
        self.map_text = ""
        self.last_step = 0

    def start(self, mode, map_id):
        self.map_data = get_map(mode, map_id)
        if self.map_data.p_start is None:
            raise ValueError("File map không có ký tự P (vị trí xuất phát của Pacman)")

        self.wall_surf = build_wall_surface(self.map_data)
        self.pacman_pos = list(self.map_data.p_start)
        self.pacman_dir = (1, 0)
        self.moving = False
        self.ghost_pos = [list(pos) for pos in self.map_data.g_start]
        self.score = 0
        self.mode_text = MODE_NAMES[mode]
        self.map_text = MAP_NAMES[map_id]
        self.last_step = pygame.time.get_ticks()

        width = self.map_data.cols * SIZE
        height = LE_TREN + self.map_data.rows * SIZE + LE_DUOI
        return pygame.display.set_mode((width, height))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "BACK"
            if event.key in MOVES:
                self.pacman_dir = MOVES[event.key]
                self.moving = True
        return None

    def can_go(self, direction):
        x = self.pacman_pos[0] + direction[0]
        y = self.pacman_pos[1] + direction[1]
        return self.map_data.cell(x, y) not in ('%', '-')

    def step_pacman(self):
        if not self.moving:
            return
        if self.can_go(self.pacman_dir):
            self.pacman_pos[0] += self.pacman_dir[0]
            self.pacman_pos[1] += self.pacman_dir[1]
            self.score += self.map_data.eat(self.pacman_pos[0], self.pacman_pos[1])

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_step < STEP_MS:
            return
        self.last_step = now
        self.step_pacman()
        #CHỖ NÀY NÀO ĐỂ MULTIAGENTS.PY VÔ

    def draw(self, screen):
        screen.fill(COLORS['BG'])
        draw_map(screen, self.map_data, self.wall_surf)
        for i, pos in enumerate(self.ghost_pos):
            draw_g(screen, pos, GHOST_ARTS[i % len(GHOST_ARTS)])
        draw_p(screen, self.pacman_pos, self.pacman_dir)
        draw_hud(screen, self.map_data, self.mode_text, self.map_text, self.score,
                 self.font_big, self.font_small, self.font_score)