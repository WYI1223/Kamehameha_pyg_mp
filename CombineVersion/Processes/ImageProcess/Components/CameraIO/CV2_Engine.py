import time
import cv2
import threading


class CameraCapture(threading.Thread):
    def __init__(self):
        super().__init__()


    class CameraApp:
        def __init__(self):
            super().__init__()
            self.cap = None
            self.lock = threading.Lock()
            self.frame = None
            self.running = True

        def list_cameras(self):
            available_cameras = []
            for i in range(5):  # 假设检查前10个索引
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    available_cameras.append(i)
                    cap.release()
            return available_cameras

        def select_camera(self, camera_index):
            self.cap = cv2.VideoCapture(camera_index)
            if not self.cap.isOpened():
                print("无法打开摄像头")
                return False
            width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            print(f"当前摄像头设置：宽度={width}, 高度={height}, FPS={fps}")
            return True

        def set_camera_parameters(self, width, height, fps):
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.cap.set(cv2.CAP_PROP_FPS, fps)

    # 使用
    app = CameraApp()
    cameras = app.list_cameras()

    if cameras:
        print("可用摄像头索引:", cameras)
        try:
            chosen_index = int(input("请选择一个摄像头索引: "))
            if chosen_index in cameras:
                if app.select_camera(chosen_index):
                    # 用户可以选择设置新的参数
                    app.set_camera_parameters(1920, 1080, 60)
            else:
                print("无效的摄像头索引。")
        except ValueError:
            print("请输入有效的数字索引。")
    else:
        print("未检测到可用摄像头。")

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
