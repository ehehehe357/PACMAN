import os

MAPS_DIR = os.path.dirname(os.path.abspath(__file__))

SCORE_G1 = 50
SCORE_G2 = 10

def map_path(filename):
    return os.path.join(MAPS_DIR, filename)

class MapData:
    def __init__(self, lines):
        self.grid = [list(line) for line in lines]
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        self.p_start = None
        self.g_start = []

        for r in range (self.rows):
            for c in range (self.cols):
                ch = self.grid[r][c]
                if ch == 'P':
                    self.p_start = (c, r)
                    self.grid[r][c] = ' '
                elif ch=='G':
                    self.g_start.append ((c, r))
                    self.grid[r][c] = ' '
    def cell(self, x, y):
        if 0 <= y < self.rows and 0 <= x < self.cols:
            return self.grid[y][x]
        return '%'

    def is_wall (self, x, y):
        return self.cell(x, y) == '%'

    def eat (self, x, y):
        ch = self.cell(x, y)
        if ch=='o':
            self.grid[y][x] = ' '
            return SCORE_G1
        if ch == '.':
            self.grid[y][x] = ' '
            return SCORE_G2
        return 0

    def goal_left(self):
        return sum(row.count('o') + row.count('.') for row in self.grid)

def load_map (path):
    with open(path, encoding="utf-8") as f:
        lines = [line.rstrip("\r\n") for line in f if line.strip()]
    if not lines:
        raise ValueError(f"File map rỗng: {path}")
    width = len(lines[0])
    for i, line in enumerate(lines, 1):
        if len(line) != width:
            raise ValueError(f"{path}: dòng {i} dài {len(line)} ký tự, dòng 1 dài {width}")
    return MapData(lines)

'''Chỗ này sửa thêm sau khi thống nhất được menu :>'''
def get_map(mode, map_id):
    """Chọn map theo chế độ chơi. Mode 1 = không ma, mode 2/3 = có ma."""
    name = "tinyMaze.txt" if mode == 1 else "tinyMaze_ghost.txt"
    return load_map(map_path(name))