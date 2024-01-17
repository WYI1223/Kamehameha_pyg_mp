import multiprocessing
import pygame
from CombineVersion.Processes.GameProcess.game import Game
from CombineVersion.Processes.GameProcess.ui import ui


class Game_Engine(multiprocessing.Process):

    def __init__(self, image_queue: multiprocessing.Queue, statemachine: multiprocessing.Value):
        super().__init__()

        self.image_queue = image_queue
        self.statemachine = statemachine


        self.state_ui = 0

    def run(self):
        pygame.init()
        pygame.display.set_caption('Dragon ball')

        while True:
            if self.state_ui == -1:
                with self.statemachine.get_lock():
                    self.statemachine.value = 0
                break

            if self.state_ui == 0:
                self.state_ui = ui.Mt().main()

            if self.state_ui == 1:
                self.state_ui = Game().run(self.image_queue)
        print("Game_Engine stop")

    def stop(self):

        pass


if __name__ == '__main__':
    Game_Engine(multiprocessing.Queue, multiprocessing.Value('i', 1)).run()