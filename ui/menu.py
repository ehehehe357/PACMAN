import pygame
import sys
from ui.pixel_assets import COLORS

b_width = 400
b_height = 50

def __init__ (self, screen, width, height):
    self.screen = screen
    self.width = width
    self.height = height
    self.title_heading_1 = pygame.font.SysFont("04B_30_.TTF", 56, bold=False, italic=False)
    self.font_title = pygame.font.SysFont("SVN-Determination Sans.otf", 48, bold=True, italic=False)
    self.font_button = pygame.font.SysFont("SVN-Determination Sans.otf", 24, bold=False, italic=False)

    self.current_state = 1
    self.select_mode = None
    self.select_map = None

    self.option1 = [
        "Start",
        "Exit"
    ]
    self.option2 = [
        "Discovery Mode/nKhông có ma", 
        "Survival Mode/nBa ma săn đuổi", 
        "Counter-Attack Mode/nSăn ma", 
        "Back"
    ]
    self.option3 = [
        "Tiny Maze", 
        "Medium Maze", 
        "Big Maze",
        "Back"
    ]

    self.select_index = 0

def draw_box (self, options, start_y):
    for i, options in enumerate(options):
        is_selected = (i == self.select_index)
        text_color = COLORS.get('Y') if not is_selected else COLORS.get('W')

        opt_surf = self.font_button.render(options, text_color)

        box_width, box_height = b_width, b_height
        box_x = (self.width - box_width) // 2
        box_y = start_y + i*70
        box_rect = pygame.Rect (box_x, box_y, box_width, box_height)

        box_bg_color = COLORS.get('BG') if not is_selected else COLORS.get("BL")
        border_color = COLORS.get('BL')

        pygame.draw.rect(self.screen, box_bg_color, box_rect, border_radius=8)
        pygame.draw.rect(self.screen, border_color, box_rect, 2, border_radius=8)

        opt_rect = opt_surf.get_rect(center=box_rect.center)
        self.screen.blit(opt_surf, opt_rect)

def draw(self):
    bg_color = COLORS.get('BG')
    self.screen.fill(bg_color)

    heading_color = COLORS.get('Y')

    if self.current_state == 1:
        title_surf = self.title_heading_1.render("PACMAN", True, heading_color)
        title_rect = title_surf.get_rect(center = (self.width//2, 150))
        self.screen.blit(title_surf, title_rect)

        self.draw_box(self.option1, start_y = 280)

    elif self.current_state == 2:
        title_surf = self.font_title.render("CHỌN CHẾ ĐỘ", True, heading_color)
        title_rect = title_surf.get_rect(center = (self.width//2, 150))
        self.screen.blit(title_surf, title_rect)

        self.draw_box(self.option2, start_y = 220)
    elif self.current_state == 3:
        title_surf = self.font_title.render("CHỌN KIỂU MAP", True, heading_color)
        title_rect = title_surf.get_rect(center = (self.width//2, 150))
        self.screen.blit(title_surf, title_rect)

        self.draw_box(self.option3, start_y = 220)

def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            current_options = (
                self.options_giao_dien_1 if self.current_state == 1 else
                self.options_giao_dien_2 if self.current_state == 2 else
                self.options_giao_dien_3
            )

            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(current_options)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(current_options)
            elif event.key == pygame.K_RETURN:
                # Xử lý logic khi bấm Enter tùy theo giao diện hiện tại
                
                # --- XỬ LÝ GIAO DIỆN 1 ---
                if self.current_state == 1:
                    if self.selected_index == 0: # Start
                        self.current_state = 2   # Chuyển qua giao diện 2 (Chọn mode)
                        self.selected_index = 0
                    elif self.selected_index == 1: # Exit
                        return "EXIT"

                # --- XỬ LÝ GIAO DIỆN 2 ---
                elif self.current_state == 2:
                    if self.selected_index == 3: # Nút quay lại
                        self.current_state = 1   # Về giao diện 1
                        self.selected_index = 0
                    else:                        # Chọn 1 trong 3 Mode
                        self.selected_mode = self.selected_index + 1
                        self.current_state = 3   # Chuyển qua giao diện 3 (Chọn map)
                        self.selected_index = 0

                # --- XỬ LÝ GIAO DIỆN 3 ---
                elif self.current_state == 3:
                    if self.selected_index == 3: # Nút quay lại
                        self.current_state = 2   # Về giao diện 2
                        self.selected_index = 0
                    else:                        # Chọn 1 trong 3 Map
                        self.selected_map = self.selected_index + 1
                        # Hoàn tất chọn cả Mode và Map, trả về kết quả để main.py bắt đầu game
                        return {
                            "action": "START_GAME",
                            "mode": self.selected_mode,
                            "map": self.selected_map
                        }
        return None