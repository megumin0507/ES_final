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
        options = [
            self.L_blue_img,
            self.L_red_img,
            self.R_blue_img,
            self.R_red_img
        ]
        w = [10, 10, 10, 10]
        self.k = random.randint(4, 8)
        imgs = random.choices(options, weights=w, k=self.k)
        for i in range(self.k):
            self.notes.append(Note(self.slot_positions[i], imgs[i]))


    def _load_sprites(self):
        def scale(img, scale_factor=0.5):
            new_width = int(img.get_width() * scale_factor)
            new_height = int(img.get_height() * scale_factor)
            return pygame.transform.smoothscale(img, (new_width, new_height))
        
        self.background_img = pygame.image.load(f"{sprites_dir}background.png").convert_alpha()
        self.textboxes_img = pygame.image.load(f"{sprites_dir}textbox.png").convert_alpha()
        self.L_blue_img = scale(pygame.image.load(f"{sprites_dir}L_Blue.png").convert_alpha())
        self.L_red_img = scale(pygame.image.load(f"{sprites_dir}L_Red.png").convert_alpha())
        self.R_blue_img = scale(pygame.image.load(f"{sprites_dir}R_Blue.png").convert_alpha())
        self.R_red_img = scale(pygame.image.load(f"{sprites_dir}R_Red.png").convert_alpha())
