import pygame
import random
from src.note import Note

sprites_dir = ".\\sprites\\"

class Scene:
    def __init__(self, screen: pygame.Surface):
        self._load_sprites()
        self.screen = screen
        
        y_pos = 100
        self.slot_positions = [
            pygame.Vector2(91, y_pos),   # Slot 1
            pygame.Vector2(227, y_pos),  # Slot 2
            pygame.Vector2(363, y_pos),  # Slot 3
            pygame.Vector2(499, y_pos),  # Slot 4
            pygame.Vector2(635, y_pos),  # Slot 5
            pygame.Vector2(771, y_pos),  # Slot 6
            pygame.Vector2(907, y_pos),  # Slot 7
            pygame.Vector2(1043, y_pos)  # Slot 8
        ]
        
        A_ypos = 700
        self.A_slot_positions = [
            pygame.Vector2(91, A_ypos),   # Slot 1
            pygame.Vector2(227, A_ypos),  # Slot 2
            pygame.Vector2(363, A_ypos),  # Slot 3
            pygame.Vector2(499, A_ypos),  # Slot 4
            pygame.Vector2(635, A_ypos),  # Slot 5
            pygame.Vector2(771, A_ypos),  # Slot 6
            pygame.Vector2(907, A_ypos),  # Slot 7
            pygame.Vector2(1043, A_ypos)  # Slot 8
        ]
        self.notes: list[Note] = []
        self.k = 0
        self.set_random_sequence()

    def run(self, dt):
        self.load_game_scene(dt)

    def load_game_scene(self, dt):
        self.screen.blit(self.background_img, (0, 0))
        self.screen.blit(self.textboxes_img, (0, 0))
        for i in range(self.k):
            note = self.notes[i]
            pre_note = self.notes[i-1] if i != 0 else None
            img = note.get_img()
            pos = note.get_pos(dt)
            if pre_note is not None: # not first note
                if note.should_jump() and pre_note.has_jumped():
                    note.jump()
            else: # first note
                if note.should_jump():
                    note.jump()
            self.screen.blit(img, pos)

    def set_random_sequence(self):
        self.notes = []
        
        options = [0, 1, 2, 3]
        w = [10, 10, 10, 10]
        self.k = random.randint(4, 8)
        self.answer = random.choices(options, weights=w, k=self.k)
        print(self.answer)
        
        for i in range(self.k):
            id = self.answer[i]
            self.notes.append(Note(self.slot_positions[i], id))


    def _load_sprites(self):        
        self.background_img = pygame.image.load(f"{sprites_dir}background.png").convert_alpha()
        self.textboxes_img = pygame.image.load(f"{sprites_dir}textbox.png").convert_alpha()

    def show_user_motion(self, motion_id, pos):
        """
        當接收到訊號時，顯示出來
        """
        note_shown = Note(self.A_slot_positions[pos], motion_id)
        self.screen.blit(note_shown.get_img() , note_shown.pos)
        print(f"Visual: Drum {motion_id} hit!")

    def draw_result_text(self, text):
        """
        在螢幕中央畫出 PERFECT 或 FAIL
        """
        # 1. 建立字型 (如果這行覺得卡頓，建議把 font 宣告移到 _init_ 裡)
        # 參數: 字體名稱, 大小, 粗體
        font = pygame.font.SysFont("Arial", 80, bold=True)
        
        # 2. 決定顏色 (包含 "FAIL" 字樣就紅色，不然就綠色)
        if "FAIL" in text:
            color = (255, 50, 50)   # 紅色
        else:
            color = (50, 255, 50)   # 綠色

        # 3. 渲染文字圖片 (文字, 反鋸齒, 顏色)
        text_surface = font.render(text, True, color)
        
        # 4. 取得螢幕的中心點並計算文字位置
        # 這裡假設你的 Scene 裡有 self.screen，如果沒有，請改用 pygame.display.get_surface()
        screen = pygame.display.get_surface() 
        screen_rect = screen.get_rect()
        
        # 讓文字的中心點 = 螢幕的中心點
        text_rect = text_surface.get_rect(center=screen_rect.center)
        
        # 5. 畫上去
        screen.blit(text_surface, text_rect)