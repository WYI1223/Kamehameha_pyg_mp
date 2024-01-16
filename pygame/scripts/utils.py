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
        images.append(load_image(path+'/'+img_name))
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

