import multiprocessing
from CombineVersion.Processes.ImageProcess.OrderProcessor import OrderProcessor
from CombineVersion.Processes.ImageProcess.MediapipeProcessor import mediapipe_subprocess
from CombineVersion.Processes.ImageProcess.Components.CameraIO.CV2_Engine import CameraCapture
import time
from loguru import logger


class ImageProcessor(multiprocessing.Process):
    def __init__(self, image_queue: multiprocessing.Queue, state_machine: multiprocessing.Value):
        super().__init__()
        self.cameraCapture = None
        self.result_images = None
        self.display_image_process = None
        self.input_order = 0

        self.image_queue = image_queue
        self.process_queue = None
        self.running = True
        self.processes = []
        self.statemachine = state_machine

    def get_photos(self):
        while self.running:
            self.process_queue.put((self.input_order, self.cameraCapture.get_frame()))
            self.input_order += 1
            time.sleep(1.0 / 60.0)
            if self.process_queue.full():
                logger.warning("process Queue is full!")
            if self.result_images.full():
                logger.warning("Result Queue is full!")
            if self.image_queue.full():
                logger.warning("image Queue is full!")

            if self.statemachine.value == 0:
                self.running = False
                self.close()
                self.display_image_process.stop()
                # print("ImageProcess is stop")

    def handle_image(self):
        num = 2
        for _ in range(num):
            process = mediapipe_subprocess(self.process_queue, self.result_images)
            process.start()
            self.processes.append(process)

    def close(self):
        for process in self.processes:
            self.process_queue.close()
            process.stop()
            process.join()

    def run(self):
        self.cameraCapture = CameraCapture()
        self.result_images = multiprocessing.Queue(8)
        self.process_queue = multiprocessing.Queue(8)
        # self.display_image_thread = threading.Thread(target=self.display_image,
        #                                              args=(self.result_images, self.image_queue), daemon=True)
        self.display_image_process = OrderProcessor(self.result_images, self.image_queue,self.statemachine)
        self.cameraCapture.start()
        logger.info("CameraCapture is start")

        time.sleep(1)
        self.display_image_process.start()
        self.handle_image()
        self.get_photos()
        print("ImageProcess is stop")
    # 其余的方法保持不变


# 使用示例
if __name__ == '__main__':
    from CombineVersion.Processes.GameProcess.pygame_engine import GameProcess
    image_queue = multiprocessing.Queue(20)

    statemachine = multiprocessing.Value('i', 1)

    multitest_process = ImageProcessor(image_queue, statemachine)
    game_process = GameProcess(image_queue, statemachine)

    game_process.start()
    multitest_process.start()

    game_process.join()
    multitest_process.join()
