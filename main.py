import pygame
import sys

# Import trực tiếp các hàm từ file ui/menu.py của bạn
from ui import menu

# --- KHỞI TẠO MÔI TRƯỜNG PYGAME ---
pygame.init()
WIDTH, HEIGHT = 600, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pacman Arcade")

clock = pygame.time.Clock()

# --- TẠO LỚP QUẢN LÝ TRẠNG THÁI MENU ---
class MenuState:
    def __init__(self):
        # Gọi hàm khởi tạo gốc từ ui/menu.py
        menu.__init__(self, screen, WIDTH, HEIGHT)
        
        # Gắn thêm hàm draw_box vào đối tượng để self.draw_box() hoạt động được
        self.draw_box = lambda options, start_y: menu.draw_box(self, options, start_y)
        
        # Đồng bộ hóa các tên biến tùy chọn để khớp với hàm xử lý phím
        if hasattr(self, 'option1'):
            self.options_giao_dien_1 = self.option1
        if hasattr(self, 'options2'):
            self.options_giao_dien_2 = self.option2
        if hasattr(self, 'options3'):
            self.options_giao_dien_3 = self.option3
            
        # Đồng bộ tên biến tiêu đề nếu bị lệch chính tả
        if hasattr(self, 'title_heading_1') and not hasattr(self, 'tittle_headline_1'):
            self.tittle_headline_1 = self.title_heading_1

    def draw(self):
        menu.draw(self)

    def handle_input(self, event):
        return menu.handle_input(self, event)

# Khởi tạo đối tượng menu
game_menu = MenuState()

# --- VÒNG LẶP CHÍNH CỦA GAME (GAME LOOP) ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # Xử lý phím bấm
        result = game_menu.handle_input(event)
        
        if result == "EXIT":
            running = False
        elif isinstance(result, dict) and result.get("action") == "START_GAME":
            print(f"--> ĐÃ CHỌN XONG! Chế độ (Mode): {result['mode']} | Bản đồ (Map): {result['map']}")

    # Vẽ menu lên màn hình
    game_menu.draw()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()