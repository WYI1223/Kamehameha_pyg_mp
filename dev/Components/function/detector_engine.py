import queue
from loguru import logger
from mediapipe import *

class attack_detector:
    _logger = None
    def set_logger(logger_):
        attack_detector._logger = logger_

    def __init__(self):
        self.queue = queue.Queue()
        self.intialize()
        pass

    def intialize(self):
        pass



    def action1(self):
        logger.info("execute action1")
        self.isSuccess = False
        pass

    def action2(self):
        logger.info("execute action2")
        pass

    def action3(self):
        logger.info("execute action3")
        pass

class jump_detector:

    def __init__(self):
        pass

    def intialize(self):
        pass

logger.info("")
logger.debug("")
class sit_detector:

    def __init__(self):
        pass

    def intialize(self):
        pass

