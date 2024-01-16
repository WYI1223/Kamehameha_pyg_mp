import sys
import pygame
from scripts.utils import load_image,load_images,Animation,load_pimages
from scripts.entities import Player,HA,Enemy
from scripts.Tilemap import Tilemap
from scripts.clouds import Clouds
offset = 0


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Dragon ball')
        self.screen = pygame.display.set_mode((640,480))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()
        self.STATE1 = 1
        self.STATE2 = False
        self.HA = None

        self.movement = [False,True,False,False]

        self.assets = {
            'decor' : load_pimages('tiles/decor'),
            'grass': load_pimages('tiles/grass'),
            'large_decor': load_pimages('tiles/large_decor'),
            'stone': load_pimages('tiles/stone'),
            'player': pygame.transform.scale(load_image('entities/player_stand.png'),(17,17)),
            'background' : pygame.transform.scale (load_image('background.png'),(1920,1080)),
            'clouds':load_pimages('clouds'),
            'HA/HA1' : Animation([pygame.transform.scale(load_image('entities/HA/HA1/ha0.png'),(34,34))]),
            'HA/HA2': Animation([pygame.transform.scale(load_image('entities/HA/HA2/head.png'),(34,34))]),
            'player/idle' : Animation(load_images('entities/player/idle2'),img_dur=6),
            'player/attack1': Animation(load_images('entities/player/attack1'), img_dur=6),
            'player/attack2': Animation(load_images('entities/player/attack2'), img_dur=6),
            'player/attack3': Animation(load_images('entities/player/attack3'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run2'),img_dur=5),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/particle': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),

        }
        print(self.assets)

        self.clouds = Clouds(self.assets['clouds'],count=16)

        self.player = Player(self, (50, 50),(8, 15))

        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load('map.json')
        self.scroll = 0

        self.enemies = []
        matching_spawners = self.tilemap.extract([('spawners', 0),('spawners', 1)])

        for spawner in matching_spawners:
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))


    def run(self):
        while True:
            self.display.blit(self.assets['background'],(0,0))
            self.scroll += (self.player.rect().centerx - self.display.get_width()/5 - self.scroll)/2
            render_scroll = (int(self.scroll))

            self.clouds.update()

            self.clouds.render(self.display,offset=render_scroll)


            self.tilemap.render(self.display,offset=render_scroll)

            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap,(0,0))
                enemy.render(self.display,offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)

            if self.STATE1 != 1:
                self.STATE1 = self.player.update(self.tilemap,(0,0), self.STATE1)
                # print("123123123")
                if self.STATE1 ==4:
                    if self.HA == None:
                        self.HA = HA(self,(self.player.pos[0], self.player.pos[1]), (8, 15))

                    self.STATE1 = self.HA.update(self.tilemap,3)
                    self.HA.render(self.display,render_scroll,13)
                    if self.STATE1 == 1:
                        self.HA = None
            else:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0), self.STATE1)
            self.player.render(self.display,offset=render_scroll)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        self.player.velocity[1] = -3
                    if event.key == pygame.K_DOWN:
                        self.movement[2] = True
                    if event.key == pygame.K_j:
                        if self.STATE1 == 1:
                            self.STATE1 = 2
                            print("State1 change to 1")
                    if event.key == pygame.K_k:
                        if self.STATE1 == 2:
                            self.STATE1 = 3
                            print("State1 change to 2")
                    if event.key == pygame.K_l:
                        if self.STATE1 == 3:
                            self.STATE1 = 4
                            print("Action done")
                        # self.STATE2 = True


                if event.type == pygame.KEYUP:
                    # if event.key == pygame.K_LEFT:
                    #     self.movement[0] = False
                    # if event.key == pygame.K_RIGHT:
                    #     self.movement[1] = False
                    if event.key == pygame.K_UP:
                        self.movement[3] = False
                    if event.key == pygame.K_DOWN:
                        self.movement[2] = False



            # print((self.movement[2] - self.movement[3])*16)
            # if self.STATE1 == 1:
            #     self.player.update(self.tilemap,((self.movement[1] - self.movement[0])/9, (self.movement[2] - self.movement[3])*16),0)
            # elif self.STATE1 != 1:
            #     self.player.update(self.tilemap, (0,0), 0)


            self.screen.blit(pygame.transform.scale(self.display, (640, 480)), (0, 0))

            pygame.display.update()
            self.clock.tick(60)

if __name__ == '__main__':
    Game().run()