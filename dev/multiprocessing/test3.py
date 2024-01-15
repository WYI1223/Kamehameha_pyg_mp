from dev.Components.mediapipe.mediapipe_engine import *
from dev.Components.function.FPS_Engine import FPS_Engine
from dev.Components.function.CV2_Engine import CV2_Engine
import cv2
import threading
import multiprocessing
import queue
import time

def capture_image(q, cv2_engine):
    sucess, image = cv2_engine.read_camera()
    if sucess:
        if not q.full():
            q.put(image)
        else:
            print("image_queue is full")
    # 重新安排下一次捕获
    threading.Timer(1.0 / 60, capture_image, [q, cv2_engine]).start()


def main():
    # 创建一个队列，最大大小为10
    image_queue = multiprocessing.Manager().Queue(10)

    # 创建并启动图像捕获线程
    cv2_engine = CV2_Engine()
    image_queue = multiprocessing.Manager().Queue(10)

    # 初始化定时器
    threading.Timer(1.0 / 60, capture_image, [image_queue, cv2_engine]).start()
    fps_engine = FPS_Engine()
    # 主线程中可以从队列中消费图像
    while True:
        try:
            image = image_queue.get(timeout=1)
            fps = fps_engine.get_fps()
            cv2.putText(image, f'FPS: {fps}', (20, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
            cv2.imshow("image", image)
            cv2.waitKey(1)
        except queue.Empty:
            print("image_queue is empty")
            time.sleep(1)
            continue
        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    main()
