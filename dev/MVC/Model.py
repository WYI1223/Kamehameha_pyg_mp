import queue
from loguru import logger
from dev.MVC.EventManager import *

# State machine constants for the StateMachine class below
STATE_CV = 1
STATE_POSE = 2
STATE_HAND = 3
STATE_FACEMESH = 4
STATE_HOLISTIC = 5


class ModelEngine(object):
    def __init__(self, evManager):
        self.img = None # current image
        self.evManager = evManager
        evManager.RegisterListener(self)
        self.state = StateMachine_level_1()

        self.first_state = STATE_CV

        self.load_settings_and_data()

        self.result_images = queue.Queue()

    def load_settings_and_data(self):
        pass

    def result_callback(self, result):
        # 将结果添加到队列
        self.result_images.put(result)
        if self.input_order.value % 50 == 0:
            logger.info("result_images size:{}", self.result_images.qsize())


    def notify(self, event):
        """
        Called by an event in the message queue.
        """

        if isinstance(event, QuitEvent):
            self.running = False

        if isinstance(event, StateChangeEvent):
            # pop request
            if not event.state:
                # false if no more states are left
                if not self.state.pop():
                    self.evManager.Post(QuitEvent())
            else:
                # push a new state on the stack
                self.state.push(event.state)

    def run(self):
        """
        Starts the game engine loop.

        This pumps a Tick event into the message queue for each loop.
        The loop ends when this object hears a QuitEvent in notify().
        """
        self.running = True
        self.evManager.Post(InitializeEvent())
        self.state.push(self.first_state)

        while self.running:
            newTick = TickEvent()
            self.evManager.Post(newTick)


class StateMachine_level_1(object):
    """
    Manages a stack based state machine.
    peek(), pop() and push() perform as traditionally expected.
    peeking and popping an empty stack returns None.
    """

    def __init__(self):
        self.statestack = []

    def peek(self):
        """
        Returns the current state without altering the stack.
        Returns None if the stack is empty.
        """
        try:
            return self.statestack[-1]
        except IndexError:
            # empty stack
            return None

    def pop(self):
        """
        Returns the current state and remove it from the stack.
        Returns None if the stack is empty.
        """
        try:
            self.statestack.pop()
            print(self.statestack)
            return len(self.statestack) > 0
        except IndexError:
            # empty stack
            return None

    def push(self, state):
        """
        Push a new state onto the stack.
        Returns the pushed value.
        """
        self.statestack.append(state)
        print(self.statestack)
        return state