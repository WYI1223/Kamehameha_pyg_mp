def run_MVC():
    evManager = EventManager()
    gamemodel = ModelEngine(evManager)
    controller = control(evManager, gamemodel)
    gamemodel.run()


# if __name__ == "__main__":
#     from dev.Components.function.CV2_Engine import CV2_Engine
#     from dev.Components.function.FPS_Engine import FPS_Engine
#     from dev.Components.mediapipe.mediapipe_engine import *
#     run()

if __name__ == "__main__":
    from dev.MVC.Model import *
    from dev.MVC.Controller import *
    from dev.MVC.EventManager import *
    run_MVC()
