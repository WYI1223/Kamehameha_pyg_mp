from dev.Components.mediapipe.mediapipe_engine import *
import multiprocessing


class mediapipe_subprocess(multiprocessing.Process):

    def __init__(self, process_queue: multiprocessing.Queue, result_queue: multiprocessing.Queue):
        super().__init__()
        self.process_queue = process_queue
        self.result_queue = result_queue
        self.running = True
        self.holistic = None


    def run(self):

        self.holistic = mediapipe_holistic_engine()
        while self.running:
            order, image = self.process_queue.get()
            self.holistic.process_image(image)
            self.holistic.draw_all_landmark_drawing_utils(image)
            pose_landmarks = self.holistic.results.pose_landmarks
            left_hand_landmarks = self.holistic.results.left_hand_landmarks
            right_hand_landmarks = self.holistic.results.right_hand_landmarks

            self.result_queue.put((order, image, pose_landmarks, left_hand_landmarks, right_hand_landmarks))

    def stop(self):
        self.running = False
        self.join()