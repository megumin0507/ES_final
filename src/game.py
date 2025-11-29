import pygame
import queue
import logging
from src.ble import BLE
from src.scene import Scene

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
        self.scene = Scene(self.screen)

        self.device_index = 0
        self.buttons = 0
        self.time = 0

        self.dt = 0
        self.running = True

    def loop(self, ble: BLE):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            try:
                while True:
                    pkt = ble.retrieve_pkt()
                    self.device_index = pkt.device_index
                    self.buttons = pkt.buttons
                    self.time = pkt.time
            except queue.Empty:
                pass
            
            self.scene.run()
            pygame.display.flip()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_q]:
                self.running = False

            self.dt = self.clock.tick(60) / 1000

    def quit(self):
        pygame.quit()