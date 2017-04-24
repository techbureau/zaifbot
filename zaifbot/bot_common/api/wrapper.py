import traceback
from zaifbot.bot_common.logger import logger
from zaifapi.impl import ZaifPrivateApi, ZaifPublicApi
from zaifbot.bot_common.save_trade_log import save_trade_log


def with_retry(func):
    def _wrapper(*args, **kwargs):
        for i in range(5):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())
        return _wrapper


class BotPrivateApi(ZaifPrivateApi):

    def __init__(self, key, secret, nonce=None):
        super().__init__(key, secret, nonce)

    @with_retry
    def active_orders(self, **kwargs):
        return super().active_orders(**kwargs)

    @with_retry
    def cancel_order(self, **kwargs):
        return super().cancel_order(**kwargs)

    @with_retry
    def deposit_history(self, **kwargs):
        return super().deposit_history(**kwargs)

    @with_retry
    def get_id_info(self):
        return super().get_id_info()

    @with_retry
    def get_info(self):
        return super().get_info()

    @with_retry
    def get_info2(self):
        return super().get_info2()

    @with_retry
    def get_personal_info(self):
        return super().get_personal_info()

    @with_retry
    def trade(self, **kwargs):
        return super().trade(**kwargs)

    @with_retry
    def trade_history(self, **kwargs):
        return super().trade_history(**kwargs)

    @with_retry
    def withdraw(self, **kwargs):
        return super().withdraw(**kwargs)

    @with_retry
    def withdraw_history(self, **kwargs):
        return super().withdraw_history(**kwargs)


class BotPublicApi(ZaifPublicApi):

    @with_retry
    def last_price(self, currency_pair):
        return super().last_price(currency_pair)

    @with_retry
    def ticker(self, currency_pair):
        return super().ticker(currency_pair)

    @with_retry
    def trades(self, currency_pair):
        return super().trades(currency_pair)

    @with_retry
    def depth(self, currency_pair):
        return super().depth(currency_pair)

    @with_retry
    def currency_pairs(self, currency_pair):
        return super().currency_pairs(currency_pair)

    @with_retry
    def currencies(self, currency):
        return super().currencies(currency)

    @with_retry
    def everything(self, func_name, currency_pair, params):
        return super().everything(func_name, currency_pair, params)
