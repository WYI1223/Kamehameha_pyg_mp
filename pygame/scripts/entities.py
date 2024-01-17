import random

import pygame
OFFSET = 1

class PhysicsEntity:
    def __init__(self,game,e_type,pos,size):
        self.animation = None
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0,0]
        self.collisions={'up':False,'down':False}
        self.img = load_image('entities/HA/HA1/ha0.png')
        self.action = ''
        self.anim_offset = (-3,-3)
        self.flip = False

    def rect(self):
        return pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()
        pass
    def update(self,tilemap, movement):
        self.collisions = {'up': False, 'down': False}
        frame_movement = (movement[0]+self.velocity[0],movement[1]+self.velocity[1])

        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                self.pos[0] = entity_rect.x
                print("player:", entity_rect.x)


        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y


        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] =0

        if self.animation is not None:
            self.animation.update()


    def render(self, surf,offset):
        surf.blit(pygame.transform.flip(self.animation.img(),self.flip,False),((self.pos[0] - offset),self.pos[1]))


class Player(PhysicsEntity):
    def __init__(self,game,pos,size):
        super().__init__(game,'player',pos,size)
        self.set_action('idle')
        self.air_time = 0


    def update(self,tilemap, movement,state):

        super().update(tilemap,movement)

        for enemy in self.game.enemies:
            # 判定是否与玩家相撞（修改self.game.player.rect()即可换成是否与气功波相撞）
            if self.rect().colliderect(enemy.rect()):
                self.game.initialize()
                return 0


        self.air_time += 1
        if self.collisions['down']:
            self.air_time =0

        if self.air_time>4:
            self.set_action('jump')
        elif movement[0] != 0:
            self.set_action('run')
        elif state == 2 :
            self.set_action('attack1')
        elif state == 3:
            self.set_action('attack2')
        elif state == 4 :
            self.set_action('attack3')
        else:
            self.set_action('idle')

        try:
            if state > 0:
                # print("execute action:",state)
                # if state == 4:
                    # state = 1
                return state
        except Exception as e:
            print(e)
            return 0

class HA(PhysicsEntity):
    def __init__(self,game,pos,size):
        super().__init__(game,'HA',pos,size)
        self.action = 'HA2'
        self.animation = self.game.assets[self.type + '/' + self.action].copy()


        # self.set_action("HA1")
        # print(self.animation)
        self.counter = 0
        self.counter2 = 0



    def update(self,tilemap,frame_movement):
        self.pos[0] += frame_movement
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement > 0:
                    entity_rect.right = rect.left
                if frame_movement < 0:
                    entity_rect.left = rect.right
                # for enemy in self.game.enemies:
                #     if entity_rect.right == enemy.rect().left:
                #         entity_rect.right = enemy.rect().left
                self.pos[0] = entity_rect.x
                self.set_action("HA2")
                # print("HA:", entity_rect.x)
                self.counter += 1

        if entity_rect.right > self.game.player.pos[0] + 100 :
            self.pos[0] = entity_rect.x
            self.set_action("HA2")
            # print("HA:", entity_rect.x)
            self.counter += 1
        self.animation.update()
        if self.counter > 5:
            self.counter = 0
            self.game.isAttacking = False
            return 1
        return 4
    def render(self, surf, offsetx, offsety):
        if self.counter2<100:
            print(self.counter2)
            for i in range(self.counter2):
                surf.blit(self.img,((self.pos[0]-offsetx-i), self.pos[1]))
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False),
                  ((self.pos[0] - offsetx), self.pos[1]-offsety))

        self.counter2 = self.counter2+3





class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size)

        self.walking = 0
        self.dead = False
        self.dead_counter = 0


    def update(self, tilemap, movement=(0, 0)):
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)

        super().update(tilemap, movement=movement)
        if self.dead:
            self.set_action('run')
            self.dead_counter += 1
            return

        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        if self.game.isAttacking:
                if self.game.HA != None:
                    # 判定是否与玩家相撞（修改self.game.player.rect()即可换成是否与气功波相撞）
                    if self.rect().colliderect(self.game.HA.rect()):
                        self.dead = True
                else:
                    self.dead = False

class Endpoint(PhysicsEntity):
    def __init__(self,game,pos,size):
        super().__init__(game,'endpoint',pos,size)
        self.action = ''
        self.set_action('1')

    def end(self):
        if self.game.player.pos[0] > self.pos[0]:
            return True

    def update(self):
        if self.end():
            return -1
        super().update(self.game.tilemap,movement=(0,0))

import pygame
import os

BASE_IMG_PATH = 'data/images/'
new = (12,15)
def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH+path).convert_alpha()
    # img.set_colorkey((0,0,0))
    img.set_colorkey((27,147,59))
    # img = pygame.transform.scale(img,new)
    return img

def load_images(path):
    images = []
    for img_name in os.listdir(BASE_IMG_PATH +path):
        img = load_image(path+'/'+img_name)
        # img.set_colorkey((27,147,59))
        images.append(img)
    return images
def load_pimages(path):
    images = []
    for img_name in os.listdir(BASE_IMG_PATH +path):
        img = load_image(path+'/'+img_name)
        img.set_colorkey((0,0,0))
        images.append(img)
    return images



class Animation:
    def __init__(self,images, img_dur=5,loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0

    def copy(self):
        # print()
        return Animation(self.images,self.img_duration,self.loop)

    def update(self):
        if self.loop:
            self.frame = (self.frame + 1)%(self.img_duration*len(self.images))
        else:
            self.frame = min(self.frame+1, self.img_duration*len(self.images) - 1)
            if self.frame >= self.img_duration*len(self.images)-1:
                self.done =True
    def img(self):
        return self.images[int(self.frame / self.img_duration)]