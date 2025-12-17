import pygame
import random
from src2.note import Note
from src2.player import Player

sprites_dir = ".\\sprites\\"

class Scene:
    def __init__(self, screen: pygame.Surface):
        self._load_sprites()
        self.screen = screen

        # -----parameters-----
        self.beat_unit = 200
        
        Q_ypos = 60
        self.Q_slot_positions = [
            pygame.Vector2(91, Q_ypos),   # Slot 1
            pygame.Vector2(227, Q_ypos),  # Slot 2
            pygame.Vector2(363, Q_ypos),  # Slot 3
            pygame.Vector2(499, Q_ypos),  # Slot 4
            pygame.Vector2(635, Q_ypos),  # Slot 5
            pygame.Vector2(771, Q_ypos),  # Slot 6
            pygame.Vector2(907, Q_ypos),  # Slot 7
            pygame.Vector2(1043, Q_ypos)  # Slot 8
        ]
        self.Q_notes: list[Note] = []
        
        self.player_notes: list[Note] = []  # 保存玩家輸入的 notes，不分player
        self.ans_length = 0
        self.set_random_sequence()

    def load_game_scene(self, dt):
        self.screen.blit(self.background_img, (0, 0))
        for i in range(self.ans_length):
            note = self.Q_notes[i]
            pre_note = self.Q_notes[i-1] if i != 0 else None
            img = note.get_img()
            pos = note.get_pos(dt)
            if pre_note is not None: # not first note
                if note.should_jump() and note.jumped_delay_timer <= 0:
                    note.jump()
            else: # first note
                if note.should_jump():
                    note.jump()
            self.screen.blit(img, pos)
        for player_note in self.player_notes:
            self.screen.blit(player_note.get_img(), player_note.pos)

    def set_random_sequence(self):
        beat_unit = self.beat_unit # const ms
        self.player_notes = [] # 只是清空
        
        options = [-1, 0, 1]
        w = [15, 10, 10]
        first = random.choices(options[1:], weights=w[1:], k=1)
        rest = random.choices(options, weights=w, k=7)
        self.Q = first+rest
        # base on slot ans generate answer
        self.ans_class = first
        self.ans_time = [0] #第一個一定是0
        self.ans_length = 1
        t_interval = beat_unit
        for slot in rest:
            if slot==-1:
                t_interval += beat_unit
            else:
                self.ans_class.append(slot)
                self.ans_time.append(t_interval)
                self.ans_length += 1
                t_interval = beat_unit
        
        print(self.Q)
        print(self.ans_class)
        print(self.ans_time)
        print(self.ans_length)
        
        self.Q_notes = []
        for i in range(8): # generate note object
            if self.Q[i] == -1:
                continue
            else:
                self.Q_notes.append(Note(self.Q_slot_positions[i], self.Q[i], delay = i*beat_unit/1000))
            
        self.switch_interval = 18*beat_unit


    def _load_sprites(self):        
        self.background_img = pygame.image.load(f"{sprites_dir}background2.png").convert_alpha()

    def show_user_motion(self, motion_id, time, player: Player):
        """
        當接收到訊號時，顯示出來
        """
        if player.device_idx==0:
            note_shown = Note(pygame.Vector2(91 + time/400*136, 360), motion_id)
            self.player_notes.append(note_shown) #不分player
            print(f"Visual:p1 Drum {motion_id} hit!")
        else:
            note_shown = Note(pygame.Vector2(91 + time/400*136, 550), motion_id)
            self.player_notes.append(note_shown) #不分player
            print(f"Visual:p2 Drum {motion_id} hit!")

    def draw_result_text(self, player: Player):
        """
        在螢幕中央畫出 PERFECT 或 FAIL
        """
        text = player.score_result
        id = player.device_idx
        # 1. 建立字型 (如果這行覺得卡頓，建議把 font 宣告移到 _init_ 裡)
        # 參數: 字體名稱, 大小, 粗體
        font = pygame.font.SysFont("Arial", 120, bold=True)
        
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
        
        # 5. 畫上去
        screen.blit(text_surface, pygame.Vector2(600, 360 if id ==0 else 550))

    def draw_waiting_text(self, text):
        """顯示等待 BLE 連接的文字"""
        self.screen.fill((0, 0, 0))  # 清空畫面
        font = pygame.font.Font(None, 72)
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, 
                                                self.screen.get_height() // 2))
        self.screen.blit(text_surface, text_rect)