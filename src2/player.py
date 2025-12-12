class Player:
    def __init__(self, device_idx):
        self.device_idx = device_idx
        self.sequence_class = []
        self.sequence_time = []
        self.score_result = None
    
    def reset(self):
        """重置玩家狀態"""
        self.sequence_class = []
        self.sequence_time = []
        self.score_result = None
    
    def add_motion(self, motion, time):
        """添加動作"""
        self.sequence_class.append(motion)
        if len(self.sequence_time) == 0:
            self.sequence_time.append(0)
        else:
            self.sequence_time.append(time)