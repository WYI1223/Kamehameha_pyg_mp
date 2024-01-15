import sys
import pygame
from scripts.utils import load_images
from scripts.Tilemap import Tilemap
offset = 0
class Editor:
    def __init__(self):
        self.right_clicking = False
        pygame.init()

        pygame.display.set_caption('editor')
        self.screen = pygame.display.set_mode((640,480))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.movement = [False,False,False,False]

        self.assets = {
            'decor' : load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),

        }
        print(self.assets)

        self.tilemap = Tilemap(self, tile_size=16)
        self.scroll = 0

        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0
        self.click = False
        self.shift = False
    def run(self):
        while True:
            self.display.fill((0,0,0))

            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant]
            current_tile_img.set_alpha(100)

            self.display.blit(current_tile_img,(5,5))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.click = True
                    if event.button == 3:
                        self.right_clicking = True
                    if self.shift:
                        if event.button == 4:
                            self.tile_variant = (self.tile_group -1)%len(self.assets[self.tile_list[self.tile_group]])
                        if event.button == 5:
                            self.tile_variant = (self.tile_group +1)%len(self.assets[self.tile_list[self.tile_group]])
                    else:
                        if event.button == 4:
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                        if event.button == 5:
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        self.movement[2] = True
                    if event.key == pygame.K_DOWN:
                        self.movement[3] = True
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                    if event.key == pygame.K_UP:
                        self.movement[3] = False
                    if event.key == pygame.K_DOWN:
                        self.movement[2] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False


            self.screen.blit(pygame.transform.scale(self.display, (640, 480)), (0, 0))

            pygame.display.update()
            self.clock.tick(60)

Editor().run()