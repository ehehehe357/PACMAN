import random
from maps.map_loader import MapData, SCORE_G1, SCORE_G2

MAP_SIZES = {
    1: (21, 11),  # Tiny Maze (Nhỏ)
    2: (27, 15),  # Medium Maze (Vừa)
    3: (33, 19)   # Big Maze (Lớn)
}

def gen_map(map_type = 1):
    width, height = MAP_SIZES.get(map_type)
    grid = [['%' for _ in range(width)] for _ in range(height)]

    start_x, start_y = 1, 1
    grid[start_x][start_y] = ' '

    stack = [(start_x, start_y)]

    while stack:
        x, y = stack[-1]
        neighbors = []
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            nx, ny = x+dx, y+dy
            if 0 < nx < width - 1 and 0 < ny < height - 1 and grid[ny][nx] == '%':
                neighbors.append((nx, ny, dx, dy))
        if neighbors:
            nx, ny, dx, dy = random.choice(neighbors)
            grid[y + dy // 2][x + dx // 2] = ' ' # Đập tường ở giữa
            grid[ny][nx] = ' '                     # Mở đường đi mới
            stack.append((nx, ny))
        else:
            stack.pop()
    
    for _ in range((width * height) // 12):
        rx = random.randint(1, width - 2)
        ry = random.randint(1, height - 2)
        if grid[ry][rx] == '%':
            grid[ry][rx] = ' '

    grid[1][1] = 'P'

    for r in range(height):
        for c in range(width):
            if grid[r][c] == ' ':
                rand_val = random.random()
                if rand_val < 0.15:
                    grid[r][c] = 'o'  # Goal 1 (+50đ)
                elif rand_val < 0.85:
                    grid[r][c] = '.'  # Goal 2 (+10đ)

    return ["".join(row) for row in grid]