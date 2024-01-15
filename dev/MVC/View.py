import time

from dev.MVC.EventManager import *
import pygame
from pygame.locals import *
import pygame.freetype
import cv2
from loguru import logger


class UI_View(object):
    def __init__(self, evManager, model):
        self.evManager = evManager
        self.model = model

        self.expected_frame = 0
        self.image_out = None
        self.image_out_buffer = {}

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


        pose_landmarks = None
        Left_Hand_Landmarks = None
        Right_Hnad_Landmarks = None
        if self.expected_frame not in self.image_out_buffer:
            # 如果缓冲区中没有图像，从队列中获取图像
            if not self.model.result_images.empty():
                frame_count, image, pose_landmarks, Left_Hand_Landmarks, Right_Hnad_Landmarks = self.model.result_images.get()
                # print(f"Received frame self.expected_frame{frame_count}")
                if frame_count == self.expected_frame:
                    self.image_out = image
                    self.expected_frame += 1
                else:
                    self.image_out_buffer[frame_count] = (image, pose_landmarks, Left_Hand_Landmarks, Right_Hnad_Landmarks)
            else:
                # 将缓冲区最小的self.expected_frame显示出来
                if len(self.image_out_buffer) > 0:
                    self.expected_frame = min(self.image_out_buffer.keys())
                    logger.warning("Losing frame!")
                else:
                    time.sleep(1.0 / 60.0)
                    # logger.warning("No frame in queue!")
        else:
            # 如果缓冲区中有图像，显示图像
            self.image_out, pose_landmarks, Left_Hand_Landmarks, Right_Hnad_Landmarks = self.image_out_buffer.pop(self.expected_frame)
            self.expected_frame += 1
        if self.image_out is not None:
            self.model.fps_engine.get_fps()
            fps_averge = self.model.fps_engine.get_average_fps()
            fps_low10 = self.model.fps_engine.get_low10_fps()
            fps_low50 = self.model.fps_engine.get_low50_fps()
            cv2.putText(self.image_out, f'FPS_averge: {fps_averge}, FPS_low10: {fps_low10}, FPS_low50: {fps_low50}',
                        (20, 70), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 3)

            self.model.detector.datainput(pose_landmarks, left_hand_landmark=Left_Hand_Landmarks,
                               right_hand_landmark=Right_Hnad_Landmarks)

            self.model.detector.detect()
            self.model.detector.sit_detect()
            self.model.jump_detector.datainput(pose_landmarks)
            self.model.jump_detector.jump()
        else:
            self.render()

        """
        Draw things on pygame
        """
        empty_color = pygame.Color(0, 0, 0, 0)
        self.model.screen.fill(empty_color)

        # Convert into RGB
        self.image_out = cv2.cvtColor(self.image_out, cv2.COLOR_BGR2RGB)

        # Convert the image into a format pygame can display

        self.image_out = pygame.image.frombuffer(self.image_out.tostring(), self.image_out.shape[1::-1], "RGB")

        # blit the image onto the screen
        self.model.screen.blit(self.image_out, (0, 0))


        # Update the screen
        pygame.display.flip()

        # limit the redraw speed to 30 frames per second
        self.clock.tick(60)

