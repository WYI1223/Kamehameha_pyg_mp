import time

from dev.MVC.EventManager import *
import pygame
from pygame.locals import *
import pygame.freetype
import cv2
from loguru import logger
from dev.multiprocessing.processing.pygame_engine import GameProcess


class UI_View(object):
    def __init__(self, evManager, model):
        self.evManager = evManager
        self.model = model

    def initialize(self):
        """
        Initialize the UI.
        """
        self.model.GameProcess = GameProcess(self.model.image_queue)
        self.model.GameProcess.start()

    def quit_pygame(self):
        # shut down the pygame graphics
        self.isinitialized = False
        pygame.quit()


    def render(self):


        pass

