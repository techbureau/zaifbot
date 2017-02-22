from abc import abstractmethod
from zaifbot.bot_common.utils import get_current_last_price
from zaifbot.modules.auto_trade.process_common import ProcessBase


class LossCut(ProcessBase):
    def get_name(self):
        return 'loss_cut'

    def is_started(self):
        last_price = get_current_last_price()
        if last_price <= self.config.event.loss_cut.target_value:
            return True
        return False

    @abstractmethod
    def execute(self):
        raise NotImplementedError
