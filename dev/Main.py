from dev.Components.function.CV2_engine import cv2_engine
from dev.Components.function.FPS_engine import FPS_engine
from dev.Components.mediapipe.mediapipe_engine import *


def run():
    CV2_engine = cv2_engine()
    fps_engine = FPS_engine()
    Mediapipe_engine = mediapipe_holistic_engine()
    while True:
        success, img = CV2_engine.read_camera()
        fps_engine.get_fps()
        img = fps_engine.display(img)
        CV2_engine.display_camera()
        if CV2_engine.check_exit():
            break

if __name__ == "__main__":
    run()