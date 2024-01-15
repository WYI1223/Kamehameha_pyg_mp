import queue
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


class Multitest:
    def __init__(self):
        self.cameraCapture = CameraCapture()
        self.cameraCapture.start()
        logger.info("CameraCapture is start")
        time.sleep(1)
        self.result_images = queue.Queue()
        self.display_image_thread = threading.Thread(target=self.display_image, args=(self.result_images,), daemon=True)

        self.display_image_thread.start()
        self.input_order = multiprocessing.Value('i', 0)

        self.pool = multiprocessing.Pool(multiprocessing.cpu_count() // 2)

    def result_callback(self, result):
        # 将结果添加到队列
        self.result_images.put(result)
        if self.input_order.value % 50 == 0:
            logger.info("result_images size:{}", self.result_images.qsize())

    def display_image(self, result_images):

        # 图片缓冲区
        image_buffer = {}
        expected_frame = 0
        image_out = None
        fps_engine = FPS_Engine()

        detector = attack_detector()

        jumpdetector = jump_detector()

        while True:
            pose_landmarks = None
            Left_Hand_Landmarks = None
            Right_Hnad_Landmarks = None
            # print("display_image is running")
            if expected_frame not in image_buffer:
                # 如果缓冲区中没有图像，从队列中获取图像
                if not result_images.empty():
                    frame_count, image, pose_landmarks, Left_Hand_Landmarks, Right_Hnad_Landmarks = result_images.get()
                    # print(f"Received frame {frame_count}")
                    if frame_count == expected_frame:
                        image_out = image
                        expected_frame += 1
                    else:
                        image_buffer[frame_count] = (image, pose_landmarks, Left_Hand_Landmarks, Right_Hnad_Landmarks)
                else:
                    # 将缓冲区最小的expected_frame显示出来
                    if len(image_buffer) > 0:
                        expected_frame = min(image_buffer.keys())
                        logger.warning("Losing frame!")
                    else:
                        time.sleep(1.0 / 60.0)
                        # logger.warning("No frame in queue!")
            else:
                # 如果缓冲区中有图像，显示图像
                image_out, pose_landmarks, Left_Hand_Landmarks, Right_Hnad_Landmarks = image_buffer.pop(expected_frame)
                expected_frame += 1
            if image_out is not None:
                fps_engine.get_fps()
                fps_averge = fps_engine.get_average_fps()
                fps_low10 = fps_engine.get_low10_fps()
                fps_low50 = fps_engine.get_low50_fps()
                cv2.putText(image_out, f'FPS_averge: {fps_averge}, FPS_low10: {fps_low10}, FPS_low50: {fps_low50}',
                            (20, 70), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 3)
                cv2.imshow('Processed Frame', image_out)

                detector.datainput(pose_landmarks, left_hand_landmark=Left_Hand_Landmarks, right_hand_landmark=Right_Hnad_Landmarks)

                detector.detect()
                detector.sit_detect()
                jumpdetector.datainput(pose_landmarks)
                jumpdetector.jump()

                if cv2.waitKey(5) == ord('q'):
                    break

    def handle_image(self):
        wait_time = 1.0 / 60.0

        while True:
            time.sleep(wait_time)
            image = self.cameraCapture.get_frame()
            if self.result_images.qsize() > 10:
                logger.debug("result_images is full")
                time.sleep(0.01)
                continue
            with self.input_order.get_lock():
                order = self.input_order.value + 1
                self.input_order.value = order
            self.pool.apply_async(MathCompute.process_image, args=(order, image), callback=self.result_callback)

    def close_pool(self):
        self.pool.close()
        self.pool.join()


def main():
    multitest = Multitest()
    multitest.handle_image()
    multitest.close_pool()


if __name__ == '__main__':
    main()
