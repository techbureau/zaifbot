from abc import abstractmethod
from zaifbot.bot_common.utils import get_current_last_price
from zaifbot.modules.processes.process_common import ProcessBase


class SellByPrice(ProcessBase):
    def __init__(self, target_value):
        self._target_value = target_value

    def get_name(self):
        return 'sell_by_price'

    def is_started(self):
        last_price = get_current_last_price()
        if last_price >= self._target_value:
            return True
        return False

    @abstractmethod
    def execute(self):
        raise NotImplementedError
