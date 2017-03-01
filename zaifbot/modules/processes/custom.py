from abc import abstractmethod
from zaifbot.modules.processes.process_common import ProcessBase


class Custom(ProcessBase):
    @abstractmethod
    def get_name(self):
        raise NotImplementedError

    @abstractmethod
    def is_started(self):
        raise NotImplementedError

    @abstractmethod
    def execute(self):
        raise NotImplementedError
