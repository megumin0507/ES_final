import pygame
import math

sprites_dir = ".\\sprites\\"

class Note:
    def __init__(self, pos: pygame.Vector2, target_x: float, id, speed: float):
        self.original_pos = pos.copy()
        self.pos = pos.copy()
        self.target_x = target_x
        self.speed = speed
        self.id = id
        self.jumping = False
        self.is_hit = False
        self.v = pygame.Vector2(-self.speed, 0)
        self.a = pygame.Vector2(0, 0)
        self._load_sprites()
        options = [
            self.Blue_img,
            self.Red_img,
        ]
        self.img = options[id]

    def _load_sprites(self):
        def scale(img, scale_factor=0.5):
            new_width = int(img.get_width() * scale_factor)
            new_height = int(img.get_height() * scale_factor)
            return pygame.transform.smoothscale(img, (new_width, new_height))
        
        self.Blue_img = scale(pygame.image.load(f"{sprites_dir}Blue.png").convert_alpha())
        self.Red_img = scale(pygame.image.load(f"{sprites_dir}Red.png").convert_alpha())

    def get_img(self):
        return self.img

    def get_pos(self, dt: float):
        self.v += self.a * dt
        self.pos += self.v * dt
        return self.pos
    
    def jump(self):
        self.jumping = True
        self.is_hit = True
        self.v.x = self.speed/2
        self.v.y = -1000
        self.a.y = 5000

    def is_out_of_screen(self):
        return self.pos.x < -100 or self.pos.y > 600