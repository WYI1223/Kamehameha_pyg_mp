import numpy as np
from multiprocessing import Process, Queue
import pygame
import time

def worker(q):
    pygame.init()
    screen = pygame.display.set_mode((640, 480))

    while True:
        image_np = q.get()
        image = pygame.surfarray.make_surface(image_np)
        screen.blit(image, (0, 0))
        pygame.display.flip()

def main():
    q = Queue()

    p = Process(target=worker, args=(q,))
    p.start()

    while True:
        image = pygame.Surface((640, 480))
        image_np = pygame.surfarray.array3d(image)
        q.put(image_np)

        time.sleep(1)

if __name__ == "__main__":
    main()