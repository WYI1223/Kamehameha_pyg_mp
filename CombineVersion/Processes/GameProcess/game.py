import cv2
import pygame
from CombineVersion.Processes.GameProcess.scripts.utils import load_image,load_images,Animation,load_pimages
from CombineVersion.Processes.GameProcess.scripts.entities import Player,HA,Enemy,Endpoint
from CombineVersion.Processes.GameProcess.scripts.Tilemap import Tilemap
from CombineVersion.Processes.GameProcess.scripts.clouds import Clouds
from CombineVersion.Processes.GameProcess.ui.ScoreBoard import ScoreBoard
offset = 0


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((1920,1080))

        self.display = pygame.Surface(((1920-680)//2, 1080//2))

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
        self.movement = [False,True,False,False]

        self.clouds = Clouds(self.assets['clouds'],count=16)

        self.player = Player(self, (50, 50),(8, 15))

        self.endpoint = None


        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load('mapWithEndpoint.json')
        self.scroll = 0

        self.Jump = False
        self.isAttacking = False

        self.pause = True
        self.gameover = False

        self.scoreboard = ScoreBoard()

        self.enemies = []
        matching_spawners = self.tilemap.extract([('spawners', 0),('spawners', 1)])
        for spawner in matching_spawners:
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))

        matching_endpoint = self.tilemap.extract([('endpoint', 0)])
        for endpoint in matching_endpoint:
            self.endpoint = Endpoint(self, endpoint['pos'], (8, 15))
            self.endpoint.update()


    def run(self,image_queue, state_machine):
        self.initialize()
        self.image_queue = image_queue
        self.statemachine = state_machine

        while True:

            self.renderImage()

            if self.gameover:
                if self.scoreboard.run(self.statemachine) == 0:
                    self.initialize()
                continue


            if self.player.pos[1]>540:
                self.gameover = True

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
                if self.STATE1 ==4:
                    if self.HA == None:
                        self.HA = HA(self,(self.player.pos[0], self.player.pos[1]), (8, 15))

                    self.STATE1 = self.HA.update(self.tilemap,3)
                    self.HA.render(self.display,render_scroll,13)
                    if self.STATE1 == 1:
                        self.HA = None
            else:
                if self.player.update(self.tilemap, ((self.movement[1] - self.movement[0])*0.5, 0), self.STATE1) == 0:
                    continue
            if self.endpoint is not None:
                if self.endpoint.update() == -1:
                    return -1
                self.endpoint.render(self.display, offset=render_scroll)
            self.player.render(self.display, offset=render_scroll)
            for enemy in self.enemies.copy():
                enemy.update(self.tilemap, (0,0))

                enemy.render(self.display,offset=render_scroll)
                if enemy.dead == True:
                    if enemy.dead_counter > 10:
                        self.score_kill += 100
                        self.enemies.remove(enemy)



            """
            状态判断
            """
            state = self.statemachine.value
            if state == 1:
                self.Jump = False

            if state == 1 and self.STATE1 != 1:
                self.isAttacking = False
                self.STATE1 = 1
            if state == 2:
                self.isAttacking = True
                if self.STATE1 == 1:
                    self.STATE1 = 2
                    print("State1 change to 1")
            if state == 3:
                if self.STATE1 == 2:
                    self.STATE1 = 3
                    print("State1 change to 2")
            if state == 4:
                if self.STATE1 == 3:
                    self.STATE1 = 4
                    print("Action done")
            if state == 5:
                # if not self.Jump:
                self.player.velocity[1] = -3
                # self.Jump = True
                # self.movement[3] = True

            if state == 8:
                self.pause = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # sys.exit()
                    return -1



                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        self.player.velocity[1] = -3
                        # self.movement[3] = True
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
            text_rect.topleft = (50,50)

            # 将文本绘制到屏幕上

            self.display.blit(text_surface, text_rect)


            self.screen.blit(pygame.transform.scale(self.display, (1920-680, 1080)), (0, 0))



            # if self.pauseM() == -1:
            #     return -1
            self.renderText()
            pygame.display.update()

            self.clock.tick(60)
    def pauseM(self):
        while self.pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -1
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.pause = False
            self.renderImage()
            if self.statemachine.value == 6:
                self.pause = False

            text_pause_font = pygame.font.Font(None, 200)
            text_pause_surface = text_pause_font.render("Game Pause", True, (255, 255, 255))  # 文本颜色为白色
            # 获取文本的矩形区域
            text_puase_rect = text_pause_surface.get_rect()
            text_puase_rect.center = (self.screen.get_width() // 2, self.screen.get_height() // 2)
            # 将文本绘制到屏幕上
            self.screen.blit(text_pause_surface, text_puase_rect)

            pygame.display.update()

    def renderText(self):
        text = None
        state = self.statemachine.value
        if state == 2:
            text = "Attack1"
        elif state == 3:
            text = "Attack2"
        elif state == 4:
            text = "Attack3"
        elif state == 5:
            text = "Jump"
        elif state == 6:
            text = "Sit and Game Start"
        else:
            return
        text_action_font = pygame.font.Font(None, 100)
        text_action_surface = text_action_font.render(text, True, (255, 255, 255))
        text_action_rect = text_action_surface.get_rect()
        text_action_rect.midbottom = self.screen.get_rect().midbottom
        self.screen.blit(text_action_surface, text_action_rect)
    def renderImage(self):

        if not self.image_queue.empty():
            image = self.image_queue.get()
            image_out = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_out = pygame.image.frombuffer(image_out.tostring(), image_out.shape[1::-1], "RGB")
            self.screen.blit(image_out, (self.screen.get_width() - image_out.get_width(), 0))

if __name__ == '__main__':
    Game().run()