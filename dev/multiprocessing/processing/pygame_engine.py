import cv2
import pygame
from pygame.locals import *
import pygame.freetype
import multiprocessing
from loguru import logger
import time

# 继承 multiprocessing.Process 类来创建一个子进程类
class GameProcess(multiprocessing.Process):
    def __init__(self, image_queue: multiprocessing.Queue):
        # 初始化父类 Process
        super(GameProcess, self).__init__()
        # 将图像队列存储为类属性
        self.image_queue = image_queue

    # run 方法包含原来 run_game 函数的主要逻辑
    def run(self):
        # 初始化 pygame 模块
        pygame.init()
        pygame.font.init()
        pygame.freetype.init()

        # 设置窗口标题
        pygame.display.set_caption("Pygame Display Image")

        # 设置窗口模式
        flags = DOUBLEBUF

        # 选择显示屏幕
        if(pygame.display.get_num_displays() >= 2):
            screen_no = 1
        else:
            screen_no = 0

        # 设置显示窗口的大小和属性
        screen = pygame.display.set_mode((1920, 1080), flags, 16, display=screen_no, vsync=1)

        # 创建一个时钟对象来控制帧率
        clock = pygame.time.Clock()

        # 允许的事件类型
        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

        # 游戏主循环标志
        running = True
        while running:
            # 限制帧率为每秒60帧
            clock.tick(60)

            # 检查图像队列是否有新图像
            if not self.image_queue.empty():
                image = self.image_queue.get()
                image_out = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image_out = pygame.image.frombuffer(image_out.tostring(), image_out.shape[1::-1], "RGB")
                screen.blit(image_out, (0, 0))

            # 处理 Pygame 事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # 更新显示
            pygame.display.flip()

        # 退出 Pygame
        pygame.quit()

if __name__ == '__main__':
    # 创建图像队列，用于进程间通信
    image_queue = multiprocessing.Queue()
    # 创建并启动子进程
    game_process = GameProcess(image_queue)
    game_process.start()
    # 等待子进程结束
    game_process.join()
