import time
import cv2


class FPS_Engine:
    """
    计算帧率
    """
    def __init__(self):
        self.ptime = 0
        self.fps = 0
        self.fps_list = []
    def get_fps(self):
        ctime = time.time()
        try:
            self.fps = 1 / (ctime - self.ptime)
        except:
            print("FPS计算错误")
        self.ptime = ctime
        self.fps_list.append(self.fps)
        if len(self.fps_list) > 10:
            self.fps_list.pop(0)
        return self.fps

    def display_FPS(self,img):
        cv2.putText(img, str(int(self.fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)
        return img

    def get_average_fps(self):
        return sum(self.fps_list)/len(self.fps_list)