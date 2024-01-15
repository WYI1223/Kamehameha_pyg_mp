import pygame


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
        self.set_action('idle')

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
        # surf.blit(pygame.transform.flip(self.animation.img()), ((self.pos[0] - offset),self.pos[1]))



class Player(PhysicsEntity):
    def __init__(self,game,pos,size):
        super().__init__(game,'player',pos,size)
        self.air_time = 0

    def update(self,tilemap, movement):

        super().update(tilemap,movement)

        self.air_time += 1
        if self.collisions['down']:
            self.air_time =0

        if self.air_time>4:
            self.set_action('jump')
        elif movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')