"""
每个文件中记录日志所需的代码
from loguru import logger
def set_logger(logger_):
    Worker._logger = logger_
"""

import os.path
from loguru import logger
from multiprocessing import Pool, Process

class Worker:

    _logger = None
    @staticmethod
    def set_logger(logger_):
        Worker._logger = logger_

    def work(self, x):
        self._logger.info("Square rooting {}", x)
        return x**0.5
def set_logger(logger_):
    global logger
    logger = logger_

def work(x):
    logger.info("Square rooting {}", x)
    return x**0.5

#日志系统的方法
def log():
    logger.remove()
    #创建日志目录以及日志文件
    logDir = os.path.expanduser('Log')
    logFile = os.path.join(logDir, "Dragonball_{time}.log")
    if not os.path.exists(logDir):
        os.mkdir(logDir)

    #设置日志储存的规则（储存到logfile中，字节大小为200kb，压缩成zip文件，以队列方式储存）
    logger.add(logFile, rotation="200KB", compression="zip", enqueue=True, backtrace=True)

    worker = Worker()

    for i in range(100):
    #两个进程池
        with Pool(4, initializer=worker.set_logger, initargs=(logger,)) as pool:
            results = pool.map(worker.work, [1, 10, 100])

        with Pool(4, initializer=set_logger, initargs=(logger,)) as pool:
            results = pool.map(work, [1, 10, 100])




if __name__ == "__main__":
    log()

