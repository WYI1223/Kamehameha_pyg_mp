import time

from CombineVersion.MVC.EventManager import QuitEvent
from CombineVersion.Processes.GameProcess.Game_Engine import Game_Engine


class UI_View(object):
    def __init__(self, evManager, model):
        self.evManager = evManager
        self.model = model

    def initialize(self):
        """
        Initialize the UI.
        """
        self.model.GameProcess = Game_Engine(self.model.image_queue, self.model.STATE_MACHINE)
        self.model.GameProcess.start()

    def quit_pygame(self):
        # shut down the pygame graphics
        self.model.STATE_MACHINE = 0
        self.isinitialized = False




    def render(self):
        pass

