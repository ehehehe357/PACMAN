import pygame
from ui.pixel_assets import COLORS, P_OPEN, P_CLOSED, SIZE, LE_TREN

p_couter = 0
p_speed = 10
is_mouth_open = True

def surface_matrix (matrix, pixel_scale=4):
    rows = len(matrix)
    cols = len(matrix[0])

    width = cols*pixel_scale
    height = rows*pixel_scale

    P = pygame.Surface((width, height), pygame.SRCALPHA)

    for r_idx, row in enumerate(matrix):
        for c_idx, char in enumerate(matrix):
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

def draw_p (screen, potision):
    global p_couter, is_mouth_open
    x, y = potision
    pos_x = int (x*SIZE)
    pos_y = int(y*SIZE + LE_TREN)

    p_couter +=1
    if p_couter >= p_speed:
        is_mouth_open = not is_mouth_open
        p_couter = 0

    current_art = p_open if is_mouth_open else p_close

    screen.blit(current_art, (pos_x, pos_y))

def draw_g (screen, position, ghost_art):
    x, y = position
    pos_x = int (x*SIZE)
    pos_y = int (y*SIZE + LE_TREN)

    g_surf = surface_matrix(ghost_art, pixel_scale=4)
    screen.blit(g_surf, (pos_x, pos_y))