import pygame
import math

sprites_dir = ".\\sprites\\"

class Note:
    def __init__(self, pos: pygame.Vector2, id, delay: float = 1.0):
        self.original_pos = pos.copy()
        self.pos = pos.copy()
        self.id = id
        self.delay_duration = delay
        self.jumped_delay_timer = self.delay_duration
        self.jumping = False
        self.jumped = False
        self.v = pygame.Vector2(0, 0)
        self.a = pygame.Vector2(0, 5000)
        self._load_sprites()
        options = [
            self.R_blue_img,
            self.R_red_img,
            # self.L_blue_img,
            # self.L_red_img
        ]
        self.img = options[id]

    def _load_sprites(self):
        def scale(img, scale_factor=0.5):
            new_width = int(img.get_width() * scale_factor)
            new_height = int(img.get_height() * scale_factor)
            return pygame.transform.smoothscale(img, (new_width, new_height))
        
        # self.L_blue_img = scale(pygame.image.load(f"{sprites_dir}L_Blue.png").convert_alpha())
        # self.L_red_img = scale(pygame.image.load(f"{sprites_dir}L_Red.png").convert_alpha())
        self.R_blue_img = scale(pygame.image.load(f"{sprites_dir}R_Blue.png").convert_alpha())
        self.R_red_img = scale(pygame.image.load(f"{sprites_dir}R_Red.png").convert_alpha())

    def get_img(self):
        return self.img

    def get_pos(self, dt: float):
        if self.jumping:
            self.v += self.a * dt
            self.pos += self.v * dt
            if math.isclose(self.v.y, 1000, rel_tol=6e-2):
                self.pos = self.original_pos
                self.jumping = False
                self.jumped = True
        if self.jumped_delay_timer > 0:
            self.jumped_delay_timer -= dt
            if self.jumped_delay_timer <= 0:
                self.jumped_delay_timer = 0
        return self.pos
    
    def should_jump(self):
        return not self.jumping and not self.jumped
    
    def jump(self):
        self.jumping = True
        self.v.y = -1000