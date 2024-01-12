from dev.Components.function.CV2_Engine import CV2_Engine
from dev.Components.function.FPS_Engine import FPS_Engine
from dev.Components.mediapipe.mediapipe_engine import *


def run():
    CV2_engine = CV2_Engine()
    fps_engine = FPS_Engine()
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