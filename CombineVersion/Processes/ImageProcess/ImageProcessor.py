import multiprocessing
import queue

from CombineVersion.Processes.ImageProcess.OrderProcessor import OrderProcessor
from CombineVersion.Processes.ImageProcess.MediapipeProcessor import mediapipe_subprocess
from CombineVersion.Processes.ImageProcess.Components.CameraIO.CV2_Engine import CameraCapture
import time
from loguru import logger


class ImageProcessor(multiprocessing.Process):
    def __init__(self, image_queue: multiprocessing.Queue, state_machine: multiprocessing.Value, processes_pid: multiprocessing.Queue):
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
        self.processes_pid = processes_pid

        self.isRunning_subprocess = None
        self.isRunning_OrderProcessor = None

    def get_photos(self):
        while self.running:
            try:
                self.process_queue.put((self.input_order, self.cameraCapture.get_frame()))
            except queue.Full:
                time.sleep(1.0 / 60.0)
                continue
            self.input_order += 1
            time.sleep(1.0 / 60.0)
            if self.process_queue.full():
                logger.warning("process Queue is full!")
            if self.result_images.full():
                logger.warning("Result Queue is full!")
            if self.image_queue.full():
                logger.warning("image Queue is full!")

            if self.statemachine.value == 0:
                # print(self.statemachine.value)
                logger.debug("ImageProcess stoping 1")
                self.cameraCapture.stop()
                logger.debug("ImageProcess stoping 2")
                self.close()
                logger.debug("ImageProcess stoping 3")
                self.isRunning_OrderProcessor.clear()
                self.display_image_process.stop()
                logger.debug("ImageProcess stoping 4")
                self.display_image_process.join()
                logger.debug("ImageProcess stoping 5")
                self.running = False
                logger.debug("ImageProcess stoping 6")



    def handle_image(self):
        num = 2
        for _ in range(num):
            process = mediapipe_subprocess(self.process_queue, self.result_images, self.isRunning_subprocess)
            process.start()
            self.processes_pid.put(("Image_subProcesee", process.pid))
            self.processes.append(process)

    def close(self):
        # self.isRunning_subprocess.clear()
        for process in self.processes:
            process.stop()
            process.join()

    def run(self):
        self.isRunning_subprocess = multiprocessing.Event()
        self.isRunning_subprocess.set()

        self.cameraCapture = CameraCapture()
        self.result_images = multiprocessing.Queue(8)
        self.process_queue = multiprocessing.Queue(8)


        self.isRunning_OrderProcessor = multiprocessing.Event()
        self.isRunning_OrderProcessor.set()

        self.display_image_process = OrderProcessor(self.result_images, self.image_queue,self.statemachine,self.isRunning_OrderProcessor)

        self.cameraCapture.start()
        logger.info("CameraCapture is start")
        self.processes_pid.put(("Image Process",self.pid))
        time.sleep(1)
        self.display_image_process.start()
        self.processes_pid.put(("orderProcessor",self.pid))
        self.handle_image()
        self.get_photos()
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
