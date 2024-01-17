from CombineVersion.Processes.ImageProcess.Components.Mediapipe.mediapipe_engine import *
import multiprocessing
import math

class mediapipe_subprocess(multiprocessing.Process):

    def __init__(self, process_queue: multiprocessing.Queue, result_queue: multiprocessing.Queue):
        super().__init__()
        self.process_queue = process_queue
        self.result_queue = result_queue
        self.running = True
        self.holistic = None

    # def calculate_distance(self,landmark1, landmark2):
    #     """
    #     Calculate the Euclidean distance between two landmarks.
    #
    #     Args:
    #     - landmark1 (object): The first landmark with x, y, (and optional z) attributes.
    #     - landmark2 (object): The second landmark with x, y, (and optional z) attributes.
    #
    #     Returns:
    #     - float: The Euclidean distance between the two landmarks.
    #     """
    #     if landmark1.visibility < 0.5 or landmark2.visibility < 0.5:
    #         return False
    #
    #     x1, y1, z1 = landmark1.x, landmark1.y, landmark1.z
    #     x2, y2, z2 = landmark2.x, landmark2.y, landmark2.z
    #     return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)


        # self.hand = mediapipe_hand_engine()
        # self.pose = mediapipe_pose_engine()
    # self.hand.process_image(image)
    # self.pose.process_image(image)
    #
    # self.hand.draw_all_landmark_drawing_utils(image)
    # self.pose.draw_all_landmark_drawing_utils(image)
    #
    # left_hand_landmarks = None
    # right_hand_landmarks = None
    #
    #
    # if self.hand.detected and self.pose.detected:
    #     left_wrist_distance = self.calculate_distance(self.pose.Pixel_Landmark[15],
    #                                                   self.hand.Pixel_Landmark[0].landmark[17])
    #     right_wrist_distance = self.calculate_distance(self.pose.Pixel_Landmark[16],
    #                                                    self.hand.Pixel_Landmark[0].landmark[17])
    #     if left_wrist_distance < right_wrist_distance:
    #         left_hand_landmarks = self.hand.Pixel_Landmark[0]
    #         if len(self.hand.Pixel_Landmark) > 1:
    #             right_hand_landmarks = self.hand.Pixel_Landmark[1]
    #
    #     else:
    #         right_hand_landmarks = self.hand.Pixel_Landmark[0]
    #         if len(self.hand.Pixel_Landmark) > 1:
    #             left_hand_landmarks = self.hand.Pixel_Landmark[1]
    #
    # pose_landmarks = self.pose.results.pose_landmarks

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
        self.terminate()
        print("mediapipe_subprocess is stop")