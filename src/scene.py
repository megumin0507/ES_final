import pygame

sprites_dir = ".\\sprites\\"

class Scene:
    def __init__(self, screen: pygame.Surface):
        self._load_sprites()
        self.screen = screen

    def run(self):
        self.load_game_scene()

    def load_game_scene(self):
        self.screen.blit(self.background_img, (0, 0))
        self.screen.blit(self.textboxes_img, (0, 0))

    def _load_sprites(self):
        self.background_img = pygame.image.load(f"{sprites_dir}background.png").convert_alpha()
        self.textboxes_img = pygame.image.load(f"{sprites_dir}textbox.png").convert_alpha()
        self.L_blue_img = pygame.image.load(f"{sprites_dir}L_Blue.png").convert_alpha()
        self.L_red_img = pygame.image.load(f"{sprites_dir}L_Red.png").convert_alpha()
        self.R_blue_img = pygame.image.load(f"{sprites_dir}R_Blue.png").convert_alpha()
        self.R_red_img = pygame.image.load(f"{sprites_dir}R_Red.png").convert_alpha()
