from abc import abstractmethod
from zaifbot.bot_common.utils import get_current_last_price
from zaifbot.modules.processes.process_common import ProcessBase


class SellByPrice(ProcessBase):
    def get_name(self):
        return 'sell_by_price'

    def is_started(self):
        last_price = get_current_last_price('btc_jpy')
        if last_price >= self.config.event.sell.target_value:
            return True
        return False

    @abstractmethod
    def execute(self):
        raise NotImplementedError
