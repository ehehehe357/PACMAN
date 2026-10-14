import pygame

from ui.menu import load_font, FONT_MAIN, FONT_HEADING
from ui.display import build_wall_surface, draw_map, draw_hud, draw_p, draw_g, draw_box_winlose
from ui.pixel_assets import (
    COLORS, SIZE, LE_TREN, LE_DUOI,
    GHOST_RED, GHOST_PINK, GHOST_BLUE, GHOST_ORANGE,
    GHOST_ATE, GHOST_EAT,
)
from maps.map_generator import get_map

try:
    from src.engine import GameState
    from src.multiAgents import AlphaBetaAgent, ChaseGhost
except ImportError:
    from engine import GameState
    from multiAgents import AlphaBetaAgent, ChaseGhost

MODE_NAMES = {
    1: "Player vs AI Ghosts",
    2: "AI vs AI Autoplay",
    3: "Discovery Mode",
}
MAP_NAMES = {1: "Tiny Maze", 2: "Medium Maze", 3: "Big Maze"}

ACTION_TO_DIR = {
    'NORTH': (0, -1),
    'SOUTH': (0, 1),
    'WEST': (-1, 0),
    'EAST': (1, 0),
    'STOP': (0, 0),
}

class ScreenLayout:
    """Adapter chuyển map_data của UI thành Layout tương thích GameState của Engine"""
    def __init__(self, map_data, pacman_pos, ghost_pos, cached_walls=None):
        self.pacman_start = tuple(pacman_pos)
        self.ghost_starts = [tuple(g) for g in ghost_pos]
        self.height = map_data.rows
        self.width = map_data.cols
        self.walls = cached_walls if cached_walls is not None else [[map_data.grid[r][c] == '%' for c in range(map_data.cols)] for r in range(map_data.rows)]
        self.food = [[map_data.grid[r][c] == '.' for c in range(map_data.cols)] for r in range(map_data.rows)]
        self.capsules = [(c, r) for r in range(map_data.rows) for c in range(map_data.cols) if map_data.grid[r][c] == 'o']

STEP_MS = 150
P_BLINK = 500
P_BLINKS = 3
MOVES = {
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0),
}

GHOST_ARTS = [GHOST_RED, GHOST_PINK, GHOST_BLUE, GHOST_ORANGE]
NORMAL, SCARED, EATEN = "NORMAL", "SCARED", "EATEN"
SCARED_SECONDS = {1: 4, 2: 5, 3: 6}
BLINK_MS = 1000
GHOST_POINTS = 200

