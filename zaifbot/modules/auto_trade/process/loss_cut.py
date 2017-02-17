from zaifbot.bot_common.utils import get_current_last_price
from zaifapi import ZaifPrivateApi
from .process_common import ProcessBase


class LossCut(ProcessBase):
    def __init__(self):
        super().__init__(name='loss cut process')

    def is_started(self):
        last_price = get_current_last_price(self.config.system.currency_pair)
        if last_price <= self.config.event.loss_cut.target_value:
            return True
        return False

    def start(self):
        api = ZaifPrivateApi(self.config.api_keys.key, self.config.api_keys.secret)
        api.trade(currency_pair=self.config.system.currency_pair,

                  )
        schema_keys = ['currency_pair', 'action', 'price', 'amount', 'limit', 'is_token']