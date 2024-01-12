import time
import cv2


class FPS_Engine:
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

    def display(self,img):
        cv2.putText(img, str(int(self.fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)
        return img