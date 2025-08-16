import sys
import os
import pygame
import random
import json
import time

# 尝试导入OpenCV库用于视频播放
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

# 尝试导入MoviePy库用于视频播放
try:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    try:
        from moviepy.editor import VideoFileClip
        MOVIEPY_AVAILABLE = True
    except ImportError:
        MOVIEPY_AVAILABLE = False
        VideoFileClip = None

from enum import Enum, auto


# 游戏设置
game_settings = {
    "music_volume": 0.5,
    "zombie_spawn_rate_modifier": 1.0,
    "bullet_storage": 0,
    "shop_costs": {
        "life": 10,
        "custom_bullet": 2,
        "turret": 30,
        "shuffle": 15
    }
}

# 资源路径解决方案
def resource_path(relative_path):
    """ 获取资源的绝对路径，适用于开发环境和PyInstaller环境 """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 初始化pygame
pygame.init()

# 游戏状态
class GameState(Enum):
    SPLASH_SCREEN = auto()
    VERSION_INFO = auto()
    ACCOUNT_SELECTION = auto()
    MAIN_MENU = auto()
    CLASSIC_MODE_SELECTION = auto()
    BATTLE_MODE_SELECTION = auto()
    LEVEL_SELECTION = auto()
    BATTLE_LEVEL_SELECTION = auto()
    PLAYING = auto()
    BATTLE_MODE_PLAYING = auto()
    LEVEL_COMPLETE = auto()
    GAME_OVER = auto()
    ENDLESS_PLAYING = auto()
    BATTLE_MODE_ENDLESS_PLAYING = auto()
    ENDLESS_GAMEOVER = auto()
    QUIT = auto()

# 游戏常量
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
TRIPLE_MATCH_WIDTH = 400
TRIPLE_MATCH_HEIGHT = 400
ZOMBIE_AREA_WIDTH = 800
ZOMBIE_AREA_HEIGHT = 400

# 加载音效
sounds = {}
try:
    sounds['eliminate'] = pygame.mixer.Sound(resource_path('ogg/vi.mp3'))
except:
    sounds['eliminate'] = None
try:
    sounds['life_lost'] = pygame.mixer.Sound(resource_path('ogg/de.mp3'))
except:
    sounds['life_lost'] = None

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
DARK_GREEN = (0, 100, 0)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GREEN = (144, 238, 144)

# 设置屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("一哈基三米")

# 初始化字体
pygame.font.init()
font_path = None
font_name = None

