import pygame
import math

sprites_dir = ".\\sprites\\"

class Note:
    def __init__(self, pos: pygame.Vector2, target_x: float, id, speed: float, length=0):
        self.original_pos = pos.copy()
        self.pos = pos.copy()
        self.target_x = target_x
        self.speed = speed
        self.length = length
        self.id = id
        self.jumping = False
        self.is_hit = False
        self.v = pygame.Vector2(-self.speed, 0)
        self.a = pygame.Vector2(0, 0)
        self._load_sprites()
        options = [
            self.Blue_img,
            self.Red_img,
            self.Yellow_img
        ]
        self.img = options[id]

    def _load_sprites(self):
        def scale(img, scale_factor=0.5):
            new_width = int(img.get_width() * scale_factor)
            new_height = int(img.get_height() * scale_factor)
            return pygame.transform.smoothscale(img, (new_width, new_height))
        
        self.Blue_img = scale(pygame.image.load(f"{sprites_dir}Blue.png").convert_alpha())
        self.Red_img = scale(pygame.image.load(f"{sprites_dir}Red.png").convert_alpha())
        self.Yellow_img = scale(pygame.image.load(f"{sprites_dir}Yellow.png").convert_alpha())

    def get_img(self):
        if self.id == 2 and self.length > 0:
            # 建立一個包含 "尾巴 + 音符頭" 的新 Surface
            w, h = self.img.get_size()
            total_width = w + int(self.length)
            
            # 建立透明背景
            combined_surf = pygame.Surface((total_width, h), pygame.SRCALPHA)
            
            # 1. 畫尾巴 (黃色長方形，置中)
            # 尾巴從音符頭的一半開始，往後延伸
            rect_color = (255, 200, 0) # 黃色
            rect_height = h // 2       # 尾巴高度設為音符的一半
            rect_y = (h - rect_height) // 2
            
            # 畫在音符頭的後面 (從中心點往右延伸)
            pygame.draw.rect(combined_surf, rect_color, (w//2, rect_y, self.length, rect_height))
            
            # 2. 畫音符頭 (蓋在尾巴開頭上)
            combined_surf.blit(self.img, (0, 0))
            
            return combined_surf
        else:
            return self.img

    def get_pos(self, dt: float):
        self.v += self.a * dt
        self.pos += self.v * dt
        return self.pos
    
    def jump(self):
        self.jumping = True
        self.is_hit = True
        if self.id != 2:
            self.v.x = self.speed/2
            self.v.y = -1000
            self.a.y = 5000

    def is_out_of_screen(self):
        return self.pos.x < -1000 or self.pos.y > 720