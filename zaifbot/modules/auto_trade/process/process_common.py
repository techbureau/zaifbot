from abc import ABCMeta, abstractmethod
from time import sleep
from multiprocessing import Process
from zaifbot.bot_common.config import load_config


class ProcessBase(Process, metaclass=ABCMeta):
    def __init__(self, name):
        super().__init__(name=name)
        self.config = load_config()

    def run(self):
        while True:
            sleep(self.config.system.sleep_time)
            if self.is_started() is False:
                continue
            self.start()

    @abstractmethod
    def is_started(self):
        raise NotImplementedError

    @abstractmethod
    def start(self):
        raise NotImplementedError
