from dev.MVC.EventManager import *
import dev.MVC.View as view
from dev.Components.function.FPS_Engine import FPS_Engine
from dev.Components.function.CV2_Engine import CV2_Engine
from dev.Components.mediapipe.mediapipe_engine import *
import cv2
import pygame


class control(object):
    def __init__(self, evManager, model):
        self.evManager = evManager
        evManager.RegisterListener(self)
        self.model = model
        self.pageinitilized = False

        self.model.CV2_class = None

    def initialize(self):
        """
        Initialize view.
        """
        self.graphics = view.UI_View(self.evManager, self.model)
        self.graphics.initialize()

    def input_event(self):
        self.model.input_event = pygame.event.get()
        # pass
        for event in self.model.input_event:

            # handle window manager closing our window
            if event.type == pygame.QUIT:
                self.graphics.quit_pygame()
                self.evManager.Post(QuitEvent())

    def notify(self, event):
        """
        Receive events posted to the message queue.
        """
        if isinstance(event, InitializeEvent):
            self.initialize()

        # if the state is changing, reset the pageinitilized flag
        elif isinstance(event, StateChangeEvent):
            self.pageinitilized = False
            print("State change event")

        elif isinstance(event, TickEvent):

            self.model.currentstate = self.model.state.peek()
            if self.pageinitilized == False:
                """
                Initialize new page
                """
                if self.model.CV2_class == None:
                    self.model.CV2_class = CV2_Engine()
                self.model.FPS_class = FPS_Engine()
                # self.model.Mediapipe_Holistic_class = mediapipe_holistic_engine()
                print("New page initialized")
                # self.model.segmentation_class = segmentation_engine()

                self.pageinitilized = True

            """
            Handle all Business Logic
            """

            # Get camera image from CV2
            self.model.success, self.model.img = self.model.CV2_class.read_camera()  # read camera

            if self.model.success:
                # Calculate FPS
                self.model.FPS_class.get_fps()
                # self.model.Mediapipe_Holistic_class.process_image(self.model.img)

                """
                Tell view to render after all Business Logic
                """
                self.graphics.render()
            self.input_event()

