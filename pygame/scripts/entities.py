import pygame


class PhysicsEntity:
    def __init__(self,game,e_type,pos,size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0,0]

        self.action = ''
        self.anim_offset = (-3,-3)
        self.flip = False
        self.set_action('idle')

    def rect(self):
        return pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.assets[self.e_type + '/' + self.action].copy()
        pass
    def update(self,tilemap, movement):
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
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                self.pos[1] = entity_rect.y
                self.velocity[1] = min(5, 0)


        self.velocity[1] = min(5, self.velocity[1] + 0.1)


    def render(self, surf):
        surf.blit(pygame.transform)
        surf.blit(self.game.assets['player'], self.pos)