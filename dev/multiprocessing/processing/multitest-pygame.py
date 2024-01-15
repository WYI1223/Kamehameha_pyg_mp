import queue
import pygame
from pygame.locals import *
from loguru import logger
import cv2
import threading
import multiprocessing
import time
from dev.multiprocessing.cameraIO.CV2_Engine import CameraCapture
from dev.Components.function.FPS_Engine import FPS_Engine
from dev.Components.mediapipe.mediapipe_engine import *
from dev.multiprocessing.detector.detector import *
from dev.Components.Math import MathCompute
import pygame_subprocessing


class Multitest:
    def __init__(self, queue):
        self.cameraCapture = CameraCapture()
        self.cameraCapture.start()
        logger.info("CameraCapture is start")
        time.sleep(1)
        self.result_images = queue.Queue()

        self.input_order = multiprocessing.Value('i', 0)
        self.images_queue = queue

        self.pool = multiprocessing.Pool(multiprocessing.cpu_count() // 2)

    def result_callback(self, result):
        # 将结果添加到队列
        self.result_images.put(result)
        logger.warning("result_callback is running")
        if self.input_order.value % 50 == 0:
            logger.info("result_images size:{}", self.result_images.qsize())

    def display_image(self):
        image_buffer = {}
        expected_frame = 0
        image_surface = None

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_q):
                    running = False

            image = None
            pose_landmarks = None
            Left_Hand_Landmarks = None
            Right_Hand_Landmarks = None

            if expected_frame not in image_buffer:
                if not self.result_images.empty():
                    frame_count, image, pose_landmarks, Left_Hand_Landmarks, Right_Hand_Landmarks = self.result_images.get()
                    if frame_count == expected_frame:
                        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        expected_frame += 1
                    else:
                        image_buffer[frame_count] = (image, pose_landmarks, Left_Hand_Landmarks, Right_Hand_Landmarks)
                else:
                    if len(image_buffer) > 0:
                        expected_frame = min(image_buffer.keys())
                        logger.warning("Losing frame!")
                    else:
                        continue
            else:
                image, pose_landmarks, Left_Hand_Landmarks, Right_Hand_Landmarks = image_buffer.pop(expected_frame)
                expected_frame += 1

            if image is not None:
                # Convert the image from BGR to RGB
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                # Create a surface using the RGB image
                image_surface = pygame.surfarray.make_surface(image_rgb)

                # 将image_surface加入到一个队列中，然后在run_game这一子进程中显示
                self.images_queue.put(image_surface)

        self.close_pool()
    def handle_image(self):
        while True:
            time.sleep(1.0/60.0)
            image = self.cameraCapture.get_frame()
            if self.result_images.qsize() > 10:
                logger.debug("result_images is full")
                time.sleep(0.1)
                continue
            with self.input_order.get_lock():
                order = self.input_order.value + 1
                self.input_order.value = order
            self.pool.apply_async(MathCompute.process_image, args=(order, image), callback=self.result_callback)

    def close_pool(self):
        self.pool.close()
        self.pool.join()


def main():
    pygame.init()
    multitest = Multitest()
    multitest.display_image()


if __name__ == '__main__':
    main()
