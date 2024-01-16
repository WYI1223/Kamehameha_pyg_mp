import threading
import multiprocessing

from dev.multiprocessing.processing.display_subprocess import DisplayImageProcess
from dev.multiprocessing.processing.subprocess_mediapipe import mediapipe_subprocess
from dev.multiprocessing.cameraIO.CV2_Engine import CameraCapture
from dev.Components.function.FPS_Engine import FPS_Engine
from dev.Components.function.detector_engine import *
from dev.multiprocessing.processing.pygame_engine import GameProcess


class ImageProcessor(multiprocessing.Process):
    def __init__(self, image_queue: multiprocessing.Queue, state_machine: multiprocessing.Value):
        super().__init__()
        self.cameraCapture = None
        self.result_images = None
        self.display_image_process = None
        self.input_order = 0

        self.image_queue = image_queue
        self.process_queue = None
        self.running = True
        self.processes = []
        self.statemachine = state_machine

    def display_image(self, result_images, image_queue):

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
                frame_count, image, pose_landmarks, Left_Hand_Landmarks, Right_Hnad_Landmarks = result_images.get()
                    # print(f"Received frame {frame_count}")

                if frame_count == expected_frame:
                    image_out = image
                    expected_frame += 1
                else:
                    image_buffer[frame_count] = (image, pose_landmarks, Left_Hand_Landmarks, Right_Hnad_Landmarks)

            else:
                # 如果缓冲区中有图像，显示图像
                image_out, pose_landmarks, Left_Hand_Landmarks, Right_Hnad_Landmarks = image_buffer.pop(expected_frame)
                expected_frame += 1

            if image_out is not None:

                fps_engine.get_fps()
                fps_averge = fps_engine.get_average_fps()
                fps_low10 = fps_engine.get_low10_fps()
                fps_low50 = fps_engine.get_low50_fps()
                cv2.putText(image_out, f'FPS_averge: {fps_averge}',
                            (20, 70), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 3)
                cv2.putText(image_out, f'FPS_low10: {fps_low10}',
                            (40,70),cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 3)
                cv2.putText(image_out, f'FPS_low50: {fps_low50}',
                            (60, 70), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 3)

                detector.datainput(pose_landmarks, left_hand_landmark=Left_Hand_Landmarks,
                                   right_hand_landmark=Right_Hnad_Landmarks)

                detector.detect()
                detector.sit_detect()
                jumpdetector.datainput(pose_landmarks)
                jumpdetector.jump()

                image_queue.put(image_out)

    def get_photos(self):
        while self.running:
            self.process_queue.put((self.input_order, self.cameraCapture.get_frame()))
            self.input_order += 1
            time.sleep(1.0 / 60.0)
            if self.process_queue.full():
                logger.warning("process Queue is full!")
            if self.result_images.full():
                logger.warning("Result Queue is full!")
            if self.image_queue.full():
                logger.warning("image Queue is full!")

            if self.statemachine.value == 0:
                self.running = False
                self.close()

    def handle_image(self):
        num = 2
        for _ in range(num):
            process = mediapipe_subprocess(self.process_queue, self.result_images)
            process.start()
            self.processes.append(process)

    def close(self):
        for process in self.processes:
            process.stop()
            process.join()

    def run(self):
        self.cameraCapture = CameraCapture()
        self.result_images = multiprocessing.Queue(8)
        self.process_queue = multiprocessing.Queue(8)
        # self.display_image_thread = threading.Thread(target=self.display_image,
        #                                              args=(self.result_images, self.image_queue), daemon=True)
        self.display_image_process = DisplayImageProcess(self.result_images, self.image_queue)
        self.cameraCapture.start()
        logger.info("CameraCapture is start")

        time.sleep(1)
        self.display_image_process.start()
        self.handle_image()
        self.get_photos()

    # 其余的方法保持不变


# 使用示例
if __name__ == '__main__':
    image_queue = multiprocessing.Queue(20)

    statemachine = multiprocessing.Value('i', 1)

    multitest_process = ImageProcessor(image_queue, statemachine)
    game_process = GameProcess(image_queue, statemachine)

    game_process.start()
    multitest_process.start()

    game_process.join()
    multitest_process.join()
