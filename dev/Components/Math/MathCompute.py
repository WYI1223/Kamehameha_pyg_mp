from dev.Components.mediapipe.mediapipe_engine import *

holistic_detection = mediapipe_holistic_engine()

def process_image(count, image):

    holistic_detection.process_image(image)
    holistic_detection.draw_all_landmark_drawing_utils(image)

    pose_landmarks = holistic_detection.results.pose_landmarks
    left_hand_landmarks = holistic_detection.results.left_hand_landmarks
    right_hand_landmarks = holistic_detection.results.right_hand_landmarks

    return (count, image, pose_landmarks, left_hand_landmarks, right_hand_landmarks)
