import multiprocessing
import pygame
from CombineVersion.Processes.GameProcess.game import Game
from CombineVersion.Processes.GameProcess.ui import StartMenu


class Game_Engine(multiprocessing.Process):

    def __init__(self, image_queue: multiprocessing.Queue, statemachine: multiprocessing.Value, processes_pid: multiprocessing.Queue):
        super().__init__()

        self.image_queue = image_queue
        self.statemachine = statemachine
        self.processes_pid = processes_pid

        self.state_ui = 0
        self.player_name = ''

    def run(self):
        self.processes_pid.put(("Game_Engine", self.pid))
        pygame.init()
        pygame.display.set_caption('Dragon ball')
        # 初始化音频
        pygame.mixer.init()

        while True:
            if self.state_ui == -1:
                with self.statemachine.get_lock():
                    self.statemachine.value = 0
                    print("Game_Engine_Statemachine:", self.statemachine.value)
                pygame.mixer.music.stop()
                pygame.quit()
                break

            if self.state_ui == 0:
                # 停止当前音乐
                pygame.mixer.music.stop()

                # 加载并播放state.mp3
                pygame.mixer.music.load('CombineVersion/Data/GameData/BGM/start.mp3')
                pygame.mixer.music.play(-1)

                self.state_ui, self.player_name = StartMenu.Mt().main()

            if self.state_ui == 1:
                # 停止当前音乐
                pygame.mixer.music.stop()

                # 加载并播放gaming.mp3
                pygame.mixer.music.load('CombineVersion/Data/GameData/BGM/gaming.mp3')
                pygame.mixer.music.play(-1)
                if self.player_name == '':
                    self.player_name = 'Player'
                self.state_ui = Game().run(self.image_queue, self.statemachine,self.player_name)

        print("Game_Engine stop")

    def stop(self):

        pass


if __name__ == '__main__':
    Game_Engine(multiprocessing.Queue, multiprocessing.Value('i', 1)).run()