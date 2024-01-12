import time





class FPS_engine:
    """
    计算帧率
    """
    def __init__(self):
        self.ptime = 0
        self.fps = 0
    def get_fps(self):
        ctime = time.time()
        try:
            self.fps = 1 / (ctime - self.ptime)
        except:
            print("FPS计算错误")
        self.ptime = ctime
        return self.fps
