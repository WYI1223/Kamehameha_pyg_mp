import cv2
import pygame
import multiprocessing
from loguru import logger
import time

def run_game(image_queue):
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    pygame.display.set_caption("Pygame Display Image")

    # 创建 Clock 对象
    clock = pygame.time.Clock()

    running = True
    while running:
        # 限制帧率
        clock.tick(60)  # 例如，每秒60帧

        # 检查队列是否有新图像
        if not image_queue.empty():

            image = image_queue.get()

            # Convert into RGB
            image_out = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Convert the image into a format pygame can display

            image_out = pygame.image.frombuffer(image_out.tostring(), image_out.shape[1::-1], "RGB")

            # 显示图像
            screen.blit(image_out, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    # 创建进程间通信队列
    image_queue = multiprocessing.Queue()

    # 创建并启动子进程
    game_process = multiprocessing.Process(target=run_game, args=(image_queue,))
    game_process.start()

    # 主进程中可以将图像放入队列
    # 例如：image_queue.put(your_pygame_surface)

    # 等待子进程结束
    game_process.join()
