import sys
import pygame
from scripts.utils import load_image,load_images,Animation
from scripts.entities import PhysicsEntity
from scripts.Tilemap import Tilemap
class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Dragon ball')
        self.screen = pygame.display.set_mode((640,480))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.movement = [False,False,False,False]

        self.assets = {
            'decor' : load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'player/idle' : Animation(load_images('entities/player/idle'),img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump'), img_dur=4),
            'player/slide': Animation(load_images('entities/player/slide'), img_dur=4),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide'), img_dur=4)

        }
        print(self.assets)

        self.player = PhysicsEntity(self, 'player',(50, 50),(8, 15))

        self.tilemap = Tilemap(self, tile_size=16)

    def run(self):
        while True:
            self.display.fill((14,219,248))
            self.tilemap.render(self.display)

            self.player.render(self.display)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.movement[3] = True
                    if event.key == pygame.K_DOWN:
                        self.movement[2] = True

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.movement[3] = False
                    if event.key == pygame.K_DOWN:
                        self.movement[2] = False


            print((self.movement[2] - self.movement[3])*16)

            self.player.update(self.tilemap,(self.movement[1] - self.movement[0], (self.movement[2] - self.movement[3])*16))

            self.screen.blit(pygame.transform.scale(self.display, (640, 480)), (0, 0))

            pygame.display.update()
            self.clock.tick(60)

Game().run()