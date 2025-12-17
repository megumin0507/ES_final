import pygame
import queue
import logging
from ble import BLE
from src1.scene import Scene

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
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.don = pygame.mixer.Sound('./sound/don.wav')
        self.ka = pygame.mixer.Sound('./sound/ka.wav')

        self.screen = pygame.display.set_mode(self.resolution)
        self.clock = pygame.time.Clock()
        self.scene = Scene(self.screen)

        self.device_index = 0
        self.buttons = 0
        self.time = 0

        self.running = False

        self.current_result_text = None 
        self.result_timer = 0
        self.combo = 0

        self.last_switch_time = pygame.time.get_ticks() 
        self.switch_interval = self.scene.switch_interval

    def loop(self, ble: BLE):
        logger.info("Waiting for BLE connection...")
        self.scene.draw_waiting_text("Waiting for BLE connection...")
        pygame.display.flip()
        
        while not ble.ble_connected[0] or not ble.ble_connected[1]:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
            pygame.time.wait(100)
        
        logger.info("BLE connected! Starting game...")
        self.scene.draw_waiting_text("BLE Connected! Starting...")
        pygame.display.flip()
        self.running = True
        pygame.time.wait(1000)

        while self.running:
            
            dt = self.clock.tick(60) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Set a new sequence
            current_time = pygame.time.get_ticks()
            if current_time - self.last_switch_time > self.switch_interval:
                self.scene.set_random_sequence() 
                self.switch_interval = self.scene.switch_interval
                self.last_switch_time = current_time
                self.current_result_text = None
            
            try:
                while True:
                    pkt = ble.retrieve_pkt()
                    self.device_index = pkt.device_index
                    self.buttons = pkt.buttons
                    self.time = pkt.time

                    motion =  self.device_index*2 + self.buttons-1 
                    if 0 <= motion <= 3:
                        self.handle_input(motion)
                        if self.buttons == 1:
                            self.ka.play()
                        elif self.buttons == 2:
                            self.don.play()

            except queue.Empty:
                pass
            
            self.scene.load_game_scene(dt)
            for note in self.scene.Q_notes:
                if not note.is_hit:
                    if note.pos.x + self.scene.GOOD_THRESHOLD - self.scene.TARGET_X < -self.scene.GOOD_THRESHOLD:
                        self.combo = 0
                        note.is_hit = True
                        self.current_result_text = "MISS"
                        self.result_timer = 0.5
                        break
                if note.is_out_of_screen():
                    self.scene.Q_notes.remove(note)
            self.scene.draw_combo(self.combo)

            if self.current_result_text and self.result_timer > 0:
                self.scene.draw_result_text(self.current_result_text)
                self.result_timer -= dt

            pygame.display.flip()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_q]:
                self.running = False

    def handle_input(self, motion_id):
        """處理輸入判定"""
        # 呼叫 Scene 檢查是否打中
        result = self.scene.check_input_hit(motion_id)
        
        if result:
            self.current_result_text = result
            self.result_timer = 0.5 # 文字顯示 0.5 秒
            
            if result == "PERFECT":
                # 在這裡加combo
                self.combo += 1
            else:
                self.combo = 0

    def quit(self):
        pygame.quit()