class GameScreen:
    def __init__(self):
        self.font_big = load_font(FONT_MAIN, 24)
        self.font_small = load_font(FONT_MAIN, 16)
        self.font_score = load_font(FONT_MAIN, 22)
        self.font_bigger = load_font(FONT_MAIN, 40)

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

        self.status = "PLAYING"
        self.dying_start = 0
        self.font_heading = load_font(FONT_HEADING, 40)

        self.map_id = 1
        self.ghost_state = []
        self.ghost_path = []
        self.scared_end = 0
        self.eat_combo = 0

    def start(self, mode, map_id):
        self.map_data = get_map(mode, map_id)
        if self.map_data.p_start is None:
            raise ValueError("File map không có ký tự P (vị trí xuất phát của Pacman)")

        self.wall_surf = build_wall_surface(self.map_data)
        self.pacman_pos = list(self.map_data.p_start)
        self.pacman_dir = (1, 0)
        self.ghost_pos = [list(pos) for pos in self.map_data.g_start]
        self.map_id = map_id
        self.ghost_state = [NORMAL for _ in self.ghost_pos]
        self.ghost_path = [[] for _ in self.ghost_pos]
        self.scared_end = 0
        self.eat_combo = 0
        self.score = 0
        self.mode_text = MODE_NAMES.get(mode, "Arcade")
        self.map_text = MAP_NAMES[map_id]
        self.cached_walls = [[self.map_data.grid[r][c] == '%' for c in range(self.map_data.cols)] for r in range(self.map_data.rows)]
        self.last_step = pygame.time.get_ticks()
        self.status = "PLAYING"
        self.paused = False #trạng thái tạm dừng
        self.btn_pause_rect = None
        self.btn_restart_rect = None

        # Cấu hình AI: Mode 2 là Pacman AI tự chơi, Mode 1 là Người chơi vs Ma AI
        self.mode = mode
        self.is_ai_pacman = (mode == 2)
        if self.is_ai_pacman:
            # depth=1 tương đương nhìn trước 4 ply (Pacman + 3 con ma), tính toán cực nhanh (<2ms) không giật lag
            self.pacman_agent = AlphaBetaAgent(depth=1)
            self.moving = True
        else:
            self.pacman_agent = None
            self.moving = False

        # Khởi tạo ma AI săn đuổi (ChaseGhost từ multiAgents.py)
        self.ghost_agents = [
            ChaseGhost(chase_prob=0.85, seed=i, index=i + 1)
            for i in range(len(self.ghost_pos))
        ]

        width = self.map_data.cols * SIZE
        height = LE_TREN + self.map_data.rows * SIZE + LE_DUOI
        return pygame.display.set_mode((width, height))

    def get_game_state(self):
        """Chuyển đổi trạng thái màn hình hiện tại thành GameState để AI tính toán"""
        layout = ScreenLayout(self.map_data, self.pacman_pos, self.ghost_pos, self.cached_walls)
        state = GameState(layout)
        state.score = self.score
        now = pygame.time.get_ticks()
        if self.scared_end and now < self.scared_end:
            rem = max(1, int((self.scared_end - now) / 1000 * 2))
            state.scared_timers = [rem if s == SCARED else 0 for s in self.ghost_state]
        else:
            state.scared_timers = [0] * len(self.ghost_pos)
        return state

    def handle_event(self, event):
        # 1 BẮT PHÍM BẤM
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "BACK"

            # phím SPACE:bật tắt tạm dừng
            elif event.key == pygame.K_SPACE:
                self.paused = not self.paused

            # phím R : restart
            elif event.key == pygame.K_r:
                self.start(self.mode,self.map_id)

            # phím S: chạy 1 bước khi đang tạm dừng
            elif event.key == pygame.K_s:
                if self.paused and self.status == "PLAYING":
                    self.step_once()

            # Nếu là chế độ người chơi (Mode != 2) thì nhận phím bấm
            elif not self.is_ai_pacman and event.key in MOVES:
                self.pacman_dir = MOVES[event.key]
                self.moving = True

        # 2 BẮT CLICK CHUỘT VÀO CÁC NÚT TRÊN MÀN HÌNH
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
             #click pause / resume
            if self.btn_pause_rect and self.btn_pause_rect.collidepoint(mouse_pos):
                self.paused = not self.paused

            #click nút STEP
            elif self.btn_step_rect and self.btn_step_rect.collidepoint(mouse_pos):
                if self.paused and self.status == "PLAYING":
                    self.step_once()
            # Click nút RESTART
            elif self.btn_restart_rect and self.btn_restart_rect.collidepoint(mouse_pos):
                self.start(self.mode, self.map_id)
        return None

    def can_go(self, direction):
        x = self.pacman_pos[0] + direction[0]
        y = self.pacman_pos[1] + direction[1]
        return self.map_data.cell(x, y) not in ('%', '-')

    def step_pacman(self):
        # Nếu là Pacman AI (Mode 2), tự động hỏi AlphaBetaAgent nước đi tối ưu
        if self.is_ai_pacman:
            state = self.get_game_state()
            action = self.pacman_agent.get_action(state)
            if action and action in ACTION_TO_DIR and action != 'STOP':
                self.pacman_dir = ACTION_TO_DIR[action]
                self.moving = True
            else:
                self.moving = False


        if not self.moving:
            return
        if self.can_go(self.pacman_dir):
            self.pacman_pos[0] += self.pacman_dir[0]
            self.pacman_pos[1] += self.pacman_dir[1]
            x, y = self.pacman_pos

            # Chỉ phạt trừ điểm khi Pacman bước vào ô bùn lầy '~'
            if self.map_data.cell(x, y) == '~':
                self.score -= 5  # Bị phạt 3 điểm vì lội bùn
                
            if self.map_data.cell(x, y) == 'o':
                self.start_scared()
            self.score += self.map_data.eat(x, y)
            self.check_collision()

    def start_scared(self):
        """Pacman vừa ăn goal1: ma NORMAL -> SCARED, đếm giờ lại từ đầu."""
        self.scared_end = pygame.time.get_ticks() + SCARED_SECONDS[self.map_id] * 1000
        self.eat_combo = 0
        for i in range(len(self.ghost_state)):
            if self.ghost_state[i] == NORMAL:    # ma đang EATEN thì cứ về nhà tiếp
                self.ghost_state[i] = SCARED

    def update_scared(self, now):
        """Hết giờ thì mọi ma SCARED trở lại NORMAL."""
        if self.scared_end and now >= self.scared_end:
            self.scared_end = 0
            for i in range(len(self.ghost_state)):
                if self.ghost_state[i] == SCARED:
                    self.ghost_state[i] = NORMAL

    def check_collision(self):
        """Pacman và ma ở cùng một ô."""
        for i, pos in enumerate(self.ghost_pos):
            if pos != self.pacman_pos:
                continue
            if self.ghost_state[i] == SCARED:
                self.eat_combo += 1
                self.score += GHOST_POINTS * self.eat_combo      # 200, 400, 600
                self.ghost_state[i] = EATEN
                home = self.map_data.g_start[i]                  # ô xuất phát của chính con ma đó
                self.ghost_path[i] = self.map_data.find_path(tuple(pos), home)
            # elif NORMAL: ma bắt được Pacman -> xử lý thua (làm sau)

    def step_eaten_ghosts(self):
        """Mỗi bước, ma EATEN đi 1 ô trên đường về nhà; tới nơi thì thành NORMAL."""
        for i, state in enumerate(self.ghost_state):
            if state != EATEN:
                continue
            if self.ghost_path[i]:
                x, y = self.ghost_path[i].pop(0)
                self.ghost_pos[i] = [x, y]
            if not self.ghost_path[i]:
                self.ghost_state[i] = NORMAL

    def ghost_art(self, i, now):
        """Chọn hình vẽ cho con ma thứ i."""
        normal_art = GHOST_ARTS[i % len(GHOST_ARTS)]
        state = self.ghost_state[i]
        if state == EATEN:
            return GHOST_ATE
        if state == SCARED:
            remaining = self.scared_end - now
            if remaining <= BLINK_MS:
                # chia 1 giây cuối thành 6 khoảng: EAT, thường, EAT, thường, EAT, thường
                phase = (BLINK_MS - remaining) * 6 // BLINK_MS
                if phase % 2 == 1:
                    return normal_art
            return GHOST_EAT
        return normal_art

    def check_end(self):
        """Gọi sau MỖI lần Pacman hoặc ma di chuyển."""
        px, py = self.pacman_pos
        """""if any((g[0], g[1]) == (px, py) for g in self.ghost_pos):   # thua xét trước
            self.status = "DYING"""
        #ban đầu ăn ma là chết luôn dù đang ở trạng thái gì , đã saurw thành ăn ma ở trạng thái normal mới chít
        px, py = self.pacman_pos
        #chỉ bị ma bắt nếu ở trạng thái normal
        is_caught = any((g[0], g[1]) == (px, py) and self.ghost_state[i] == NORMAL 
        for i, g in enumerate(self.ghost_pos))
        if is_caught:
            self.status = "DYING"
            self.dying_start = pygame.time.get_ticks()
        elif self.map_data.goal_left() == 0:
            self.status = "WIN"
    
    def update(self):
        now = pygame.time.get_ticks()
        self.update_scared(now)
        if self.status == "DYING":                    # đang nhấp nháy
            if now - self.dying_start >= P_BLINKS * 2 * P_BLINK:
                self.status = "LOSE"
            return
        if self.status != "PLAYING":
            return
        #Nếu đang dừng thì ko tự động đi bước tiếp thep
        if self.paused:
            return
        if now - self.last_step < STEP_MS:
            return
        self.last_step = now
        self.step_once() #gọi hàm 1 bước ở dưới

        
    def step_once(self):
        """Thực hiện 1 bước của pacman và ghost"""
        if self.status != "PLAYING":                  # WIN / LOSE: đứng yên
            return
        self.step_pacman()
        self.step_eaten_ghosts()
        self.step_ghosts()
        self.check_collision()
        self.check_end()



    def step_ghosts(self):
        """Cho ma AI bước đi: dùng ChaseGhost từ multiAgents khi bình thường, né Pacman khi sợ"""
        state = self.get_game_state()
        import random
        for i, g_state in enumerate(self.ghost_state):
            if g_state == EATEN:
                continue
            gx, gy = self.ghost_pos[i]
            legal_moves = []
            for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                if self.map_data.cell(gx + dx, gy + dy) != '%':
                    legal_moves.append((dx, dy))
            if not legal_moves:
                continue

            if g_state == SCARED:
                # Khi ma sợ: cố gắng chạy xa khỏi Pacman
                px, py = self.pacman_pos
                best_moves = []
                max_d = -1
                for dx, dy in legal_moves:
                    d = abs(gx + dx - px) + abs(gy + dy - py)
                    if d > max_d:
                        max_d = d
                        best_moves = [(dx, dy)]
                    elif d == max_d:
                        best_moves.append((dx, dy))
                chosen = random.choice(best_moves)
                self.ghost_pos[i] = [gx + chosen[0], gy + chosen[1]]
            else:
                # Khi bình thường: Ma dùng ChaseGhost từ multiAgents.py để săn đuổi Pacman!
                moved = False
                if i < len(self.ghost_agents):
                    g_action = self.ghost_agents[i].get_action(state, agent_index=i + 1)
                    if g_action in ACTION_TO_DIR:
                        dx, dy = ACTION_TO_DIR[g_action]
                        if (dx, dy) in legal_moves:
                            self.ghost_pos[i] = [gx + dx, gy + dy]
                            moved = True
                if not moved:
                    chosen_dx, chosen_dy = random.choice(legal_moves)
                    self.ghost_pos[i] = [gx + chosen_dx, gy + chosen_dy]



                
    def draw(self, screen):
        screen.fill(COLORS['BG'])
        draw_map(screen, self.map_data, self.wall_surf)
        now = pygame.time.get_ticks()
        for i, pos in enumerate(self.ghost_pos):
            draw_g(screen, pos, self.ghost_art(i, now))
        show_pacman = True
        if self.status == "DYING":
            elapsed = pygame.time.get_ticks() - self.dying_start
            show_pacman = (elapsed // BLINK_MS) % 2 == 1   # pha chẵn ẩn, pha lẻ hiện
        if show_pacman:
            draw_p(screen, self.pacman_pos, self.pacman_dir)
        draw_hud(screen, self.map_data, self.mode_text, self.map_text, self.score,
                 self.font_big, self.font_small, self.font_score)
        w, h = screen.get_width(), screen.get_height()
        if self.status == "LOSE":
            draw_box_winlose(screen, "YOU LOSE", "DIU CAN ĐU ỊT",
                             self.font_bigger, self.font_score, w, h)
        elif self.status == "WIN":
            draw_box_winlose(screen, "YOU WIN", "THẮNG GÒI ĐÓ, VUI HĂM",
                             self.font_bigger, self.font_score, w, h)
                                     # =========================================================
        # VẼ 3 NÚT ĐIỀU KHIỂN CÁCH ĐỀU NHAU Ở DƯỚI BẢN ĐỒ
        # =========================================================
        screen_w = screen.get_width()
        map_bottom = LE_TREN + self.map_data.rows * SIZE
        
        btn_w = 140   # Chiều rộng mỗi nút
        btn_h = 28    # Chiều cao mỗi nút
        btn_y = map_bottom + (LE_DUOI - btn_h) // 2  # Căn giữa theo chiều dọc dải dưới
        
        # Tính khoảng cách cách đều 4 phía
        gap = (screen_w - 3 * btn_w) // 4

        # 1. NÚT 1: PAUSE / RESUME [SPACE]
        x1 = gap
        self.btn_pause_rect = pygame.Rect(x1, btn_y, btn_w, btn_h)
        pause_text = "RESUME [Space]" if self.paused else "PAUSE [Space]"
        pause_color = (230, 120, 30) if self.paused else (50, 50, 60) # Cam khi dừng, Xám khi chạy
        pygame.draw.rect(screen, pause_color, self.btn_pause_rect, border_radius=6)
        pygame.draw.rect(screen, COLORS['W'], self.btn_pause_rect, width=1, border_radius=6) # Viền trắng
        txt_pause = self.font_small.render(pause_text, True, COLORS['W'])
        screen.blit(txt_pause, txt_pause.get_rect(center=self.btn_pause_rect.center))

        # 2. NÚT 2: STEP [S]
        x2 = gap * 2 + btn_w
        self.btn_step_rect = pygame.Rect(x2, btn_y, btn_w, btn_h)
        step_color = (40, 100, 200) if self.paused else (40, 40, 45) # Xanh sáng khi pause, xám mờ khi đang chạy
        pygame.draw.rect(screen, step_color, self.btn_step_rect, border_radius=6)
        pygame.draw.rect(screen, COLORS['W'] if self.paused else (100, 100, 100), self.btn_step_rect, width=1, border_radius=6)
        txt_step = self.font_small.render("STEP [S]", True, COLORS['W'] if self.paused else (150, 150, 150))
        screen.blit(txt_step, txt_step.get_rect(center=self.btn_step_rect.center))

        # 3. NÚT 3: RESTART [R]
        x3 = gap * 3 + btn_w * 2
        self.btn_restart_rect = pygame.Rect(x3, btn_y, btn_w, btn_h)
        pygame.draw.rect(screen, (180, 45, 45), self.btn_restart_rect, border_radius=6) # Đỏ
        pygame.draw.rect(screen, COLORS['W'], self.btn_restart_rect, width=1, border_radius=6)
        txt_restart = self.font_small.render("RESTART [R]", True, COLORS['W'])
        screen.blit(txt_restart, txt_restart.get_rect(center=self.btn_restart_rect.center))