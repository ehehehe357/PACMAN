import pygame
from ui.pixel_assets import (
    COLORS, P_OPEN, P_CLOSED, GOAL1, GOAL2, SIZE, LE_TREN, LE_DUOI
)

p_couter = 0
p_speed = 10
is_mouth_open = True

WALL_T = 4

def surface_matrix (matrix, pixel_scale=4):
    rows = len(matrix)
    cols = len(matrix[0])

    width = cols*pixel_scale
    height = rows*pixel_scale

    P = pygame.Surface((width, height), pygame.SRCALPHA)

    for r_idx, row in enumerate(matrix):
        for c_idx, char in enumerate(row):
            if char in COLORS and COLORS[char]:
                color = COLORS[char]
                pygame.draw.rect(
                    P,
                    color,
                    (
                        c_idx * pixel_scale,
                        r_idx * pixel_scale,
                        pixel_scale,
                        pixel_scale
                    )
                )
    return P

p_open = surface_matrix(P_OPEN)
p_close = surface_matrix(P_CLOSED)
DIR_ANGLE = {(1, 0): 0, (0, -1): 90, (-1, 0): 180, (0, 1): 270}
p_open_dir = {d: pygame.transform.rotate(p_open, a) for d, a in DIR_ANGLE.items()}
p_close_dir = {d: pygame.transform.rotate(p_close, a) for d, a in DIR_ANGLE.items()}
goal1_surf = surface_matrix(GOAL1, pixel_scale=6)
goal2_surf = surface_matrix(GOAL2, pixel_scale=6)
_ghost_cache = {}
_mud_txt_surf = None

def blit_center(screen, surf, col, row):
    """Vẽ surf vào chính giữa ô (col, row)."""
    x = col * SIZE + (SIZE - surf.get_width()) // 2
    y = row * SIZE + LE_TREN + (SIZE - surf.get_height()) // 2
    screen.blit(surf, (x, y))

def draw_p (screen, potision, direction=(1, 0)):
    global p_couter, is_mouth_open
    x, y = potision
    #pos_x = int (x*SIZE)
    #pos_y = int(y*SIZE + LE_TREN)

    p_couter +=1
    if p_couter >= p_speed:
        is_mouth_open = not is_mouth_open
        p_couter = 0

    sprites = p_open_dir if is_mouth_open else p_close_dir

    #current_art = p_open if is_mouth_open else p_close
    #screen.blit(current_art, (pos_x, pos_y))
    blit_center(screen, sprites.get(direction, sprites[(1, 0)]), x, y)

def draw_g (screen, position, ghost_art):
    x, y = position
    pos_x = int (x*SIZE)
    pos_y = int (y*SIZE + LE_TREN)

    g_surf = surface_matrix(ghost_art, pixel_scale=4)
    screen.blit(g_surf, (pos_x, pos_y))

def build_wall_surface(map_data):
    """Vẽ tường 1 lần duy nhất ra 1 Surface, mỗi frame chỉ blit lại."""
    surf = pygame.Surface((map_data.cols * SIZE, map_data.rows * SIZE), pygame.SRCALPHA)
    color = COLORS['BL']
    t = WALL_T

    for r in range(map_data.rows):
        for c in range(map_data.cols):
            x, y = c * SIZE, r * SIZE

            if not map_data.is_wall(c, r):
                if map_data.grid[r][c] == '-':
                    pygame.draw.rect(surf, COLORS['P'], (x, y + SIZE // 2 - t // 2, SIZE, t))
                continue

            if r > 0 and not map_data.is_wall(c, r - 1):
                pygame.draw.rect(surf, color, (x, y, SIZE, t))
            if r < map_data.rows - 1 and not map_data.is_wall(c, r + 1):
                pygame.draw.rect(surf, color, (x, y + SIZE - t, SIZE, t))
            if c > 0 and not map_data.is_wall(c - 1, r):
                pygame.draw.rect(surf, color, (x, y, t, SIZE))
            if c < map_data.cols - 1 and not map_data.is_wall(c + 1, r):
                pygame.draw.rect(surf, color, (x + SIZE - t, y, t, SIZE))
    return surf


def draw_map(screen, map_data, wall_surf):
    screen.blit(wall_surf, (0, LE_TREN))
    for r in range(map_data.rows):
        for c in range(map_data.cols):
            ch = map_data.grid[r][c]
            x = c * SIZE
            y = r * SIZE + LE_TREN
            
            # Vẽ ô bùn lầy '~' có viền và đánh dấu chi phí = 5
            if ch == '~':
                mud_rect = pygame.Rect(x + 2, y + 2, SIZE - 4, SIZE - 4)
                pygame.draw.rect(screen, COLORS['MUD'], mud_rect, border_radius=4)
                # Vẽ nhãn số 5 nhỏ
                global _mud_txt_surf
                if _mud_txt_surf is None:
                    _font_mini = pygame.font.SysFont("arial", 12, bold=True)
                    _mud_txt_surf = _font_mini.render("5", True, COLORS['MUD_TXT'])
                screen.blit(_mud_txt_surf, _mud_txt_surf.get_rect(center=mud_rect.center))
            elif ch == 'o':
                blit_center(screen, goal1_surf, c, r)
            elif ch == '.':
                blit_center(screen, goal2_surf, c, r)

def draw_hud(screen, map_data, mode_text, map_text, score, font_big, font_small, font_score):
    # bên trái:tên chế độ và tên map
    s1 = font_big.render(mode_text, True, COLORS['Y'])
    s2 = font_small.render(map_text, True, COLORS['W'])
    screen.blit(s1, (10, 4))
    screen.blit(s2, (10, 4 + s1.get_height()))

    # bên phải hiện score ở góc trên cùng bên phải
    s3 = font_score.render(f"SCORE: {score}", True, COLORS['Y'])
    screen.blit(s3, (screen.get_width() - s3.get_width() - 15, 10))

def draw_box_winlose(screen, title_text, sub_text, font_title, font_sub, screen_width, screen_height):
    GAP = 20
    PAD = 60
    box_width = 360

    '''box_width = 360
    box_height = 180
    box_x = (screen_width - box_width) // 2
    box_y = (screen_height - box_height) // 2
    box_rect = pygame.Rect(box_x, box_y, box_width, box_height)'''

    title_surf = font_title.render(title_text, True, COLORS.get('Y', (255, 245, 59)))
    sub_surf = font_sub.render(sub_text, True, COLORS.get('Y', (255, 245, 59)))

    t_ink = title_surf.get_bounding_rect()
    s_ink = sub_surf.get_bounding_rect()

    box_height = PAD + t_ink.height + GAP + s_ink.height + PAD
    box_x = (screen_width - box_width) // 2
    box_y = (screen_height - box_height) // 2
    box_rect = pygame.Rect(box_x, box_y, box_width, box_height)

    pygame.draw.rect(screen, COLORS.get('BG', (3, 3, 3)), box_rect, border_radius=12)
    pygame.draw.rect(screen, COLORS.get('BL'), box_rect, 3, border_radius=12)

    title_y = box_rect.y + PAD - t_ink.top
    sub_y = box_rect.y + PAD + t_ink.height + GAP - s_ink.top
    screen.blit(title_surf, title_surf.get_rect(midtop=(box_rect.centerx, title_y)))
    screen.blit(sub_surf, sub_surf.get_rect(midtop=(box_rect.centerx, sub_y)))