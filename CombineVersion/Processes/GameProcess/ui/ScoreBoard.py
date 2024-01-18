import time

import pygame.image


class ScoreBoard:


    def __init__(self):
        self.scores = {}
        pygame.init()
        pygame.display.set_caption('Dragon ball')
        self.windows = pygame.display.set_mode((1920, 1080))
        self.image_scoreBoard = pygame.image.load('CombineVersion/Data/GameData/images/ScoreBoard/ScoreBoard.png').convert_alpha()
        self.image_scoreBoard_restart = pygame.image.load('CombineVersion/Data/GameData/images/ScoreBoard/ScoreMenu_reStart.png').convert_alpha()
        rect_x, rect_y = 665, 794  # Top-left corner of the rectangle
        rect_width, rect_height = 573, 131  # Size of the rectangle
        self.restart_buttom = pygame.Rect(rect_x, rect_y, rect_width, rect_height)

        self.scoreBoard_rect = self.image_scoreBoard.get_rect()
        self.scoreBoard_restart_rect = self.image_scoreBoard_restart.get_rect(topleft=(0, 0))
        self.scoreBoard_rect.center = pygame.display.get_surface().get_rect().center

        self.font = pygame.font.Font(None, 48)


        self.hover = False
        self.time = 0

        score = {}

    def test_score(self):
        self.scores = {
            "Player 1": 100,
            "Player 2": 200,
            "Player 3": 300,
            "Player 4": 400,
            "Player 5": 500
        }


    def add_score(self, name, score):
        self.scores[name] = score

        pass

    def get_score(self, num):


        pass

    def scoreBoardRender(self, statemachine):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return -1
        # Get the current mouse position
        x, y = pygame.mouse.get_pos()

        # Check if the mouse is inside the rectangle
        if self.restart_buttom.collidepoint(x, y):
            self.hover = True
            self.windows.blit(self.image_scoreBoard_restart, self.scoreBoard_rect)
        else:
            self.hover = False
            self.windows.blit(self.image_scoreBoard, self.scoreBoard_rect)

        scores = self.scores

        # for i in range(5):
        #     scores = self.get_score(i)


        for i, (player, score) in enumerate(scores.items()):
            score_text = "{:12}:{:15d}".format(player, score)
            score_surface = self.font.render(score_text, True, (255, 255, 255))  # White color
            score_x = self.windows.get_width() / 2
            score_y = self.windows.get_height() / 2 - 40 * (len(scores) / 2) + i * 60
            score_rect = score_surface.get_rect(center=(score_x, score_y))
            self.windows.blit(score_surface, score_rect)


        if statemachine.value == 6 or self.hover:
            if self.time == 0:
                self.time = time.time()

            text_countdown = "Count Down: {}".format(3 - int(time.time() - self.time))
            countdown_surface = self.font.render(text_countdown, True, (255, 255, 255))  # White color
            countdown_rect = countdown_surface.get_rect()
            countdown_rect.midtop = self.restart_buttom.midbottom

            self.windows.blit(countdown_surface, countdown_rect)

            if time.time() - self.time > 3:
                self.time = 0
                return 0
        else:
            self.time = 0
        pygame.display.update()

    def run(self, statemachine,name,score):
        self.add_score(name, score)
        return self.scoreBoardRender(statemachine)
        pass

