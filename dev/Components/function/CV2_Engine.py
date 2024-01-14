import cv2
import time
import threading
import queue

class CV2_Engine:

    def __init__(self):
        # 使用 FrameCapture 类处理视频捕获
        self.frame_capture = FrameCapture()
        self.frame_capture.start()

    def read_camera(self):
        # 从 FrameCapture 队列中获取图像
        frame = self.frame_capture.read()
        return frame is not None, frame

    def save_camera(self):
        # 保存当前帧到文件
        success, img = self.read_camera()
        if success:
            cv2.imwrite("photos/{}.jpg".format(time.time()), img)

    def display_camera(self):
        # 显示当前帧
        success, img = self.read_camera()
        if success:
            cv2.imshow("Image", img)

    def check_exit(self):
        # 检查是否退出
        if cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty('Image', cv2.WND_PROP_VISIBLE) < 1:
            return True
        else:
            return False

    def release_camera(self):
        # 释放资源
        self.frame_capture.stop()
        cv2.destroyAllWindows()

class FrameCapture:
    def __init__(self, max_queue_size=10):
        self.capture = cv2.VideoCapture(0)  # 0 表示默认摄像头
        self.queue = queue.Queue(maxsize=max_queue_size)
        self.stopped = False

    def start(self):
        threading.Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return
            ret, frame = self.capture.read()
            if not ret:
                continue
            self.queue.put(frame)

    def read(self):
        return self.queue.get()

    def stop(self):
        self.stopped = True
        self.capture.release()
