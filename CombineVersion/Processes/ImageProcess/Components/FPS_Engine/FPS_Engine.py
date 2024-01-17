import heapq
import time
from collections import deque
import cv2


class FPS_Engine:
    """
    计算帧率
    """
    def __init__(self):
        self.ptime = 0
        self.fps = 0
        self.fps_list = deque(maxlen=100)
        self.total_fps = 0

    def get_fps(self):
        ctime = time.time()
        try:
            self.fps = 1 / (ctime - self.ptime)
        except ZeroDivisionError:
            print("FPS计算错误")
        self.ptime = ctime
        if len(self.fps_list) == 100:
            self.total_fps -= self.fps_list[0]
        self.fps_list.append(self.fps)
        self.total_fps += self.fps

        return round(self.fps)

    def get_average_fps(self):
        if len(self.fps_list) == 0:
            return 0
        return round(self.total_fps / len(self.fps_list))

    def get_low10_fps(self):
        smallest_10 = heapq.nsmallest(10, self.fps_list)
        return round(sum(smallest_10) / len(smallest_10))

    def get_low50_fps(self):
        if len(self.fps_list) < 50:
            return round(sum(self.fps_list) / len(self.fps_list)) if self.fps_list else 0
        return round(sum(heapq.nsmallest(50, self.fps_list)) / 50)

    def display_FPS(self, img):
        fps_rounded = round(self.fps)
        cv2.putText(img, str(fps_rounded), (10, 80), cv2.FONT_HERSHEY_PLAIN, 0, (255, 0, 255), 1)
        return img


