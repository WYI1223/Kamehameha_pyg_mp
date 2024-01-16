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

        if state > 0:
            # print("execute action:",state)
            # if state == 4:
                # state = 1
            return state


class HA(PhysicsEntity):
    def __init__(self,game,pos,size):
        super().__init__(game,'HA',pos,size)
        self.action = ''
        self.set_action("HA1")
        # print(self.animation)
        self.counter = 0



    def update(self,tilemap,frame_movement):

        self.pos[0] += frame_movement
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement > 0:
                    entity_rect.right = rect.left
                if frame_movement < 0:
                    entity_rect.left = rect.right
                self.pos[0] = entity_rect.x
                self.set_action("HA2")
                print("HA:", entity_rect.x)
                self.counter += 1
                
        if entity_rect.right > self.game.player.pos[0] +100 :
            self.pos[0] = entity_rect.x
            self.set_action("HA2")
            print("HA:", entity_rect.x)
            self.counter += 1
        self.animation.update()
        if self.counter == 5:
            self.counter = 0
            return 1
        return 4
    def render(self, surf, offsetx, offsety):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False),
                  ((self.pos[0] - offsetx), self.pos[1]-offsety))
