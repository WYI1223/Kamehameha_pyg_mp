import time
import cv2
import threading


class CameraCapture(threading.Thread):
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(1)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))  # set codec
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # set width
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)  # set height
        self.cap.set(cv2.CAP_PROP_FPS, 60)  # set fps
        self.lock = threading.Lock()
        self.frame = None
        self.running = True

    def run(self):
        while self.running:
            time.sleep(1.0 / 60.0)
            ret, frame = self.cap.read()
            if ret:
                start_x = (1920 - 680) // 2
                end_x = start_x + 680
                # 裁剪图像
                frame = frame[:, start_x:end_x]
                with self.lock:
                    self.frame = frame

    def get_frame(self):
        with self.lock:
            return self.frame

    def stop(self):
        self.running = False
        self.cap.release()

#
# if __name__ == '__main__':
#     from dev.Components.function.FPS_Engine import FPS_Engine
#
#     print(1)
#     # 使用示例
#     camera = CameraCapture()
#     print(2)
#     camera.start()
#     print(3)
#     fps_engine = FPS_Engine()
#
#     try:
#         while True:
#             frame = camera.get_frame()
#             if frame is not None:
#                 fps = fps_engine.get_fps()
#                 cv2.putText(frame, f'FPS: {fps}', (20, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
#                 cv2.imshow("Frame", frame)
#             if cv2.waitKey(1) == ord('q'):
#                 break
#     except KeyboardInterrupt:
#         pass
#     finally:
#         camera.stop()
#         camera.join()
#         cv2.destroyAllWindows()