def find_font():
    global font_path, font_name
    sys_font_names = ['Microsoft YaHei', 'SimHei', 'KaiTi', 'FangSong', 'wqy-zenhei', 'Noto Sans CJK SC', 'Droid Sans Fallback']
    for name in sys_font_names:
        if name in pygame.font.get_fonts():
            font_name = name
            return
    font_file_paths = ['/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 'C:/Windows/Fonts/msyh.ttc', 'C:/Windows/Fonts/simhei.ttf', '/System/Library/Fonts/STHeiti Medium.ttc']
    for path in font_file_paths:
        if os.path.exists(path):
            font_path = path
            return

find_font()

if font_path:
    font_small = pygame.font.Font(font_path, 24)
    font_medium = pygame.font.Font(font_path, 36)
    font_large = pygame.font.Font(font_path, 48)
elif font_name:
    font_small = pygame.font.SysFont(font_name, 24)
    font_medium = pygame.font.SysFont(font_name, 36)
    font_large = pygame.font.SysFont(font_name, 48)
else:
    font_small = pygame.font.SysFont('sans', 24)
    font_medium = pygame.font.SysFont('sans', 36)
    font_large = pygame.font.SysFont('sans', 48)

# 加载三消元素图片并调整大小
try:
    cell_size = TRIPLE_MATCH_WIDTH // 8
    element1 = pygame.image.load(resource_path("imgs/tree/1.png")).convert_alpha()
    element1 = pygame.transform.scale(element1, (cell_size, cell_size))
    element2 = pygame.image.load(resource_path("imgs/tree/2.png")).convert_alpha()
    element2 = pygame.transform.scale(element2, (cell_size, cell_size))
    element3 = pygame.image.load(resource_path("imgs/tree/3.png")).convert_alpha()
    element3 = pygame.transform.scale(element3, (cell_size, cell_size))
    elements = [element1, element2, element3]
except Exception as e:
    print(f"加载图片失败: {e}")
    cell_size = TRIPLE_MATCH_WIDTH // 8
    element1 = pygame.Surface((cell_size, cell_size)); element1.fill(RED)
    element2 = pygame.Surface((cell_size, cell_size)); element2.fill(GREEN)
    element3 = pygame.Surface((cell_size, cell_size)); element3.fill(BLUE)
    elements = [element1, element2, element3]

# 用户数据文件
USER_DATA_FILE = "user_data.json"

def load_user_data():
    if not os.path.exists(USER_DATA_FILE): return {}
    try:
        with open(USER_DATA_FILE, "r") as f:
            data = json.load(f)
            return data
    except json.JSONDecodeError: return {}

def save_user_data(data):
    with open(USER_DATA_FILE, "w") as f: json.dump(data, f, indent=4)

class Button:
    def __init__(self, x, y, width, height, text, color, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surf = font_medium.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    def is_clicked(self, pos): return self.rect.collidepoint(pos)


def splash_screen():
    """开屏页面 - 显示3秒或按任意键跳过"""
    start_time = pygame.time.get_ticks()
    while True:
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - start_time) // 1000
        
        # 如果超过3秒，自动进入下一个页面
        if elapsed_time >= 3:
            return GameState.VERSION_INFO
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GameState.QUIT
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                # 按任意键或点击鼠标跳过
                return GameState.VERSION_INFO
        
        screen.fill(WHITE)
        
        # 显示版本号
        version_text = font_medium.render("版本 3.2beta-0809", True, BLACK)
        screen.blit(version_text, (SCREEN_WIDTH // 2 - version_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        
        # 显示大字游戏名称
        title_font = pygame.font.Font(font_path, 72) if font_path else pygame.font.SysFont(font_name or 'sans', 72)
        title_text = title_font.render("一哈基三米", True, BLACK)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        
        # 显示开发者信息
        developer_text = font_medium.render("哔哩哔哩  我就是仁菜  开发", True, BLACK)
        screen.blit(developer_text, (SCREEN_WIDTH // 2 - developer_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))
        
        pygame.display.flip()


def version_info_screen():
    """版本信息页面 - 显示更新介绍"""
    back_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50, "进入游戏", GREEN)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GameState.QUIT
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.is_clicked(event.pos):
                    return GameState.ACCOUNT_SELECTION
            elif event.type == pygame.KEYDOWN:
                # 按任意键也可以进入游戏
                return GameState.ACCOUNT_SELECTION
        
        screen.fill(WHITE)
        
        # 显示版本号
        version_text = font_large.render("版本 3.2beta-0809", True, BLACK)
        screen.blit(version_text, (SCREEN_WIDTH // 2 - version_text.get_width() // 2, 100))
        
        # 显示更新介绍标题
        update_title = font_medium.render("更新介绍", True, BLACK)
        screen.blit(update_title, (SCREEN_WIDTH // 2 - update_title.get_width() // 2, 200))
        
        # 显示更新内容
        update_content = [
            "• 加入战斗模式",
            "• 修复bug"
        ]
        
        y_offset = 280
        for line in update_content:
            content_text = font_small.render(line, True, BLACK)
            screen.blit(content_text, (SCREEN_WIDTH // 2 - content_text.get_width() // 2, y_offset))
            y_offset += 40
        
        back_button.draw(screen)
        pygame.display.flip()


def account_selection_screen():
    user_data = load_user_data()
    creating_user = False
    new_username = ""
    while True:
        buttons = []
        users = list(load_user_data().keys())
        y_offset = 150
        for i, user in enumerate(users): buttons.append(Button(SCREEN_WIDTH // 2 - 150, y_offset + i * 60, 300, 50, user, LIGHT_BLUE))
        new_user_button = Button(SCREEN_WIDTH // 2 - 150, y_offset + len(users) * 60, 300, 50, "创建新账号", GREEN)
        input_box_y = y_offset + (len(users) + 1) * 60
        input_box = pygame.Rect(SCREEN_WIDTH // 2 - 150, input_box_y, 300, 50)
        confirm_button = Button(SCREEN_WIDTH // 2 - 150, input_box_y + 60, 140, 50, "确认", GREEN)
        cancel_button = Button(SCREEN_WIDTH // 2 + 10, input_box_y + 60, 140, 50, "取消", RED)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return None, GameState.QUIT
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not creating_user:
                    if new_user_button.is_clicked(event.pos): creating_user = True; new_username = ""
                    for i, button in enumerate(buttons):
                        if button.is_clicked(event.pos): return users[i], GameState.MAIN_MENU
                else:
                    if confirm_button.is_clicked(event.pos):
                        if new_username and new_username not in user_data:
                            user_data[new_username] = {"level": 1}; save_user_data(user_data); return new_username, GameState.MAIN_MENU
                    if cancel_button.is_clicked(event.pos): creating_user = False; new_username = ""
            if event.type == pygame.KEYDOWN and creating_user:
                if event.key == pygame.K_RETURN:
                    if new_username and new_username not in user_data:
                        user_data[new_username] = {"level": 1}; save_user_data(user_data); return new_username, GameState.MAIN_MENU
                elif event.key == pygame.K_BACKSPACE: new_username = new_username[:-1]
                elif event.unicode.isprintable(): new_username += event.unicode
        screen.fill(WHITE)
        title_text = font_large.render("选择账号", True, BLACK)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
        if not creating_user:
            for button in buttons: button.draw(screen)
            new_user_button.draw(screen)
        else:
            create_text = font_medium.render("输入新用户名:", True, BLACK)
            screen.blit(create_text, (input_box.x, input_box.y - 40))
            lang_tip_text = font_small.render("仅支持英文输入", True, GRAY)
            screen.blit(lang_tip_text, (input_box.x, input_box.y + 55))
            pygame.draw.rect(screen, LIGHT_BLUE, input_box, 2)
            input_text_surf = font_medium.render(new_username, True, BLACK)
            screen.blit(input_text_surf, (input_box.x + 5, input_box.y + 5))
            confirm_button.draw(screen)
            cancel_button.draw(screen)
        pygame.display.flip()

def main_menu_screen(username, current_level):
    switch_button = Button(50, SCREEN_HEIGHT - 180, 200, 50, "切换账号", LIGHT_BLUE)
    quit_button = Button(50, SCREEN_HEIGHT - 110, 200, 50, "退出游戏", RED)
    classic_mode_button = Button(SCREEN_WIDTH - 250, SCREEN_HEIGHT - 180, 200, 50, "经典玩法", GREEN)
    battle_mode_button = Button(SCREEN_WIDTH - 250, SCREEN_HEIGHT - 110, 200, 50, "战斗模式", GREEN)
    volume_slider = pygame.Rect(SCREEN_WIDTH // 2 - 150, 300, 300, 20)
    spawn_rate_slider = pygame.Rect(SCREEN_WIDTH // 2 - 150, 400, 300, 20)
    dragging_volume = False
    dragging_spawn_rate = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return GameState.QUIT, current_level, None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if switch_button.is_clicked(event.pos): return GameState.ACCOUNT_SELECTION, 1, None
                    if quit_button.is_clicked(event.pos): return GameState.QUIT, current_level, None
                    if classic_mode_button.is_clicked(event.pos): return GameState.CLASSIC_MODE_SELECTION, current_level, None
                    if battle_mode_button.is_clicked(event.pos): return GameState.BATTLE_MODE_SELECTION, current_level, None
                    if volume_slider.collidepoint(event.pos): dragging_volume = True
                    if spawn_rate_slider.collidepoint(event.pos): dragging_spawn_rate = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: dragging_volume = False; dragging_spawn_rate = False
            if event.type == pygame.MOUSEMOTION:
                if dragging_volume:
                    pos_x = event.pos[0]
                    game_settings["music_volume"] = max(0.0, min(1.0, (pos_x - volume_slider.x) / volume_slider.width))
                    pygame.mixer.music.set_volume(game_settings["music_volume"])
                if dragging_spawn_rate:
                    pos_x = event.pos[0]
                    game_settings["zombie_spawn_rate_modifier"] = max(0.5, min(4.0, ((pos_x - spawn_rate_slider.x) / spawn_rate_slider.width) * 3.5 + 0.5))
        screen.fill(WHITE)
        title_text = font_large.render(f"欢迎, {username}", True, BLACK)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
        switch_button.draw(screen)
        quit_button.draw(screen)
        classic_mode_button.draw(screen)
        battle_mode_button.draw(screen)
        volume_text = font_medium.render(f"背景音量: {int(game_settings['music_volume'] * 100)}%", True, BLACK)
        screen.blit(volume_text, (volume_slider.x, volume_slider.y - 40))
        pygame.draw.rect(screen, GRAY, volume_slider)
        volume_handle_pos = volume_slider.x + int(volume_slider.width * game_settings["music_volume"])
        pygame.draw.rect(screen, BLUE, (volume_handle_pos - 5, volume_slider.y - 5, 10, 30))
        spawn_rate_text = font_medium.render(f"僵尸速度: {game_settings['zombie_spawn_rate_modifier']:.2f}x", True, BLACK)
        screen.blit(spawn_rate_text, (spawn_rate_slider.x, spawn_rate_slider.y - 40))
        pygame.draw.rect(screen, GRAY, spawn_rate_slider)
        spawn_rate_handle_pos = spawn_rate_slider.x + int(spawn_rate_slider.width * (game_settings["zombie_spawn_rate_modifier"] - 0.5) / 3.5)
        pygame.draw.rect(screen, BLUE, (spawn_rate_handle_pos - 5, spawn_rate_slider.y - 5, 10, 30))
        pygame.display.flip()

def classic_mode_selection_screen(current_level):
    adventure_button = Button(SCREEN_WIDTH // 2 - 150, 250, 300, 50, "冒险模式", GREEN)
    endless_unlocked = current_level >= len(LEVELS)
    endless_color = GREEN if endless_unlocked else GRAY
    endless_button = Button(SCREEN_WIDTH // 2 - 150, 350, 300, 50, "无尽模式", endless_color)
    back_button = Button(SCREEN_WIDTH // 2 - 150, 450, 300, 50, "返回", LIGHT_BLUE)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return GameState.QUIT, None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if adventure_button.is_clicked(event.pos): return GameState.LEVEL_SELECTION, None
                if endless_unlocked and endless_button.is_clicked(event.pos): return GameState.ENDLESS_PLAYING, None
                if back_button.is_clicked(event.pos): return GameState.MAIN_MENU, None
        screen.fill(WHITE)
        title_text = font_large.render("选择经典玩法", True, BLACK)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
        adventure_button.draw(screen)
        endless_button.draw(screen)
        if not endless_unlocked:
            lock_text = font_small.render("通关冒险模式解锁", True, BLACK)
            screen.blit(lock_text, (endless_button.rect.x, endless_button.rect.y + 60))
        back_button.draw(screen)
        pygame.display.flip()

def battle_mode_selection_screen(current_level):
    adventure_button = Button(SCREEN_WIDTH // 2 - 150, 250, 300, 50, "冒险模式", GREEN)
    endless_unlocked = current_level >= len(BATTLE_LEVELS)
    endless_color = GREEN if endless_unlocked else GRAY
    endless_button = Button(SCREEN_WIDTH // 2 - 150, 350, 300, 50, "无尽模式", endless_color)
    back_button = Button(SCREEN_WIDTH // 2 - 150, 450, 300, 50, "返回", LIGHT_BLUE)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return GameState.QUIT, None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if adventure_button.is_clicked(event.pos): return GameState.BATTLE_LEVEL_SELECTION, None
                if endless_unlocked and endless_button.is_clicked(event.pos): return GameState.BATTLE_MODE_ENDLESS_PLAYING, None
                if back_button.is_clicked(event.pos): return GameState.MAIN_MENU, None
        screen.fill(WHITE)
        title_text = font_large.render("选择战斗模式", True, BLACK)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
        adventure_button.draw(screen)
        endless_button.draw(screen)
        if not endless_unlocked:
            lock_text = font_small.render("通关战斗冒险模式解锁", True, BLACK)
            screen.blit(lock_text, (endless_button.rect.x, endless_button.rect.y + 60))
        back_button.draw(screen)
        pygame.display.flip()

def level_selection_screen(max_unlocked_level, levels_data=None, mode_title="选择关卡", back_state=GameState.MAIN_MENU):
    if levels_data is None: levels_data = LEVELS
    buttons = []
    levels_per_row = 6
    button_width = 150; button_height = 80; h_spacing = 40; v_spacing = 40
    start_x = (SCREEN_WIDTH - (levels_per_row * button_width) - ((levels_per_row - 1) * h_spacing)) // 2
    start_y = 150
    for i in range(len(levels_data)):
        level_num = i + 1
        row = i // levels_per_row; col = i % levels_per_row
        x = start_x + col * (button_width + h_spacing)
        y = start_y + row * (button_height + v_spacing)
        color = GREEN if level_num <= max_unlocked_level else GRAY
        buttons.append(Button(x, y, button_width, button_height, f"第 {level_num} 关", color))
    back_button = Button(50, SCREEN_HEIGHT - 110, 200, 50, "返回", LIGHT_BLUE)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return GameState.QUIT, None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.is_clicked(event.pos): return back_state, None
                for i, button in enumerate(buttons):
                    level_num = i + 1
                    if level_num <= max_unlocked_level and button.is_clicked(event.pos):
                        if mode_title == "选择关卡": return GameState.PLAYING, level_num
                        else: return GameState.BATTLE_MODE_PLAYING, level_num
        screen.fill(WHITE)
        title_text = font_large.render(mode_title, True, BLACK)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
        for button in buttons: button.draw(screen)
        back_button.draw(screen)
        pygame.display.flip()

LEVELS = []
original_levels = [{"zombies": 10, "target_score": 15, "spawn_rate": 180}, {"zombies": 15, "target_score": 30, "spawn_rate": 150}, {"zombies": 20, "target_score": 45, "spawn_rate": 120}, {"zombies": 25, "target_score": 60, "spawn_rate": 100}, {"zombies": 30, "target_score": 75, "spawn_rate": 90}, {"zombies": 35, "target_score": 90, "spawn_rate": 80}, {"zombies": 40, "target_score": 105, "spawn_rate": 70}, {"zombies": 45, "target_score": 120, "spawn_rate": 60}, {"zombies": 50, "target_score": 135, "spawn_rate": 50}, {"zombies": 60, "target_score": 150, "spawn_rate": 40}]
for level_data in original_levels: level_data['type'] = 'score'; level_data['target'] = level_data['target_score']; LEVELS.append(level_data)
for i in range(8): zombie_kills = 30 + i * 10; LEVELS.append({"type": "kill", "target": zombie_kills, "zombies": float('inf'), "spawn_rate": 80 - i * 5})
for _ in range(2): LEVELS.append({"type": "kill", "target": 100, "zombies": float('inf'), "spawn_rate": 60, "spawn_rate_multiplier": 2.0})
match_targets = [10, 20, 30, 40, 50, 55, 60, 65, 70, 75]
for target in match_targets: LEVELS.append({"type": "match", "target": target, "zombies": 10, "spawn_rate": 180})

BATTLE_LEVELS = [{"type": "kill", "target": 5 + i * 5, "zombies": float('inf'), "spawn_rate": 120 - i * 5} for i in range(10)]

class TripleMatchGame:
    def __init__(self, mode='classic'):
        self.grid_size = 8
        self.cell_size = TRIPLE_MATCH_WIDTH // self.grid_size
        self.grid = [[random.randint(0, 2) for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.selected = None
        self.mode = mode
        self.initialize_grid()
    def initialize_grid(self):
        # Regenerate the grid once, unconditionally.
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                self.grid[r][c] = random.randint(0, 2)
        # Then, keep regenerating until the new grid has no initial matches.
        while self.find_matches():
            for r in range(self.grid_size):
                for c in range(self.grid_size): self.grid[r][c] = random.randint(0, 2)
    def draw(self, surface):
        game_area = pygame.Rect(0, SCREEN_HEIGHT - TRIPLE_MATCH_HEIGHT, TRIPLE_MATCH_WIDTH, TRIPLE_MATCH_HEIGHT)
        pygame.draw.rect(surface, GRAY, game_area)
        for i in range(self.grid_size + 1):
            pygame.draw.line(surface, BLACK, (0, SCREEN_HEIGHT - TRIPLE_MATCH_HEIGHT + i * self.cell_size), (TRIPLE_MATCH_WIDTH, SCREEN_HEIGHT - TRIPLE_MATCH_HEIGHT + i * self.cell_size))
            pygame.draw.line(surface, BLACK, (i * self.cell_size, SCREEN_HEIGHT - TRIPLE_MATCH_HEIGHT), (i * self.cell_size, SCREEN_HEIGHT))
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.grid[row][col] != -1: surface.blit(elements[self.grid[row][col]], (col * self.cell_size, SCREEN_HEIGHT - TRIPLE_MATCH_HEIGHT + row * self.cell_size))
        if self.selected:
            row, col = self.selected
            pygame.draw.rect(surface, (255, 255, 0), (col * self.cell_size, SCREEN_HEIGHT - TRIPLE_MATCH_HEIGHT + row * self.cell_size, self.cell_size, self.cell_size), 3)
    def handle_click(self, pos):
        x, y = pos
        if not (x < TRIPLE_MATCH_WIDTH and y > SCREEN_HEIGHT - TRIPLE_MATCH_HEIGHT): self.selected = None; return None
        col = x // self.cell_size
        row = (y - (SCREEN_HEIGHT - TRIPLE_MATCH_HEIGHT)) // self.cell_size
        if not (0 <= row < self.grid_size and 0 <= col < self.grid_size): return None
        if self.selected is None: self.selected = (row, col); return None
        else:
            prev_row, prev_col = self.selected
            if abs(prev_row - row) + abs(prev_col - col) == 1:
                self.swap_elements(prev_row, prev_col, row, col)
                matches = self.find_matches()
                if matches:
                    all_matched_elements = []
                    while matches:
                        for r, c in matches:
                            all_matched_elements.append({'pos': (r, c), 'type': self.grid[r][c]})
                        self.remove_matches(matches)
                        self.apply_gravity()
                        matches = self.find_matches()
                    self.selected = None
                    if self.mode == 'classic':
                        bullets_to_fire = min(len(all_matched_elements), 3)
                        to_add = len(all_matched_elements) // 3
                        return {'bullets': bullets_to_fire, 'ammo': to_add, 'matches_made': 1}
                    else: # battle mode
                        # In battle mode, ammo is gained for shuffle
                        to_add = len(all_matched_elements) // 3
                        return {'projectiles': all_matched_elements, 'matches_made': 1, 'ammo': to_add}
                else: self.swap_elements(prev_row, prev_col, row, col)
            self.selected = None
        return None
    def swap_elements(self, r1, c1, r2, c2): self.grid[r1][c1], self.grid[r2][c2] = self.grid[r2][c2], self.grid[r1][c1]
    def find_matches(self):
        matches = set()
        for r in range(self.grid_size):
            for c in range(self.grid_size - 2):
                if self.grid[r][c] == self.grid[r][c+1] == self.grid[r][c+2] != -1: matches.update([(r, c), (r, c+1), (r, c+2)])
        for c in range(self.grid_size):
            for r in range(self.grid_size - 2):
                if self.grid[r][c] == self.grid[r+1][c] == self.grid[r+2][c] != -1: matches.update([(r, c), (r+1, c), (r+2, c)])
        return list(matches)
    def remove_matches(self, matches):
        for r, c in matches: self.grid[r][c] = -1
    def apply_gravity(self):
        for c in range(self.grid_size):
            empty_slots = []
            for r in range(self.grid_size - 1, -1, -1):
                if self.grid[r][c] == -1: empty_slots.append(r)
                elif empty_slots:
                    new_r = empty_slots.pop(0)
                    self.grid[new_r][c] = self.grid[r][c]
                    self.grid[r][c] = -1
                    empty_slots.append(r)
            for r in empty_slots: self.grid[r][c] = random.randint(0, 2)

class Zombie:
    def __init__(self, x, y):
        self.x = x; self.y = y; self.width = 60; self.height = 80; self.speed = 1; self.health = 1
        try:
            self.image = pygame.image.load(resource_path("imgs/zombie.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except: self.image = None
    def move(self): self.x -= self.speed
    def draw(self, surface):
        if self.image: surface.blit(self.image, (self.x, self.y))
        else: pygame.draw.rect(surface, DARK_GREEN, (self.x, self.y, self.width, self.height))
    def hit(self): self.health -= 1; return self.health <= 0

class AutoTurret:
    def __init__(self, x, y):
        self.x = x; self.y = y; self.width = 50; self.height = 50; self.fire_rate = 1800; self.timer = 0
        try:
            self.image = pygame.image.load(resource_path("imgs/peashooter.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except Exception as e: print(f"加载炮台图片失败: {e}"); self.image = pygame.Surface((self.width, self.height)); self.image.fill(BROWN)
    def update(self, zombie_game):
        self.timer += 1
        if self.timer >= self.fire_rate:
            self.timer = 0
            for row_y in zombie_game.zombie_rows: zombie_game.projectiles.append(Projectile(self.x + self.width, row_y))
    def draw(self, surface): surface.blit(self.image, (self.x, self.y))

class Projectile:
    def __init__(self, x, y, image=None):
        self.x = x; self.y = y; self.speed = 10
        if image: self.image = image
        else:
            try:
                self.image = pygame.image.load(resource_path("imgs/zd.png")).convert_alpha()
                self.image = pygame.transform.scale(self.image, (30, 30))
            except Exception as e: print(f"加载子弹图片 'imgs/zd.png' 失败: {e}"); self.image = pygame.Surface((20, 20)); self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(x, y))
    def move(self): self.rect.x += self.speed
    def draw(self, surface): surface.blit(self.image, self.rect)
    def collide(self, zombie): return self.rect.colliderect(zombie.x, zombie.y, zombie.width, zombie.height)

class ZombieGame:
    def __init__(self, level_data):
        self.zombies = []; self.projectiles = []; self.spawn_timer = 0; self.score = 0
        self.lives = 6; self.level_data = level_data; self.zombies_spawned = 0
        self.zombies_killed = 0
        self.zombie_rows = [SCREEN_HEIGHT - ZOMBIE_AREA_HEIGHT + 60 + i * 80 for i in range(5)]
        self.turrets = []
    def update(self):
        self.spawn_timer += 1
        is_endless = self.level_data.get("zombies") == float('inf')
        is_kill_level = self.level_data.get('type') == 'kill'
        can_spawn = is_endless or is_kill_level or (self.zombies_spawned < self.level_data["zombies"])
        spawn_rate = max(1, self.level_data["spawn_rate"])  # Ensure minimum spawn rate of 1
        if is_endless or is_kill_level:
            spawn_rate = max(1, int(spawn_rate / game_settings["zombie_spawn_rate_modifier"]))
        if self.level_data.get("spawn_rate_multiplier"):
            spawn_rate = max(1, int(spawn_rate / self.level_data["spawn_rate_multiplier"]))
        # Ensure spawn_rate is at least 1 to prevent division by zero or zero spawn rate
        spawn_rate = max(1, spawn_rate)
        if self.spawn_timer >= spawn_rate and can_spawn:
            self.zombies.append(Zombie(SCREEN_WIDTH, random.choice(self.zombie_rows) - 40))
            if not is_endless: self.zombies_spawned += 1
            self.spawn_timer = 0
        for zombie in self.zombies[:]:
            zombie.move()
            if zombie.x + zombie.width <= TRIPLE_MATCH_WIDTH:
                self.lives -= 1
                if sounds['life_lost']: sounds['life_lost'].play()
                self.zombies.remove(zombie)
                if self.lives <= 0: return GameState.GAME_OVER
        for p in self.projectiles[:]:
            p.move()
            if p.rect.left > SCREEN_WIDTH: self.projectiles.remove(p)
            for z in self.zombies[:]:
                if p.collide(z):
                    if z.hit(): self.zombies.remove(z); self.score += 3; self.zombies_killed += 1
                    if p in self.projectiles: self.projectiles.remove(p)
                    break
        for turret in self.turrets: turret.update(self)
        return GameState.PLAYING
    def draw(self, surface):
        path_color = (139, 115, 85)
        for row_y in self.zombie_rows:
            path_rect = pygame.Rect(TRIPLE_MATCH_WIDTH, row_y - 40, ZOMBIE_AREA_WIDTH, 80)
            pygame.draw.rect(surface, path_color, path_rect)
            pygame.draw.rect(surface, DARK_GREEN, path_rect, 2)
        for z in self.zombies: z.draw(surface)
        for p in self.projectiles: p.draw(surface)
        for turret in self.turrets: turret.draw(surface)
    def shoot_projectile(self):
        if sounds['eliminate']: sounds['eliminate'].play()
        y_pos = random.choice(self.zombie_rows)
        self.projectiles.append(Projectile(TRIPLE_MATCH_WIDTH, y_pos))
    def shoot_custom_projectile(self, y_pos):
        if sounds['eliminate']: sounds['eliminate'].play()
        closest_row = min(self.zombie_rows, key=lambda row: abs(row - y_pos))
        self.projectiles.append(Projectile(TRIPLE_MATCH_WIDTH, closest_row))
    def is_level_complete(self, matches_made=0):
        level_type = self.level_data.get('type', 'score')
        if level_type == 'score': return self.score >= self.level_data['target']
        elif level_type == 'kill': return self.zombies_killed >= self.level_data['target']
        elif level_type == 'match': return matches_made >= self.level_data['target']
        return False

def game_loop(username, level_to_play):
    if level_to_play > len(LEVELS): all_levels_complete_screen(); return GameState.MAIN_MENU, level_to_play
    game_settings["bullet_storage"] = 0
    level_data = LEVELS[level_to_play - 1]
    triple_match = TripleMatchGame(mode='classic')
    zombie_game = ZombieGame(level_data)
    clock = pygame.time.Clock()
    is_match_level = level_data.get('type') == 'match'
    start_time = pygame.time.get_ticks(); matches_made = 0
    back_button = Button(SCREEN_WIDTH - 160, 10, 150, 40, "返回菜单", LIGHT_BLUE)
    buy_life_button = Button(20, 170, 200, 40, f"买命({game_settings['shop_costs']['life']})", BLUE)
    custom_bullet_button = Button(20, 220, 200, 40, f"自定义({game_settings['shop_costs']['custom_bullet']})", BLUE)
    buy_turret_button = Button(20, 270, 200, 40, f"炮台({game_settings['shop_costs']['turret']})", BLUE)
    shuffle_button = Button(20, 320, 200, 40, f"洗牌({game_settings['shop_costs']['shuffle']})", BLUE)
    selecting_custom_bullet_row = False; turret_purchased = False
    custom_bullet_cooldown = 0; lives_purchased = 0; life_purchase_cooldown = 0; shuffle_cooldown = 0
    while True:
        if custom_bullet_cooldown > 0: custom_bullet_cooldown -= 1
        if life_purchase_cooldown > 0: life_purchase_cooldown -= 1
        if shuffle_cooldown > 0: shuffle_cooldown -= 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return GameState.QUIT, level_to_play
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.is_clicked(event.pos): return GameState.MAIN_MENU, level_to_play
                if selecting_custom_bullet_row:
                    if event.pos[0] > TRIPLE_MATCH_WIDTH:
                        zombie_game.shoot_custom_projectile(event.pos[1])
                        game_settings["bullet_storage"] -= game_settings['shop_costs']['custom_bullet']
                        custom_bullet_cooldown = 45 * 60; selecting_custom_bullet_row = False
                    else: selecting_custom_bullet_row = False
                else:
                    if not is_match_level:
                        if buy_life_button.is_clicked(event.pos) and game_settings["bullet_storage"] >= game_settings['shop_costs']['life'] and lives_purchased < 3 and life_purchase_cooldown == 0:
                            game_settings["bullet_storage"] -= game_settings['shop_costs']['life']; zombie_game.lives += 1; lives_purchased += 1; life_purchase_cooldown = 60 * 60
                        elif buy_turret_button.is_clicked(event.pos) and not turret_purchased and game_settings["bullet_storage"] >= game_settings['shop_costs']['turret']:
                            game_settings["bullet_storage"] -= game_settings['shop_costs']['turret']; turret_purchased = True; zombie_game.turrets.append(AutoTurret(TRIPLE_MATCH_WIDTH + 50, SCREEN_HEIGHT // 2 - 25))
                    if custom_bullet_button.is_clicked(event.pos) and game_settings["bullet_storage"] >= game_settings['shop_costs']['custom_bullet'] and custom_bullet_cooldown == 0: selecting_custom_bullet_row = True
                    if shuffle_button.is_clicked(event.pos) and game_settings["bullet_storage"] >= game_settings['shop_costs']['shuffle'] and shuffle_cooldown == 0:
                        game_settings["bullet_storage"] -= game_settings['shop_costs']['shuffle']; shuffle_cooldown = 30 * 60; triple_match.initialize_grid()
                    result = triple_match.handle_click(event.pos)
                    if result:
                        matches_made += result.get('matches_made', 0)
                        game_settings["bullet_storage"] = min(game_settings["bullet_storage"] + result.get('ammo', 0), 50)
                        for _ in range(result.get('bullets', 0)): zombie_game.shoot_projectile()
        game_state = zombie_game.update()
        if game_state == GameState.GAME_OVER: return GameState.GAME_OVER, level_to_play
        if zombie_game.is_level_complete(matches_made):
            elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
            return GameState.LEVEL_COMPLETE, level_to_play, elapsed_time, zombie_game.zombies_killed, matches_made
        screen.fill(LIGHT_GREEN)
        triple_match.draw(screen)
        zombie_game.draw(screen)
        user_text = font_small.render(f"用户: {username}", True, BLACK); screen.blit(user_text, (20, 20))
        level_text = font_small.render(f"关卡: {level_to_play}", True, BLACK); screen.blit(level_text, (20, 50))
        lives_text = font_small.render(f"生命: {zombie_game.lives}", True, BLACK); screen.blit(lives_text, (20, 80))
        level_type = level_data.get('type', 'score')
        if level_type == 'score': objective_text = f"得分: {zombie_game.score}/{level_data['target']}"
        elif level_type == 'kill': objective_text = f"击杀: {zombie_game.zombies_killed}/{level_data['target']}"
        elif level_type == 'match': objective_text = f"三消: {matches_made}/{level_data['target']}"
        score_text = font_small.render(objective_text, True, BLACK); screen.blit(score_text, (20, 110))
        storage_text = font_small.render(f"备弹: {game_settings['bullet_storage']}", True, BLACK); screen.blit(storage_text, (20, 140))
        if not is_match_level:
            buy_life_button.draw(screen)
            if life_purchase_cooldown > 0:
                cooldown_text = font_small.render(f"冷却: {life_purchase_cooldown // 60}s", True, RED)
                screen.blit(cooldown_text, (buy_life_button.rect.right + 5, buy_life_button.rect.y + 10))
            if lives_purchased >= 3:
                limit_text = font_small.render("已达上限", True, RED)
                screen.blit(limit_text, (buy_life_button.rect.right + 5, buy_life_button.rect.y + 10))
            buy_turret_button.color = GRAY if turret_purchased else BLUE; buy_turret_button.draw(screen)
        shuffle_button.draw(screen)
        if shuffle_cooldown > 0:
            cooldown_text = font_small.render(f"冷却: {shuffle_cooldown // 60}s", True, RED)
            screen.blit(cooldown_text, (shuffle_button.rect.right + 5, shuffle_button.rect.y + 10))
        custom_bullet_button.draw(screen)
        if custom_bullet_cooldown > 0:
            cooldown_text = font_small.render(f"冷却: {custom_bullet_cooldown // 60}s", True, RED)
            screen.blit(cooldown_text, (custom_bullet_button.rect.right + 5, custom_bullet_button.rect.y + 10))
        back_button.draw(screen)
        if selecting_custom_bullet_row:
            select_text = font_medium.render("点击僵尸区域选择发射行", True, RED)
            screen.blit(select_text, (TRIPLE_MATCH_WIDTH + 50, 10))
        pygame.display.flip()
        clock.tick(60)

def battle_mode_game_loop(username, level_to_play, endless=False):
    level_data = BATTLE_LEVELS[level_to_play - 1] if not endless else {"type": "kill", "target": float('inf'), "zombies": float('inf'), "spawn_rate": 120}
    triple_match = TripleMatchGame(mode='battle')
    zombie_game = ZombieGame(level_data)
    zombie_game.lives = 15 # Battle mode has more lives
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks(); matches_made = 0
    shuffle_cooldown = 0
    game_settings["bullet_storage"] = 0 # Reset for battle mode
    
    back_button = Button(SCREEN_WIDTH - 160, 10, 150, 40, "返回菜单", LIGHT_BLUE)
    shuffle_button = Button(20, 170, 200, 40, f"洗牌(15)", BLUE)

    while True:
        if shuffle_cooldown > 0: shuffle_cooldown -= 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return GameState.QUIT, level_to_play
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.is_clicked(event.pos): return GameState.MAIN_MENU, level_to_play
                if shuffle_button.is_clicked(event.pos) and game_settings["bullet_storage"] >= 15 and shuffle_cooldown == 0:
                    game_settings["bullet_storage"] -= 15; shuffle_cooldown = 30 * 60; triple_match.initialize_grid()
                result = triple_match.handle_click(event.pos)
                if result and 'projectiles' in result:
                    matches_made += result.get('matches_made', 0)
                    game_settings["bullet_storage"] = min(game_settings["bullet_storage"] + result.get('ammo', 0), 50)
                    if sounds['eliminate']: sounds['eliminate'].play()
                    for p_info in result['projectiles']:
                        grid_r, grid_c = p_info['pos']
                        element_type = p_info['type']
                        start_x = grid_c * triple_match.cell_size + triple_match.cell_size / 2
                        start_y = (SCREEN_HEIGHT - TRIPLE_MATCH_HEIGHT) + grid_r * triple_match.cell_size + triple_match.cell_size / 2
                        # Find which zombie row this corresponds to
                        target_y = min(zombie_game.zombie_rows, key=lambda r: abs(r - start_y))
                        # Create projectile starting from the right edge of the match grid, aligned with the row
                        proj = Projectile(TRIPLE_MATCH_WIDTH, target_y, image=elements[element_type])
                        zombie_game.projectiles.append(proj)
        game_state = zombie_game.update()
        if game_state == GameState.GAME_OVER: return GameState.GAME_OVER, level_to_play
        if not endless and zombie_game.is_level_complete():
            elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
            return GameState.LEVEL_COMPLETE, level_to_play, elapsed_time, zombie_game.zombies_killed, matches_made
        screen.fill(LIGHT_GREEN)
        triple_match.draw(screen)
        zombie_game.draw(screen)
        user_text = font_small.render(f"用户: {username}", True, BLACK); screen.blit(user_text, (20, 20))
        mode_text = font_small.render("模式: 战斗", True, BLACK); screen.blit(mode_text, (20, 50))
        lives_text = font_small.render(f"生命: {zombie_game.lives}", True, BLACK); screen.blit(lives_text, (20, 80))
        if endless: objective_text = f"击杀: {zombie_game.zombies_killed}"
        else: objective_text = f"击杀: {zombie_game.zombies_killed}/{level_data['target']}"
        score_text = font_small.render(objective_text, True, BLACK); screen.blit(score_text, (20, 110))
        # No bullet storage in this mode, but we need it for shuffle
        storage_text = font_small.render(f"备弹: {game_settings['bullet_storage']}", True, BLACK); screen.blit(storage_text, (20, 140))
        shuffle_button.draw(screen)
        if shuffle_cooldown > 0:
            cooldown_text = font_small.render(f"冷却: {shuffle_cooldown // 60}s", True, RED)
            screen.blit(cooldown_text, (shuffle_button.rect.right + 5, shuffle_button.rect.y + 10))
        back_button.draw(screen)
        pygame.display.flip()
        clock.tick(60)

def all_levels_complete_screen():
    back_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 200, 200, 50, "返回菜单", GREEN)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.is_clicked(event.pos): return
        screen.fill(WHITE)
        title_text = font_large.render("恭喜！你已通关所有冒险关卡！", True, GREEN)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 200))
        back_button.draw(screen)
        pygame.display.flip()

def endless_game_loop(username, initial_lives=15, initial_score=0):
    game_settings["bullet_storage"] = 0
    triple_match = TripleMatchGame()
    endless_level_data = {"zombies": float('inf'), "spawn_rate": 180}
    zombie_game = ZombieGame(endless_level_data)
    zombie_game.lives = initial_lives; zombie_game.score = initial_score
    clock = pygame.time.Clock()
    back_button = Button(SCREEN_WIDTH - 160, 10, 150, 40, "返回菜单", LIGHT_BLUE)
    buy_life_button = Button(20, 170, 200, 40, f"买命({game_settings['shop_costs']['life']})", BLUE)
    custom_bullet_button = Button(20, 220, 200, 40, f"自定义({game_settings['shop_costs']['custom_bullet']})", BLUE)
    buy_turret_button = Button(20, 270, 200, 40, f"炮台({game_settings['shop_costs']['turret']})", BLUE)
    shuffle_button = Button(20, 320, 200, 40, f"洗牌({game_settings['shop_costs']['shuffle']})", BLUE)
    selecting_custom_bullet_row = False; turret_purchased = False; spawn_rate_timer = 0
    custom_bullet_cooldown = 0; lives_purchased = 0; life_purchase_cooldown = 0; shuffle_cooldown = 0
    while True:
        if custom_bullet_cooldown > 0: custom_bullet_cooldown -= 1
        if life_purchase_cooldown > 0: life_purchase_cooldown -= 1
        if shuffle_cooldown > 0: shuffle_cooldown -= 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return GameState.QUIT, zombie_game.score
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.is_clicked(event.pos): return GameState.MAIN_MENU, zombie_game.score
                if selecting_custom_bullet_row:
                    if event.pos[0] > TRIPLE_MATCH_WIDTH:
                        zombie_game.shoot_custom_projectile(event.pos[1]); game_settings["bullet_storage"] -= game_settings['shop_costs']['custom_bullet']; custom_bullet_cooldown = 45 * 60; selecting_custom_bullet_row = False
                    else: selecting_custom_bullet_row = False
                else:
                    if buy_life_button.is_clicked(event.pos) and game_settings["bullet_storage"] >= game_settings['shop_costs']['life'] and lives_purchased < 3 and life_purchase_cooldown == 0:
                        game_settings["bullet_storage"] -= game_settings['shop_costs']['life']; zombie_game.lives += 1; lives_purchased += 1; life_purchase_cooldown = 60 * 60
                    elif custom_bullet_button.is_clicked(event.pos) and game_settings["bullet_storage"] >= game_settings['shop_costs']['custom_bullet'] and custom_bullet_cooldown == 0: selecting_custom_bullet_row = True
                    elif buy_turret_button.is_clicked(event.pos) and not turret_purchased and game_settings["bullet_storage"] >= game_settings['shop_costs']['turret']:
                        game_settings["bullet_storage"] -= game_settings['shop_costs']['turret']; turret_purchased = True; zombie_game.turrets.append(AutoTurret(TRIPLE_MATCH_WIDTH + 50, SCREEN_HEIGHT // 2 - 25))
                    elif shuffle_button.is_clicked(event.pos) and game_settings["bullet_storage"] >= game_settings['shop_costs']['shuffle'] and shuffle_cooldown == 0:
                        game_settings["bullet_storage"] -= game_settings['shop_costs']['shuffle']; shuffle_cooldown = 30 * 60; triple_match.initialize_grid()
                    else:
                        result = triple_match.handle_click(event.pos)
                        if result:
                            game_settings["bullet_storage"] = min(game_settings["bullet_storage"] + result.get('ammo', 0), 50)
                            for _ in range(result.get('bullets', 0)): zombie_game.shoot_projectile()
        spawn_rate_timer += 1
        if spawn_rate_timer > 600 and zombie_game.level_data["spawn_rate"] > 45:
            zombie_game.level_data["spawn_rate"] = max(45, zombie_game.level_data["spawn_rate"] - 5); spawn_rate_timer = 0
        game_status = zombie_game.update()
        if game_status == GameState.GAME_OVER: return GameState.ENDLESS_GAMEOVER, zombie_game.score
        screen.fill(LIGHT_GREEN)
        triple_match.draw(screen)
        zombie_game.draw(screen)
        user_text = font_small.render(f"用户: {username}", True, BLACK); screen.blit(user_text, (20, 20))
        mode_text = font_small.render("模式: 无尽", True, BLACK); screen.blit(mode_text, (20, 50))
        lives_text = font_small.render(f"生命: {zombie_game.lives}", True, BLACK); screen.blit(lives_text, (20, 80))
        score_text = font_small.render(f"得分: {zombie_game.score}", True, BLACK); screen.blit(score_text, (20, 110))
        storage_text = font_small.render(f"备弹: {game_settings['bullet_storage']}", True, BLACK); screen.blit(storage_text, (20, 140))
        buy_life_button.draw(screen)
        if life_purchase_cooldown > 0:
            cooldown_text = font_small.render(f"冷却: {life_purchase_cooldown // 60}s", True, RED)
            screen.blit(cooldown_text, (buy_life_button.rect.right + 5, buy_life_button.rect.y + 10))
        if lives_purchased >= 3:
            limit_text = font_small.render("已达上限", True, RED)
            screen.blit(limit_text, (buy_life_button.rect.right + 5, buy_life_button.rect.y + 10))
        custom_bullet_button.draw(screen)
        if custom_bullet_cooldown > 0:
            cooldown_text = font_small.render(f"冷却: {custom_bullet_cooldown // 60}s", True, RED)
            screen.blit(cooldown_text, (custom_bullet_button.rect.right + 5, custom_bullet_button.rect.y + 10))
        buy_turret_button.color = GRAY if turret_purchased else BLUE; buy_turret_button.draw(screen)
        shuffle_button.draw(screen)
        if shuffle_cooldown > 0:
            cooldown_text = font_small.render(f"冷却: {shuffle_cooldown // 60}s", True, RED)
            screen.blit(cooldown_text, (shuffle_button.rect.right + 5, shuffle_button.rect.y + 10))
        back_button.draw(screen)
        if selecting_custom_bullet_row:
            select_text = font_medium.render("点击僵尸区域选择发射行", True, RED)
            screen.blit(select_text, (TRIPLE_MATCH_WIDTH + 50, 10))
        pygame.display.flip()
        clock.tick(60)

def play_video_screen(video_path, audio_path):
    # 优先使用OpenCV播放视频
    if OPENCV_AVAILABLE:
        return play_video_with_opencv(video_path, audio_path)
    elif MOVIEPY_AVAILABLE:
        return play_video_with_moviepy(video_path)
    else:
        print("未安装视频播放库。请运行 'pip install opencv-python' 或 'pip install moviepy' 进行安装。")
        return True

def play_video_with_opencv(video_path, audio_path):
    """使用OpenCV播放视频并播放对应的音频"""
    revived = False
    skip_input = ""
    
    try:
        # 停止背景音乐
        pygame.mixer.music.stop()
        
        # 开始播放指定的音频文件
        if os.path.exists(audio_path):
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.set_volume(game_settings["music_volume"])
            pygame.mixer.music.play()
        
        # 打开视频文件
        cap = cv2.VideoCapture(video_path)
        
        # 获取视频的帧率
        fps = cap.get(cv2.CAP_PROP_FPS)
        delay = int(1000 / fps) if fps > 0 else 33  # 默认约30fps
        
        # 获取视频的总帧数
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # 调整帧大小以适应屏幕
            frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            # 将BGR格式转换为RGB格式
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 转换为Pygame Surface
            frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
            
            # 在屏幕上绘制帧
            screen.blit(frame_surface, (0, 0))
            pygame.display.flip()
            
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    revived = False
                    break
                if event.type == pygame.KEYDOWN:
                    char = pygame.key.name(event.key).lower()
                    if len(char) == 1:
                        skip_input += char
                        if skip_input.endswith("iamsb"):
                            revived = True
                        if len(skip_input) > 10:
                            skip_input = skip_input[-10:]
            
            if not revived:
                # 控制播放速度
                pygame.time.delay(delay)
            else:
                break
        
        # 释放视频捕获对象
        cap.release()
        
        # 如果不是用户主动关闭，则视为复活
        if not revived:
            revived = True
            
    except Exception as e:
        print(f"使用 OpenCV 播放视频失败: {e}")
        revived = True  # 如果播放失败，也算作复活，避免卡住玩家
    finally:
        # 停止当前音频
        pygame.mixer.music.stop()
        
        # 恢复背景音乐
        try:
            pygame.mixer.music.load(resource_path('ogg/bjyy.mp3'))
            pygame.mixer.music.set_volume(game_settings["music_volume"])
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"无法重新加载背景音乐: {e}")
    
    return revived

# 保留原有的实现作为备选方案
def play_video_with_moviepy(video_path):
    """使用moviepy播放视频（原有实现）"""
    if not MOVIEPY_AVAILABLE:
        print("MoviePy 未安装，跳过视频播放。请运行 'pip install moviepy' 进行安装。")
        return True

    revived = False
    skip_input = ""
    clip = None
    
    try:
        # 停止背景音乐
        pygame.mixer.music.stop()

        clip = VideoFileClip(video_path)
        
        # 播放视频音频
        if clip.audio:
            clip.audio.preview(fps=22050)

        start_time = pygame.time.get_ticks()
        duration_ms = clip.duration * 1000
        
        # 视频播放循环
        while (pygame.time.get_ticks() - start_time) < duration_ms:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if clip: clip.close()
                    return False # 用户关闭窗口，未复活
                if event.type == pygame.KEYDOWN:
                    char = pygame.key.name(event.key).lower()
                    if len(char) == 1:
                        skip_input += char
                        if skip_input.endswith("iamsb"):
                            revived = True
                        if len(skip_input) > 10:
                            skip_input = skip_input[-10:]
            
            if revived:
                break

            # 获取当前时间的视频帧
            current_time_sec = (pygame.time.get_ticks() - start_time) / 1000.0
            if current_time_sec > clip.duration:
                break
                
            frame = clip.get_frame(current_time_sec)
            
            # 转换帧为Pygame Surface并显示
            frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            scaled_surface = pygame.transform.scale(frame_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled_surface, (0, 0))
            pygame.display.flip()

        # 视频正常播放结束或被跳过，都视为复活
        if not revived:
            revived = True

    except Exception as e:
        print(f"使用 moviepy 播放视频失败: {e}")
        revived = True # 如果播放失败，也算作复活，避免卡住玩家
    finally:
        if clip:
            # 停止视频音频
            if clip.audio:
                clip.audio.close()
            clip.close()
        
        # 恢复背景音乐
        try:
            pygame.mixer.music.load(resource_path('ogg/bjyy.mp3'))
            pygame.mixer.music.set_volume(game_settings["music_volume"])
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"无法重新加载背景音乐: {e}")
    
    return revived


def level_complete_screen(level, elapsed_time=0, zombies_killed=0, matches_made=0):
    continue_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 200, 200, 50, "继续", GREEN)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return GameState.QUIT
            if event.type == pygame.MOUSEBUTTONDOWN:
                if continue_button.is_clicked(event.pos): return GameState.PLAYING
        screen.fill(WHITE)
        title_text = font_large.render(f"关卡 {level} 完成!", True, GREEN)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
        time_text = font_medium.render(f"用时: {elapsed_time} 秒", True, BLACK)
        screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, 200))
        zombies_text = font_medium.render(f"击败僵尸: {zombies_killed} 个", True, BLACK)
        screen.blit(zombies_text, (SCREEN_WIDTH // 2 - zombies_text.get_width() // 2, 250))
        matches_text = font_medium.render(f"完成三消: {matches_made} 次", True, BLACK)
        screen.blit(matches_text, (SCREEN_WIDTH // 2 - matches_text.get_width() // 2, 300))
        continue_button.draw(screen)
        pygame.display.flip()

def main():
    pygame.mixer.init()
    try:
        pygame.mixer.music.load(resource_path('ogg/bjyy.mp3'))
        pygame.mixer.music.set_volume(game_settings["music_volume"])
        pygame.mixer.music.play(-1)
    except pygame.error as e: print(f"加载背景音乐失败: {e}")
    game_state = GameState.SPLASH_SCREEN
    username = None; max_unlocked_level = 1; selected_level = 1
    endless_lives = 15; endless_score = 0; level_stats = {}
    while game_state != GameState.QUIT:
        if game_state == GameState.SPLASH_SCREEN:
            game_state = splash_screen()
        elif game_state == GameState.VERSION_INFO:
            game_state = version_info_screen()
        elif game_state == GameState.ACCOUNT_SELECTION:
            username, game_state = account_selection_screen()
            if username:
                user_data = load_user_data()
                max_unlocked_level = user_data.get(username, {}).get("level", 1)
        elif game_state == GameState.MAIN_MENU:
            menu_result = main_menu_screen(username, max_unlocked_level)
            if isinstance(menu_result, tuple):
                game_state, max_unlocked_level, _ = menu_result
            else:
                game_state = menu_result
            if game_state == GameState.ENDLESS_PLAYING:
                endless_lives = 15
        elif game_state == GameState.CLASSIC_MODE_SELECTION:
            game_state, _ = classic_mode_selection_screen(max_unlocked_level)
        elif game_state == GameState.BATTLE_MODE_SELECTION:
            game_state, _ = battle_mode_selection_screen(max_unlocked_level)
        elif game_state == GameState.LEVEL_SELECTION:
            game_state, selected_level = level_selection_screen(max_unlocked_level, levels_data=LEVELS, mode_title="选择关卡", back_state=GameState.CLASSIC_MODE_SELECTION)
        elif game_state == GameState.BATTLE_LEVEL_SELECTION:
            # Battle mode has progressive level unlocking
            game_state, selected_level = level_selection_screen(max_unlocked_level, levels_data=BATTLE_LEVELS, mode_title="选择战斗关卡", back_state=GameState.BATTLE_MODE_SELECTION)
        elif game_state == GameState.PLAYING:
            result = game_loop(username, selected_level)
            if len(result) > 2:
                game_state, selected_level, elapsed_time, zombies_killed, matches_made = result
                level_stats = {'elapsed_time': elapsed_time, 'zombies_killed': zombies_killed, 'matches_made': matches_made}
            else: game_state, selected_level = result
        elif game_state == GameState.BATTLE_MODE_PLAYING:
            result = battle_mode_game_loop(username, selected_level)
            if len(result) > 2:
                game_state, selected_level, elapsed_time, zombies_killed, matches_made = result
                level_stats = {'elapsed_time': elapsed_time, 'zombies_killed': zombies_killed, 'matches_made': matches_made}
            else: game_state, selected_level = result
        elif game_state == GameState.BATTLE_MODE_ENDLESS_PLAYING:
            game_state, _ = battle_mode_game_loop(username, 1, endless=True)
        elif game_state == GameState.ENDLESS_PLAYING:
            game_state, endless_score = endless_game_loop(username, endless_lives, endless_score)
        elif game_state == GameState.ENDLESS_GAMEOVER:
            video_p = resource_path('ogg/deee.mp4'); audio_p = resource_path('ogg/deee.mp3')
            revived = play_video_screen(video_p, audio_p)
            if revived: endless_lives = 6; game_state = GameState.ENDLESS_PLAYING
            else: game_state = GameState.GAME_OVER
        elif game_state == GameState.LEVEL_COMPLETE:
            if selected_level == max_unlocked_level and max_unlocked_level < len(LEVELS):
                max_unlocked_level += 1
                user_data = load_user_data()
                user_data[username]["level"] = max_unlocked_level
                save_user_data(user_data)
            if selected_level >= len(LEVELS):
                all_levels_complete_screen(); game_state = GameState.MAIN_MENU
            else:
                game_state = level_complete_screen(selected_level, level_stats.get('elapsed_time', 0), level_stats.get('zombies_killed', 0), level_stats.get('matches_made', 0))
                if game_state == GameState.PLAYING: selected_level += 1
                else: game_state = GameState.MAIN_MENU
        elif game_state == GameState.GAME_OVER:
            user_data = load_user_data()
            if username in user_data:
                best_score = user_data[username].get("best_score", 0)
                if endless_score > best_score: user_data[username]["best_score"] = endless_score; save_user_data(user_data)
            endless_score = 0
            screen.fill(BLACK)
            lose_text = font_large.render("游戏结束", True, RED)
            screen.blit(lose_text, (SCREEN_WIDTH//2 - lose_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            pygame.display.flip()
            pygame.time.wait(2000)
            game_state = GameState.MAIN_MENU
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
