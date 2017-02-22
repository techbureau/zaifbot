from abc import abstractmethod
from zaifbot.bot_common.utils import get_current_last_price
from zaifbot.modules.processes.process_common import ProcessBase


class Buy(ProcessBase):
    def get_name(self):
        return 'buy'

    def is_started(self):
        last_price = get_current_last_price()
        if last_price <= self.config.event.buy.target_value:
            return True
        return False

    @abstractmethod
    def execute(self):
        raise NotImplementedError
