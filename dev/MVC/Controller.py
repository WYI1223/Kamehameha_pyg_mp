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
        if self.model.add_button.CheckisClicked() == 'clicked':
            self.model.currentstate += 1
            self.evManager.Post(StateChangeEvent(self.model.currentstate))
        elif self.model.minus_button.CheckisClicked() == 'clicked':
            self.model.currentstate -= 1
            self.evManager.Post(StateChangeEvent(self.model.currentstate))

        self.model.input_event = pygame.event.get()
        # Called for each game tick. We check our keyboard presses here.

        for event in self.model.input_event:

            # handle window manager closing our window
            if event.type == pygame.QUIT:
                self.graphics.quit_pygame()
                self.evManager.Post(QuitEvent())

            # handle key down events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.evManager.Post(StateChangeEvent(None))

                # check key press for 1, 2, 3, 4, 5; if not same as current state, change state
                elif event.key == pygame.K_1:
                    self.evManager.Post(StateChangeEvent(1))

                elif event.key == pygame.K_2:
                    self.evManager.Post(StateChangeEvent(2))

                elif event.key == pygame.K_3:
                    self.evManager.Post(StateChangeEvent(3))

                elif event.key == pygame.K_4:
                    self.evManager.Post(StateChangeEvent(4))

                elif event.key == pygame.K_5:
                    self.evManager.Post(StateChangeEvent(5))

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
                self.graphics.init_page()

                if self.model.CV2_class == None:
                    self.model.CV2_class = CV2_Engine()
                self.model.FPS_class = FPS_Engine()
                self.model.Mediapipe_Holistic_class = mediapipe_holistic_engine()
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
                self.model.FPS_class.calculate_FPS()

                try:
                    # Mediapipe Pose
                    if self.model.currentstate == 2:
                        self.model.Mediapipe_pose_class.process_image(self.model.img)
                        # self.model.Mediapipe_pose_class.expand_landmark()

                    # Mediapipe Hand
                    elif self.model.currentstate == 3:
                        self.model.Mediapipe_hand_class.process_image(self.model.img)

                    # Mediapipe FaceMesh
                    elif self.model.currentstate == 4:
                        self.model.Mediapipe_FaceMesh_class.process_image(self.model.img)

                    # Mediapipe Holistic
                    elif self.model.currentstate == 5:
                        self.model.Mediapipe_Holistic_class.process_image(self.model.img)
                except Exception as e:
                    print(e)
                    import traceback
                    traceback.print_exc()
                """
                Tell view to render after all Business Logic
                """
                self.graphics.render()

            self.input_event()

