import time

import psutil

from CombineVersion.MVC.EventManager import *
import CombineVersion.MVC.View as view
from CombineVersion.Processes.ImageProcess.ImageProcessor import *


class control(object):
    def __init__(self, evManager, model):
        self.evManager = evManager
        evManager.RegisterListener(self)

        self.model = model
        self.pageinitilized = False

    def initialize(self):
        """
        Initialize view.
        """
        self.graphics = view.UI_View(self.evManager, self.model)
        self.graphics.initialize()

    def input_event(self):
        pass
    def notify(self, event):
        """
        Receive events posted to the message queue.
        """
        if isinstance(event, InitializeEvent):
            self.initialize()

        # if the state is changing, reset the pageinitilized flag
        elif isinstance(event, StateChangeEvent):
            self.pageinitilized = False
            print("State change event")

        elif isinstance(event, TickEvent):

            self.model.currentstate = self.model.state.peek()
            if self.pageinitilized == False:
                """
                Initialize new page
                """
                self.model.ImageProcess = ImageProcessor(self.model.image_queue, self.model.STATE_MACHINE, self.model.processes_pid)
                self.model.ImageProcess.start()

                print("New page initialized")

                self.pageinitilized = True

            """
            Handle all Business Logic
            """


            if self.model.STATE_MACHINE.value == 0:
                print("STATE_MACHINE: ", self.model.STATE_MACHINE.value)


                time.sleep(1)
                def is_process_alive(pid):
                    return psutil.pid_exists(pid)

                for i in range(5):
                    info, process_pid = self.model.processes_pid.get()
                    status = "仍在运行" if is_process_alive(process_pid) else "已经结束"
                    print(f"进程 {process_pid} ({info}) {status}")
                    self.model.processes_pid.put((info, process_pid))


                self.model.ImageProcess.join()
                self.graphics.quit_pygame()
                self.evManager.Post(QuitEvent())
                # print("STATE_MACHINE: ", self.model.STATE_MACHINE.value)


            # Get camera image from CV2
            # self.model.success, self.model.img = self.model.CV2_class.read_camera()  # read camera

            # if self.model.success:
            #     self.model.handle_image()
            #     """
            #     Tell view to render after all Business Logic
            #     """
            #     self.graphics.render()
            self.input_event()

