from abc import abstractmethod
from zaifbot.bot_common.utils import get_current_last_price
from zaifbot.modules.auto_trade.process_common import ProcessBase


class AdditionalPurchase(ProcessBase):
    def get_name(self):
        return 'additional_purchase'

    def is_started(self):
        last_price = get_current_last_price(self.config.system.currency_pair)
        if last_price <= self.config.event.additional_purchase.target_value:
            return True
        return False

    @abstractmethod
    def execute(self):
        raise NotImplementedError
