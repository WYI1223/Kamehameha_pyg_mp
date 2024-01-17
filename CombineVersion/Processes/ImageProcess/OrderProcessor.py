import multiprocessing

from CombineVersion.Processes.ImageProcess.Components.FPS_Engine.FPS_Engine import FPS_Engine
from CombineVersion.Processes.ImageProcess.Components.Detector.detector_engine import *


class OrderProcessor(multiprocessing.Process):
    def __init__(self, result_images, image_queue,state_machine):
        super().__init__()
        self.result_images = result_images
        self.image_queue = image_queue
        self.statemachine = state_machine


    def detect_Method(self, statemachine, detector, image_out):
        if statemachine == 4:
            return 4

        if detector.draw_box(image_out):
            attack = detector.detect()
            if attack is not False and attack > 1:
                statemachine = attack
            else:
                if detector.jump_detect():
                    statemachine = 5
                elif detector.sit_detect():
                    statemachine = 6
                else:
                    statemachine = 1
        else:
            statemachine = 8

        return statemachine



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
                            (20, 960), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)
                cv2.putText(image_out, f'FPS_low10: {fps_low10}',
                            (20,980),cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)
                cv2.putText(image_out, f'FPS_low50: {fps_low50}',
                            (20, 1000), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)

                detector.datainput(pose_landmarks, left_hand_landmark=Left_Hand_Landmarks,
                                   right_hand_landmark=Right_Hnad_Landmarks)

                statemachine = self.statemachine.value

                statemachine = self.detect_Method(statemachine, detector, image_out)

                if statemachine != self.statemachine.value:
                    with self.statemachine.get_lock():
                        self.statemachine.value = statemachine
                        logger.info(f"state: {self.statemachine.value}")

                self.image_queue.put(image_out)
    def stop(self):
        self.result_images.close()
        self.image_queue.close()
        self.terminate()
        print("OrderProcessor is stop")
        self.join()
