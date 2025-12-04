import pygame
import math

class Note:
    def __init__(self, pos: pygame.Vector2, img):
        self.original_pos = pos.copy()
        self.pos = pos.copy()
        self.img = img
        self.jumping = False
        self.jumped = False
        self.v = pygame.Vector2(0, 0)
        self.a = pygame.Vector2(0, 5000)

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
        return self.pos
    
    def should_jump(self):
        return not self.is_jumping() and not self.has_jumped()
    
    def jump(self):
        self.jumping = True
        self.v.y = -1000

    def is_jumping(self):
        return self.jumping
    
    def has_jumped(self):
        return self.jumped
