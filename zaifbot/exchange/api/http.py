import random
import time

from zaifapi.api_error import ZaifApiNonceError, ZaifApiError
from zaifapi.impl import ZaifTradeApi, ZaifPublicApi

from zaifbot.logger import bot_logger
from zaifbot.config import get_keys

_RETRY_COUNT = 5
_WAIT_SECOND = 5


def _with_retry(func):
    def _wrapper(self, *args, **kwargs):
        for i in range(_RETRY_COUNT):
            try:
                return func(self, *args, **kwargs)
            except (ZaifApiError, ZaifApiNonceError) as e:
                a = random.uniform(0.1, 0.5)
                time.sleep(a)
                if i >= _RETRY_COUNT - 1:
                    bot_logger.exception(e)
                    raise e
                continue
    return _wrapper


__all__ = ['BotPublicApi', 'BotTradeApi']


class BotTradeApi(ZaifTradeApi):
    def __init__(self, key=None, secret=None):
        if key is None and secret is None:
            key, secret = get_keys()
        super().__init__(key, secret)

    @_with_retry
    def active_orders(self, **kwargs):
        return super().active_orders(**kwargs)

    @_with_retry
    def cancel_order(self, **kwargs):
        return super().cancel_order(**kwargs)

    @_with_retry
    def deposit_history(self, **kwargs):
        return super().deposit_history(**kwargs)

    @_with_retry
    def get_id_info(self):
        return super().get_id_info()

    @_with_retry
    def get_info(self):
        return super().get_info()

    @_with_retry
    def get_info2(self):
        return super().get_info2()

    @_with_retry
    def get_personal_info(self):
        return super().get_personal_info()

    @_with_retry
    def trade(self, **kwargs):
        def __params_pre_processing(**kwa):
            kwa['currency_pair'] = str(kwa['currency_pair'])
            kwa['action'] = str(kwa['action'])
            kwa['period'] = str(kwa['period'])
            return kwa
        kwargs = __params_pre_processing(**kwargs)
        return super().trade(**kwargs)

    @_with_retry
    def trade_history(self, **kwargs):
        return super().trade_history(**kwargs)

    @_with_retry
    def withdraw(self, **kwargs):
        return super().withdraw(**kwargs)

    @_with_retry
    def withdraw_history(self, **kwargs):
        return super().withdraw_history(**kwargs)


class BotPublicApi(ZaifPublicApi):

    @_with_retry
    def last_price(self, currency_pair):
        return super().last_price(str(currency_pair))

    @_with_retry
    def ticker(self, currency_pair):
        return super().ticker(currency_pair)

    @_with_retry
    def trades(self, currency_pair):
        return super().trades(currency_pair)

    @_with_retry
    def depth(self, currency_pair):
        return super().depth(currency_pair)

    @_with_retry
    def currency_pairs(self, currency_pair):
        return super().currency_pairs(currency_pair)

    @_with_retry
    def currencies(self, currency):
        return super().currencies(currency)

    @_with_retry
    def everything(self, func_name, currency_pair, params):
        currency_pair = str(currency_pair)
        if params.get('period'):
            params['period'] = str(params['period'])
        return super().everything(func_name, currency_pair, params)
