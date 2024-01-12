from dev.MVC.EventManager import *
import pygame
from pygame.locals import *
import pygame.freetype
import cv2
# from Learning.CourseCode.Program.Components.Button.Button import button
# from Learning.CourseCode.Program.Components.Sprite_Engine.Sprite import sprite_engine


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

        self.model.screen = pygame.display.set_mode((1280, 720), flags, 16, display=screen_no, vsync=1)

        self.clock = pygame.time.Clock()

        # speedup a little bit
        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

    def quit_pygame(self):
        # shut down the pygame graphics
        self.isinitialized = False
        pygame.quit()

    # def init_page(self):
    #     self.model.add_button = button((100, 150), self.model.add_button_path, self.model, 2)
    #     self.model.minus_button = button((100, 250), self.model.minus_button_path, self.model, 2)
    #
    #     self.model.bun_sprite = sprite_engine(self.model.bun_sprite_path, (100, 400), 6, self.model)

    def render(self):
        # Display FPS
        self.model.FPS_class.display_FPS(self.model.img)
        self.model.Mediapipe_Holistic_class.draw_all_landmark_drawing_utils(self.model.img)

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

        # Draw button
        self.model.add_button.draw(self.model.screen)
        self.model.minus_button.draw(self.model.screen)

        # Draw sprite
        self.model.bun_sprite.draw(self.model.bun_sprite_time)

        # Update the screen
        pygame.display.flip()

        # limit the redraw speed to 30 frames per second
        self.clock.tick(60)