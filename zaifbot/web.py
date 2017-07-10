import random
import time

from zaifapi.api_error import ZaifApiNonceError, ZaifApiError
from zaifapi.impl import ZaifTradeApi, ZaifPublicApi
from zaifbot.common.logger import trade_logger, bot_logger
from zaifbot.dao.base import OrderLogsDao
from zaifbot.utils import get_keys

_RETRY_COUNT = 5
_WAIT_SECOND = 5

__all__ = ['BotPublicApi', 'BotTradeApi']


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


class BotTradeApi(ZaifTradeApi):
    def __init__(self, key=None, secret=None):
        if key is None and secret is None:
            key, secret = get_keys()
        elif type(key) is not type(secret):
            raise TypeError('only key or secret is set')

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
        def __params_preprocessing(**kwa):
            kwa['currency_pair'] = str(kwa['currency_pair'])
            kwa['action'] = str(kwa['action'])
            kwa['period'] = str(kwa['period'])
            return kwa
        kwargs = __params_preprocessing(**kwargs)

        trade_result = super().trade(**kwargs)
        order_log = {'order_id': trade_result['order_id'],
                     'currency_pair': kwargs.get('currency_pair'),
                     'action': kwargs.get('action'),
                     'price': kwargs.get('price'),
                     'amount': kwargs.get('amount'),
                     'limit': kwargs.get('limit', 0.0),
                     'received': trade_result['received'],
                     'remains': trade_result['remains'],
                     'comment': kwargs.get('comment', ''),
                     'time': int(time.time())}
        trade_logger.info('zaif received: {}'.format(order_log))

        dao = OrderLogsDao()
        dao.create(**order_log)
        return trade_result

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
        return super().last_price(currency_pair)

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
        return super().everything(func_name, currency_pair, params)
