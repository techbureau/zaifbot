from abc import ABCMeta, abstractmethod
from time import sleep
from multiprocessing import Process
from zaifbot.bot_common.config import load_config
from zaifbot.bot_common.bot_const import PERIOD_SECS


class ProcessBase(Process, metaclass = ABCMeta):
    def __init__(self):
        super().__init__(name=self.get_name())
        self.config = load_config()

    def run(self):
        while True:
            sleep(PERIOD_SECS[self.config.system.sleep_time])
            #sleep(5)
            if self.is_started() is False:
                continue
            stop_process_flg = self.execute()
            if stop_process_flg:
                break

    @abstractmethod
    def get_name(self):
        raise NotImplementedError

    @abstractmethod
    def is_started(self):
        raise NotImplementedError

    @abstractmethod
    def execute(self):
        raise NotImplementedError
