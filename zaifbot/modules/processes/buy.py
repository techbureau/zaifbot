from abc import abstractmethod
from zaifbot.bot_common.utils import get_current_last_price
from zaifbot.modules.processes.process_common import ProcessBase


class BuyByPrice(ProcessBase):
    def __init__(self, target_value):
        self.target_value = target_value

    def get_name(self):
        return 'buy_by_price'

    def is_started(self):
        last_price = get_current_last_price()
        if last_price <= self.target_value:
            return True
        return False

    @abstractmethod
    def execute(self):
        raise NotImplementedError
