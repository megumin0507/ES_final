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

        self.running = False
        self.score_result = None
        
        self.player_sequence_class = []
        self.player_sequence_time = []

        self.last_switch_time = pygame.time.get_ticks() 
        self.switch_interval = self.scene.switch_interval

    def loop(self, ble: BLE):
        # 等待 BLE 連接
        logger.info("Waiting for BLE connection...")
        self.scene.draw_waiting_text("Waiting for BLE connection...")
        pygame.display.flip()
        
        while not ble.ble_connected:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
            pygame.time.wait(100)  # 避免 CPU 空轉
        
        logger.info("BLE connected! Starting game...")
        self.scene.draw_waiting_text("BLE Connected! Starting...")
        pygame.display.flip()
        self.running = True
        pygame.time.wait(1000)  # 顯示 1 秒後開始

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
                self.switch_interval = self.scene.switch_interval
                self.last_switch_time = current_time
                self.player_sequence_class = []
                self.player_sequence_time = []
                self.score_result = None 
            
            try:
                while True:
                    pkt = ble.retrieve_pkt()
                    self.device_index = pkt.device_index
                    self.buttons = pkt.buttons
                    self.time = pkt.time

                    motion =  self.device_index*2 + self.buttons-1 
                    if motion < 0 or motion > 3:
                        print("invalid motion")
                        continue
                        
                    if self.score_result is None:
                        self.player_sequence_class.append(motion)
                        if len(self.player_sequence_time)==0:
                            self.player_sequence_time.append(0)
                        else:
                            self.player_sequence_time.append(self.time)
                        # 檢查動作數量 (Pattern Finished)
                        if len(self.player_sequence_class) >= self.scene.ans_length:
                            self.calculate_score(is_timeout=False)  
                        # display
                        print(sum(self.player_sequence_time))
                        self.scene.show_user_motion(motion, sum(self.player_sequence_time)) # time

            except queue.Empty:
                pass
            
            self.scene.load_game_scene(dt)

            # 如果有結果，畫出結果文字 (Perfect / Fail)
            if self.score_result:
                self.scene.draw_result_text(self.score_result)
            pygame.display.flip()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_q]:
                self.running = False

    def calculate_score(self, is_timeout=False):
        ans_class = self.scene.ans_class
        ans_time = self.scene.ans_time
        ans_length = self.scene.ans_length
        player_class = self.player_sequence_class
        player_time = self.player_sequence_time
        
        # 時間到但沒打完 or 沒打 -> Fail
        if is_timeout or len(player_class)==0:
            self.score_result = "TIMEOUT FAIL"
            print(f"Time out!")
            return


        # 逐字比對 (Algorithm)
        # 只要有一個不一樣就是 Fail
        quality = 2
        for i in range(ans_length):
            if player_class[i] % 2 != ans_class[i]%2:
                quality= 0
                break
        else:
            # rhythm
            player_time[0] = 0
            loss = 0
            for i in range(ans_length):
                loss += abs(player_time[i] - ans_time[i])
            if loss > 300: # threshold可調
                quality = 1
            print(f"Total time loss: {loss} ms")
        
        if quality==2:
            self.score_result = "PERFECT"
            print("PERFECT!")
            # 可以在這裡加分 self.score += 100
        elif quality==1:
            self.score_result = "GOOD"
            print("GOOD!")
        else:
            self.score_result = "FAIL"
            print(f"FAIL! Input: {player_class}, Target: {ans_class}")

    def quit(self):
        pygame.quit()