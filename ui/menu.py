import os
import pygame
import sys
from ui.pixel_assets import COLORS

b_width = 400
b_height = 50

FONT_HEADING = "04B_30__.TTF"
FONT_MAIN = "SVN-Determination Sans.otf"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_font(filename, size):
    for folder in ("assets/fonts", "assets"):
        path = os.path.join(BASE_DIR, folder, filename)
        if os.path.isfile(path):
            return pygame.font.Font(path, size)
    return pygame.font.SysFont("arial", size, bold=True)

class Menu:
    def __init__ (self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.title_heading_1 = load_font(FONT_HEADING, 56)
        self.font_title = load_font(FONT_MAIN, 48)
        self.font_button = load_font(FONT_MAIN, 24)
        self.font_button_small = load_font(FONT_MAIN, 20)
        self.font_sub = load_font(FONT_MAIN, 16)

        self.current_state = 1
        self.selected_mode = None
        self.selected_map = None

        self.option1 = [
            "Start",
            "Exit"
        ]
        self.option2 = [
            "Player vs AI Ghosts\nNgười chơi vs Ma AI", 
            "AI vs AI Autoplay\nPacman AI vs Ma AI", 
            "Discovery Mode\nLuyện tập không ma", 
            "Back"
        ]
        self.option3 = [
            "Tiny Maze", 
            "Medium Maze", 
            "Big Maze",
            "Back"
        ]

        self.selected_index = 0

    def reset(self):
        self.current_state = 1
        self.selected_index = 0
    
    def draw_box (self, options, start_y):
        for i, text in enumerate(options):
            is_selected = (i == self.selected_index)
            text_color = COLORS.get('W') if is_selected else COLORS.get('Y')

            box_x = (self.width - b_width) // 2
            box_y = start_y + i*70
            box_rect = pygame.Rect (box_x, box_y, b_width, b_height)

            box_bg_color = COLORS.get('BG') if not is_selected else COLORS.get("BL")

            pygame.draw.rect(self.screen, box_bg_color, box_rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS.get('BL'), box_rect, 2, border_radius=8)

            lines = text.split("\n")

            if len(lines) == 1:
                surf = self.font_button.render(lines[0], True, text_color)
                self.screen.blit(surf, surf.get_rect(center=box_rect.center))
            else:
                s1 = self.font_button.render(lines[0], True, text_color)
                s2 = self.font_sub.render(lines[1], True, text_color)
                self.screen.blit(s1, s1.get_rect(center=(box_rect.centerx, box_rect.y + 15)))
                self.screen.blit(s2, s2.get_rect(center=(box_rect.centerx, box_rect.y + 36)))

    def get_box_rects(self):
        options = {1: self.option1, 2: self.option2, 3: self.option3}[self.current_state]
        start_y = 280 if self.current_state == 1 else 150
        rects = []
        for i in range(len(options)):
            x = (self.width - b_width) // 2
            rects.append(pygame.Rect(x, start_y + i * 70, b_width, b_height))
        return rects

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
            title_rect = title_surf.get_rect(center = (self.width//2, 100))
            self.screen.blit(title_surf, title_rect)

            self.draw_box(self.option2, start_y = 150)
        elif self.current_state == 3:
            title_surf = self.font_title.render("CHỌN KIỂU MAP", True, heading_color)
            title_rect = title_surf.get_rect(center = (self.width//2, 100))
            self.screen.blit(title_surf, title_rect)

            self.draw_box(self.option3, start_y = 150)

    def handle_input(self, event):
            if event.type == pygame.KEYDOWN:
                current_options = (
                    self.option1 if self.current_state == 1 else
                    self.option2 if self.current_state == 2 else
                    self.option3
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
            elif event.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(self.get_box_rects()):
                    if rect.collidepoint(event.pos):
                        self.selected_index = i

            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(self.get_box_rects()):
                    if rect.collidepoint(event.pos):
                        self.selected_index = i
                        return self.handle_input(
                            pygame.event.Event(pygame.KEYDOWN, key = pygame.K_RETURN)
                        )
                        

            return None