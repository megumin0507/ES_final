import pygame
import random
from src.note import Note

sprites_dir = ".\\sprites\\"

class Scene:
    def __init__(self, screen: pygame.Surface):
        self._load_sprites()
        self.screen = screen
        self.TARGET_X = 200
        self.NOTE_SPEED = 500  
        self.HIT_THRESHOLD = 80
        
        self.Q_ypos = 100
        self.Q_notes: list[Note] = []

        self.ans_class = []
        self.set_random_sequence()

    def load_game_scene(self, dt):
        self.screen.blit(self.background_img, (0, 0))
        self.screen.blit(self.textboxes_img, (0, 0))
        pygame.draw.line(self.screen, (255, 255, 255), (self.TARGET_X, 0), (self.TARGET_X, 720), 2)
        pygame.draw.circle(self.screen, (200, 200, 200), (self.TARGET_X, self.Q_ypos+60), 70, 2)
        for note in self.Q_notes:
            note.get_pos(dt) 
            self.screen.blit(note.get_img(), note.pos)

    def set_random_sequence(self):
        beat_unit = 500 
        self.notes = []
        
        options = [-1, 0, 1, 2, 3]
        w = [10, 10, 10, 10, 10]
        sequence = random.choices(options, weights=w, k=8)
        if sequence[0] == -1: sequence[0] = 0

        self.ans_class = []
        
        current_time_ms = 0
        
        start_delay_ms = 1500 

        print(f"New Sequence: {sequence}")

        for i, note_id in enumerate(sequence):
            current_time_ms += beat_unit
            if note_id == -1:
                continue
            self.ans_class.append(note_id)

            time_to_hit_sec = (start_delay_ms + current_time_ms) / 1000.0
            spawn_x = self.TARGET_X + (self.NOTE_SPEED * time_to_hit_sec)
            
            new_note = Note(
                pos=pygame.Vector2(spawn_x, self.Q_ypos), 
                target_x=self.TARGET_X, 
                id=note_id, 
                speed=self.NOTE_SPEED
            )
            self.Q_notes.append(new_note)

        last_note_x = self.Q_notes[-1].pos.x if self.Q_notes else 0
        distance_to_finish = last_note_x + 200
        total_time_sec = distance_to_finish / self.NOTE_SPEED
        self.switch_interval = total_time_sec * 1000

    def check_input_hit(self, user_input_id):
        target_note = None
        min_dist = 99999

        for note in self.Q_notes:
            if not note.is_hit:
                dist = abs(note.pos.x + 32 - self.TARGET_X)
                if dist < min_dist:
                    min_dist = dist
                    target_note = note
        
        if target_note and min_dist <= self.HIT_THRESHOLD:
            # if user_input_id == target_note.id:
            if user_input_id % 2 == target_note.id % 2:
                target_note.jump()
                print(f"Hit! Dist: {min_dist:.2f}")
                return "PERFECT"
            else:
                return "FAIL"
        else:
            return None 

    def _load_sprites(self):        
        self.background_img = pygame.image.load(f"{sprites_dir}background.png").convert_alpha()
        self.textboxes_img = pygame.image.load(f"{sprites_dir}textbox.png").convert_alpha()

    def draw_result_text(self, text):
        font = pygame.font.SysFont("Arial", 120, bold=True)
        if "FAIL" in text:
            color = (255, 50, 50)   # Red
        else:
            color = (50, 255, 50)   # Green
        text_surface = font.render(text, True, color)
        
        screen = pygame.display.get_surface() 
        screen_rect = screen.get_rect()
        
        text_rect = text_surface.get_rect(center=screen_rect.center)
        
        screen.blit(text_surface, text_rect)

    def draw_combo(self, combo_count):
        """
        顯示 Combo 數值
        位置：螢幕水平置中，偏下方
        """
        if combo_count <= 0:
            return
        if not hasattr(self, 'combo_font'):
            self.combo_font = pygame.font.SysFont("Arial", 60, bold=True)

        text_str = f"COMBO {combo_count}"
        
        color = (0, 255, 255) 
        
        text_surface = self.combo_font.render(text_str, True, color)
        
        screen_rect = self.screen.get_rect()
        text_rect = text_surface.get_rect(center=(screen_rect.centerx, screen_rect.height * 0.75))
        
        self.screen.blit(text_surface, text_rect)
        
    def draw_waiting_text(self, text):
        self.screen.fill((0, 0, 0)) 
        font = pygame.font.Font(None, 72)
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, 
                                                self.screen.get_height() // 2))
        self.screen.blit(text_surface, text_rect)