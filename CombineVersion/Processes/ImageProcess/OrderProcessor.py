import multiprocessing

from CombineVersion.Processes.ImageProcess.Components.FPS_Engine.FPS_Engine import FPS_Engine
from CombineVersion.Processes.ImageProcess.Components.Detector.detector_engine import *


class OrderProcessor(multiprocessing.Process):
    def __init__(self, result_images, image_queue):
        super().__init__()
        self.result_images = result_images
        self.image_queue = image_queue

    def run(self):
        # 这里是您的 display_image 方法的代码
        image_buffer = {}
        expected_frame = 0
        image_out = None
        fps_engine = FPS_Engine()

        detector = attack_detector()

        while True:
            pose_landmarks = None
            Left_Hand_Landmarks = None
            Right_Hnad_Landmarks = None

            if expected_frame not in image_buffer:
                frame_count, image, pose_landmarks, Left_Hand_Landmarks, Right_Hnad_Landmarks = self.result_images.get()

                if frame_count == expected_frame:
                    image_out = image
                    expected_frame += 1
                else:
                    image_buffer[frame_count] = (image, pose_landmarks, Left_Hand_Landmarks, Right_Hnad_Landmarks)
            else:
                image_out, pose_landmarks, Left_Hand_Landmarks, Right_Hnad_Landmarks = image_buffer.pop(expected_frame)
                expected_frame += 1

            if image_out is not None:

                fps_engine.get_fps()
                fps_averge = fps_engine.get_average_fps()
                fps_low10 = fps_engine.get_low10_fps()
                fps_low50 = fps_engine.get_low50_fps()
                cv2.putText(image_out, f'FPS_averge: {fps_averge}',
                            (20, 800), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 3)
                cv2.putText(image_out, f'FPS_low10: {fps_low10}',
                            (20,900),cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 3)
                cv2.putText(image_out, f'FPS_low50: {fps_low50}',
                            (20, 1000), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 3)

                detector.datainput(pose_landmarks, left_hand_landmark=Left_Hand_Landmarks,
                                   right_hand_landmark=Right_Hnad_Landmarks)

                detector.detect()
                detector.jump_detect()
                detector.sit_detect()

                self.image_queue.put(image_out)

