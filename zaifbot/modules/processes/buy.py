from abc import abstractmethod
from zaifbot.modules.processes.process_common import ProcessBase
from zaifbot.modules.utils import get_current_last_price


class BuyByPrice(ProcessBase):
    def __init__(self, target_value):
        self._target_value = target_value

    def get_name(self):
        return 'buy_by_price'

    def is_started(self, currency_pair):
        last_price = get_current_last_price(currency_pair)
        if last_price <= self._target_value:
            return True
        return False

    @abstractmethod
    def execute(self):
        raise NotImplementedError
