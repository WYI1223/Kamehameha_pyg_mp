import time

from dev.MVC.EventManager import *
import pygame
from pygame.locals import *
import pygame.freetype
import cv2


class UI_View(object):
    def __init__(self, evManager, model):
        self.evManager = evManager
        self.model = model

    def initialize(self):
        """
        Initialize the UI.
        """
        pygame.init()
        pygame.font.init()
        pygame.freetype.init()

        pygame.display.set_caption('Test_Project')

        # flags = FULLSCREEN | DOUBLEBUF
        flags = DOUBLEBUF

        if (pygame.display.get_num_displays() >= 2):
            screen_no = 1
        else:
            screen_no = 0

        self.model.screen = pygame.display.set_mode((1920,1080), flags, 16, display=screen_no, vsync=1)

        self.clock = pygame.time.Clock()

        # speedup a little bit
        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

    def quit_pygame(self):
        # shut down the pygame graphics
        self.isinitialized = False
        pygame.quit()


    def render(self):
        # Display FPS

        self.model.FPS_class.display_FPS(self.model.img)
        self.model.Mediapipe_Holistic_class.draw_all_landmark_drawing_utils(self.model.img)

        # 绘制人物所在框
        self.model.tpose_detector.draw_box(self.model.img)

        # 动作检测模组

        action = self.model.detector.detect()
        if action == 1:
            cv2.imwrite("photos/action1_{}.jpg".format(time.time()),self.model.img)
        elif action == 2:
            cv2.imwrite("photos/action2_{}.jpg".format(time.time()),self.model.img)
        elif action ==3:
            cv2.imwrite("photos/action3_{}.jpg".format(time.time()),self.model.img)

        # 跳跃检测模组
        if self.model.jump_detector.jump():
            cv2.imwrite("photos/Jump_{}.jpg".format(time.time()), self.model.img)

        # 蹲下检测模组
        # if self.model.detector.sit_detect():
        #     cv2.imwrite("photos/Sitdown_{}.jpg".format(time.time()), self.model.img)


        """
        Draw things on pygame
        """
        empty_color = pygame.Color(0, 0, 0, 0)
        self.model.screen.fill(empty_color)

        # Convert into RGB
        self.model.img = cv2.cvtColor(self.model.img, cv2.COLOR_BGR2RGB)

        # Convert the image into a format pygame can display

        self.model.img = pygame.image.frombuffer(self.model.img.tostring(), self.model.img.shape[1::-1], "RGB")

        # blit the image onto the screen
        self.model.screen.blit(self.model.img, (0, 0))


        # Update the screen
        pygame.display.flip()

        # limit the redraw speed to 30 frames per second
        self.clock.tick(60)