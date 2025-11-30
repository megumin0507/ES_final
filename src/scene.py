import pygame
import random

sprites_dir = ".\\sprites\\"

class Scene:
    def __init__(self, screen: pygame.Surface):
        self._load_sprites()
        self.screen = screen
        
        y_pos = 100
        self.slot_positions = [
            (91, y_pos),   # Slot 1
            (227, y_pos),  # Slot 2
            (363, y_pos),  # Slot 3
            (499, y_pos),  # Slot 4
            (635, y_pos),  # Slot 5
            (771, y_pos),  # Slot 6
            (907, y_pos),  # Slot 7
            (1043, y_pos)  # Slot 8
        ]
        self.current_slots = []
        self.set_random_sequence()

    def run(self):
        self.load_game_scene()

    def load_game_scene(self):
        self.screen.blit(self.background_img, (0, 0))
        self.screen.blit(self.textboxes_img, (0, 0))
        for i in range(8):
            img = self.current_slots[i]
            pos = self.slot_positions[i]
            if img is not None:
                self.screen.blit(img, pos)

    def set_random_sequence(self):
        options = [
            None,
            self.L_blue_img,
            self.L_red_img,
            self.R_blue_img,
            self.R_red_img
        ]
        w = [20, 10, 10, 10, 10]
        self.current_slots = random.choices(options, weights=w, k=8)

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
