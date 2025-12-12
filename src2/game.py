import pygame
import queue
import logging
from src2.ble import BLE
from src2.scene import Scene
from src2.player import Player

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

        # 創建兩個玩家
        self.p1 = Player(0)
        self.p2 = Player(1)

        self.running = False

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

            # 設置新序列
            current_time = pygame.time.get_ticks()
            if current_time - self.last_switch_time > self.switch_interval:
                # 計算超時的玩家
                if self.p1.score_result is None:
                    self.calculate_score(self.p1, is_timeout=True)
                if self.p2.score_result is None:
                    self.calculate_score(self.p2, is_timeout=True)
                
                # 設置新序列
                self.scene.set_random_sequence() 
                self.switch_interval = self.scene.switch_interval
                self.last_switch_time = current_time
                
                # 重置兩位玩家
                self.p1.reset()
                self.p2.reset()
            
            # 處理 BLE 輸入
            try:
                while True:
                    pkt = ble.retrieve_pkt()
                    device_index = pkt.device_index
                    button = pkt.buttons -1  # 0=側 1=下
                    time = pkt.time

                    if button<0 or button > 1:
                        print(button)
                        continue
                    # 選擇對應的玩家
                    player = self.p1 if device_index == 0 else self.p2
                    
                    # 如果該玩家還沒完成這回合
                    if player.score_result is None:
                        player.add_motion(button, time)
                        
                        # 檢查是否完成
                        if len(player.sequence_class) >= self.scene.ans_length:
                            self.calculate_score(player, is_timeout=False)
                        
                        # 顯示玩家動作
                        total_time = sum(player.sequence_time)
                        print(f"Player {device_index+1}: motion={button}, time={total_time}")
                        self.scene.show_user_motion(button, total_time, player)

            except queue.Empty:
                pass
            
            # 載入遊戲場景
            self.scene.load_game_scene(dt)

            # 顯示兩位玩家的結果
            if self.p1.score_result:
                self.scene.draw_result_text(self.p1)
            if self.p2.score_result:
                self.scene.draw_result_text(self.p2)
            
            pygame.display.flip()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_q]:
                self.running = False

    def calculate_score(self, player: Player, is_timeout=False):
        """計算單一玩家的分數"""
        ans_class = self.scene.ans_class
        ans_time = self.scene.ans_time
        ans_length = self.scene.ans_length
        
        # 時間到但沒打完 or 沒打
        if is_timeout or len(player.sequence_class) == 0:
            player.score_result = "TIMEOUT"
            print(f"Player {player.device_idx+1}: Time out!")
            return

        # 逐個比對動作
        quality = 2
        for i in range(ans_length):
            if player.sequence_class[i] != ans_class[i]:
                quality = 0
                break
        else:
            # 檢查節奏
            player.sequence_time[0] = 0
            loss = 0
            for i in range(ans_length):
                loss += abs(player.sequence_time[i] - ans_time[i])
            if loss > 300:  # threshold 可調
                quality = 1
            print(f"Player {player.device_idx+1}: Total time loss: {loss} ms")
        
        if quality == 2:
            player.score_result = "PERFECT"
            print(f"Player {player.device_idx+1}: PERFECT!")
        elif quality == 1:
            player.score_result = "GOOD"
            print(f"Player {player.device_idx+1}: GOOD!")
        else:
            player.score_result = "FAIL"
            print(f"Player {player.device_idx+1}: FAIL! Input: {player.sequence_class}, Target: {ans_class}")

    def quit(self):
        pygame.quit()