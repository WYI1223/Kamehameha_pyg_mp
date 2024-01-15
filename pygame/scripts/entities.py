import pygame


class PhysicsEntity:
    def __init__(self,game,e_type,pos,size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0,0]
        self.jumping = False
        self.on_ground = False

        # self.action = ''
        # self.anim_offset = (-3,-3)
        # self.flip = False
        # self.set_action('idle')

    def rect(self):
        return pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])

    # def set_action(self, action):
    #     if action != self.action:
    #         self.action = action
    #         self.animation = self.assets[self.e_type + '/' + self.action].copy()
    #     pass
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

        on_ground_before = self.on_ground  # 记录之前的地面状态

        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.on_ground = True
                    self.jumping = False  # 重置跳跃状态
                    self.velocity[1] = 0  # 重置垂直速度
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                self.pos[1] = entity_rect.y
                self.velocity[1] = min(5, 0)

        # 更新垂直速度
        if not on_ground_before and self.on_ground:
            self.velocity[1] = 0  # 触碰地面时重置垂直速度

        # 处理跳跃
        if self.on_ground and self.jumping:
            self.pos[1] -= 25  # 调整为合适的跳跃高度
            self.on_ground = False  # 触发跳跃时离开地面
            self.jumping = False


        self.velocity[1] = min(5, self.velocity[1] + 0.1)


    def render(self, surf):
        # surf.blit(pygame.transform)
        surf.blit(self.game.assets['player'], self.pos)