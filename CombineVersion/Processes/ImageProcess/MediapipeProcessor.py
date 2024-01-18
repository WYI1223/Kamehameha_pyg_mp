import os
import queue
import sys

from CombineVersion.Processes.ImageProcess.Components.Mediapipe.mediapipe_engine import *
import multiprocessing
import math

class mediapipe_subprocess(multiprocessing.Process):

    def __init__(self, process_queue: multiprocessing.Queue, result_queue: multiprocessing.Queue, isRunning_subprocess:multiprocessing.Event):
        super().__init__()
        self.process_queue = process_queue
        self.result_queue = result_queue
        self.running = isRunning_subprocess
        self.holistic = None

    def run(self):

        self.holistic = mediapipe_holistic_engine()

        while self.running.is_set():
            try:
                order, image = self.process_queue.get(timeout=1)
                self.holistic.process_image(image)
                self.holistic.draw_all_landmark_drawing_utils(image)

                pose_landmarks = self.holistic.results.pose_landmarks
                left_hand_landmarks = self.holistic.results.left_hand_landmarks
                right_hand_landmarks = self.holistic.results.right_hand_landmarks

                self.result_queue.put((order, image, pose_landmarks, left_hand_landmarks, right_hand_landmarks))
            except queue.Empty:
                continue
            except Exception as e:
                # 可以添加额外的异常处理逻辑
                print(f"发生异常: {e}")
                continue



    def stop(self):
        print("mediapipe_subprocess is stop")
        self.running.clear()
        # os._exit(0)
