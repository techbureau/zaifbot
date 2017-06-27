import random
import time

from zaifbot.dao.order_log import OrderLogsDao
from zaifapi.api_error import ZaifApiNonceError, ZaifApiError
from zaifapi.impl import ZaifTradeApi, ZaifPublicApi
from zaifbot.bot_common.logger import logger
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
                    logger.error(e, exc_info=True)
                    raise e
                continue
    return _wrapper


class BotTradeApi(ZaifTradeApi):
    def __init__(self, key=None, secret=None):
        if key is None and secret is None:
            key, secret = get_keys()
        elif type(key) is not type(secret):
            raise KeyError('only key or secret is set')

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
        # TODO: リファクタリングしたい
        def _make_dict(**items):
            return str(items)

        ret = super().trade(**kwargs)
        order_log = _make_dict(order_id=ret['order_id'],
                               currency_pair=kwargs.get('currency_pair'),
                               action=kwargs.get('action'),
                               price=kwargs.get('price'),
                               amount=kwargs.get('amount'),
                               limit=kwargs.get('limit', 0.0),
                               received=ret['received'],
                               remains=ret['remains'],
                               comment=kwargs.get('comment', ''))
        logger.info('order succeeded : {}'.format(order_log))
        dao = OrderLogsDao()
        record = eval(order_log)
        record['time'] = int(time.time())
        dao.create_data(record)

        return ret

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
