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

        self.running = True
        self.player_sequence = []
        self.score_result = None

        self.last_switch_time = pygame.time.get_ticks() 
        self.switch_interval = 5000*4/3 

    def loop(self, ble: BLE):
        while self.running:
            
            dt = self.clock.tick(60) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Set a new sequence
            current_time = pygame.time.get_ticks()
            if current_time - self.last_switch_time > self.switch_interval:
                if self.score_result is None:
                     self.calculate_score(is_timeout=True)
                self.scene.set_random_sequence() 
                self.last_switch_time = current_time
                self.player_sequence = []
                self.score_result = None 
            
            try:
                while True:
                    pkt = ble.retrieve_pkt()
                    self.device_index = pkt.device_index
                    self.buttons = pkt.buttons
                    self.time = pkt.time

                    motion =  self.device_index*2 + self.buttons-1 
                    if self.score_result is None:
                        self.player_sequence.append(motion)
                        # 檢查動作數量 (Pattern Finished)
                        if len(self.player_sequence) >= len(self.scene.answer):
                            self.calculate_score(is_timeout=False)
                    
                    # display
                    self.scene.show_user_motion(motion, len(self.player_sequence) - 1)

            except queue.Empty:
                pass
            
            self.scene.run(dt)

            # 如果有結果，畫出結果文字 (Perfect / Fail)
            if self.score_result:
                self.scene.draw_result_text(self.score_result)
            pygame.display.flip()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_q]:
                self.running = False

    def calculate_score(self, is_timeout=False):
        target = self.scene.answer
        actual = self.player_sequence
        
        # 狀況 A: 時間到但沒打完 -> Fail
        if is_timeout:
            self.score_result = "TIMEOUT FAIL"
            print(f"Time out! Input: {actual}, Target: {target}")
            return

        # 狀況 B: 數量不對 (理論上上面判斷過長度才會進來，這邊做個保險)
        if len(actual) != len(target):
            self.score_result = "LENGTH FAIL"
            return

        # 狀況 C: 逐字比對 (Algorithm)
        # 只要有一個不一樣就是 Fail，全部一樣才是 Perfect
        is_perfect = True
        for i in range(len(target)):
            if actual[i] != target[i]:
                is_perfect = False
                break
        
        if is_perfect:
            self.score_result = "PERFECT"
            print("PERFECT!")
            # 可以在這裡加分 self.score += 100
        else:
            self.score_result = "FAIL"
            print(f"FAIL! Input: {actual}, Target: {target}")

    def quit(self):
        pygame.quit()