def run_MVC():
    evManager = EventManager()
    gamemodel = ModelEngine(evManager)
    controller = control(evManager, gamemodel)
    gamemodel.run()

if __name__ == "__main__":
    from CombineVersion.MVC.Model import *
    from CombineVersion.MVC.Controller import *
    from CombineVersion.MVC.EventManager import *
    run_MVC()
    # from CombineVersion.Processes.GameProcess.ui.ScoreBoard import ScoreBoard
    # import multiprocessing
    # ScoreBoard().run(multiprocessing.Value('i', 1))
