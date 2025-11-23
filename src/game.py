import pygame
import queue
import logging
from src.ble import BLE

logger = logging.getLogger(__name__)

class Game:
    def __init__(self, ble, resolution):
        self.ble = ble
        self.resolution = resolution

    def run(self):
        self.init()
        self.loop(self.ble)
        self.quit()

    def init(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.resolution)
        self.clock = pygame.time.Clock()

        self.pos = pygame.Vector2(self.screen.get_width() / 2, self.screen.get_height() / 2)
        self.button_img = pygame.image.load("sprites\\L_Red.png").convert_alpha()
        self.button_img = pygame.transform.scale_by(self.button_img, 0.5)

        self.buttons_state = 0
        self.x_axis = 0
        self.y_axis = 0

        self.dt = 0
        self.running = True

    def loop(self, ble: BLE):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.screen.fill(pygame.Color(239, 233, 227))

            try:
                while True:
                    pkt = ble.retrieve_pkt()
                    self.buttons_state = pkt.buttons
                    self.x_axis = pkt.x
                    self.y_axis = pkt.y
            except queue.Empty:
                pass

            self.pos.x = max(0, min(800, self.pos.x + self.x_axis * self.dt))
            self.pos.y = max(0, min(600, self.pos.y + self.y_axis * self.dt))

            self.screen.blit(self.button_img, self.pos)

            pygame.display.flip()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_q]:
                self.running = False

            self.dt = self.clock.tick(60) / 1000

    def quit(self):
        pygame.quit()