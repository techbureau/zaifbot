from abc import abstractmethod
from zaifbot.modules.auto_trade.process_common import ProcessBase


class Custom(ProcessBase):
    def __init__(self, name, func, is_started):
        super().__init__(func)
        self._is_started = is_started
        self._name = name

    def get_name(self):
        return self._name

    def is_started(self):
        return self._is_started(self.config)

    @abstractmethod
    def execute(self):
        raise NotImplementedError
