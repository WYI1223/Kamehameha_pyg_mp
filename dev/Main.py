from dev.Components.function.CV2_engine import cv2_engine
from dev.Components.function.FPS_engine import FPS_engine
from dev.Components.mediapipe.mediapipe_engine import *


def run():
    cv2_engine = cv2_engine()
    fps_engine = FPS_engine()
    mediapipe_engine = mediapipe_engine()
    while True:
        success, img = cv2_engine.read_camera()
        fps_engine.get_fps()
        cv2_engine.display_camera()
        if cv2_engine.check_exit():
            break

if __name__ == "__main__":
    run()