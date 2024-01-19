import random

class Cloud:
    def __init__(self,pos,img,speed,depth):
        self.pos = list(pos)
        self.img = img
        self.speed = speed
        self.depth = depth

    def update(self):
        self.pos[0] += self.speed

    def render(self, surf, offset):
        render_pos = (self.pos[0]-offset*self.depth, self.pos[1]*self.depth)
        surf.blit(self.img,(render_pos[0]%(surf.get_width()+self.img.get_width())-self.img.get_width(),render_pos[1]%(surf.get_height()+self.img.get_height())-self.img.get_height()))



class Clouds:
    def __init__(self, cloud_image,count=40):
        self.clouds = []

        for i in  range(count):
            self.clouds.append(Cloud((random.random()*9999, random.random()*9999), (random.choice(cloud_image)), (random.random()*0.05+0.05), (random.random()*0.06+0.02)))

        self.clouds.sort(key=lambda x: x.depth)

    def update(self):
        for cloud in self.clouds:
            cloud.update()

    def render(self, surf, offset):
        for cloud in self.clouds:
            cloud.render(surf,offset=offset)