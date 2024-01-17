import sys
import pygame
from scripts.utils import load_image,load_images,Animation,load_pimages
from scripts.entities import Player,HA,Enemy,Endpoint
from scripts.Tilemap import Tilemap
from scripts.clouds import Clouds
offset = 0


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((1920,1080))

        self.display = pygame.Surface((1920, 1080))

        self.clock = pygame.time.Clock()

        self.assets = {
            'decor' : load_pimages('tiles/decor'),
            'grass': load_pimages('tiles/grass'),
            'large_decor': load_pimages('tiles/large_decor'),
            'stone': load_pimages('tiles/stone'),
            'endpoint/1': Animation(load_pimages('tiles/endpoint')),
            'player': pygame.transform.scale(load_image('entities/player_stand.png'),(17,17)),
            'background' : pygame.transform.scale (load_image('background.png'),(1920,1080)),
            'clouds':load_pimages('clouds'),
            'pixels': load_images('tiles/pixel'),
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

    def initialize(self):
        self.score_kill = 0
        self.STATE1 = 1

        self.HA = None
        self.font = pygame.font.Font(None, 36)
        self.movement = [False,False,False,False]

        self.clouds = Clouds(self.assets['clouds'],count=16)

        self.player = Player(self, (50, 50),(8, 15))

        self.endpoint = None


        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load('map2.json')
        self.scroll = 0

        self.isAttacking = False

        self.enemies = []
        matching_spawners = self.tilemap.extract([('spawners', 0),('spawners', 1)])
        for spawner in matching_spawners:
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))

        matching_endpoint = self.tilemap.extract([('endpoint', 0)])
        print(matching_endpoint)
        for endpoint in matching_endpoint:
            print("13123123")
            self.endpoint = Endpoint(self, endpoint['pos'], (8, 15))
            self.endpoint.update()


    def run(self):
        self.initialize()
        while True:
            if  self.player.pos[1]>540:
                self.initialize()

            self.display.blit(self.assets['background'],(0,0))




            self.scroll += (self.player.rect().centerx - self.display.get_width()/5 - self.scroll)/2
            render_scroll = (int(self.scroll))

            self.clouds.update()

            self.clouds.render(self.display,offset=render_scroll)


            self.tilemap.render(self.display,offset=render_scroll)




            if self.STATE1 != 1:
                self.STATE1 = self.player.update(self.tilemap,(0,0), self.STATE1)
                # 死亡回城
                if self.STATE1 == 0:
                    continue
                # print("123123123")
                if self.STATE1 ==4:
                    if self.HA == None:
                        self.HA = HA(self,(self.player.pos[0], self.player.pos[1]), (8, 15))

                    self.STATE1 = self.HA.update(self.tilemap,3)
                    self.HA.render(self.display,render_scroll,13)
                    if self.STATE1 == 1:
                        self.HA = None
            else:
                if self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0), self.STATE1) == 0:
                    continue

            self.player.render(self.display,offset=render_scroll)
            if self.endpoint is not None:
                if self.endpoint.update() == -1:
                    return -1
                self.endpoint.render(self.display,offset=render_scroll)
            for enemy in self.enemies.copy():
                enemy.update(self.tilemap,(0,0))

                enemy.render(self.display,offset=render_scroll)
                if enemy.dead == True:
                    if enemy.dead_counter > 10:
                        self.score_kill += 100
                        self.enemies.remove(enemy)


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    # sys.exit()
                    return -1



                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        self.player.velocity[1] = -3
                    if event.key == pygame.K_DOWN:
                        self.movement[3] = True
                    if event.key == pygame.K_j:
                        self.isAttacking = True
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

                    if event.key == pygame.K_b:
                        self.initialize()
                        continue


                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                    if event.key == pygame.K_UP:
                        self.movement[2] = False
                    if event.key == pygame.K_DOWN:
                        self.movement[3] = False
                        pass

            # 渲染文本
            text_surface = self.font.render("Score:{}".format(self.score_kill), True, (255, 255, 255))  # 文本颜色为白色

            # 获取文本的矩形区域
            text_rect = text_surface.get_rect()
            text_rect.topleft = (100,50)

            # 将文本绘制到屏幕上

            self.display.blit(text_surface, text_rect)


            self.screen.blit(pygame.transform.scale(self.display, (1960, 1080)), (0, 0))

            pygame.display.update()
            self.clock.tick(60)

if __name__ == '__main__':
    Game().run()