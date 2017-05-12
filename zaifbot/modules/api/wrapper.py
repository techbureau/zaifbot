import traceback
import time
import random
from zaifbot.bot_common.logger import logger
from zaifapi.impl import ZaifTradeApi, ZaifPublicApi
from zaifapi.api_error import ZaifApiNonceError, ZaifApiError
from zaifbot.modules.utils import get_round_price

_RETRY_COUNT = 5
_WAIT_SECOND = 5


def _with_retry(func):
    def _wrapper(self, *args, **kwargs):
        for i in range(_RETRY_COUNT):
            try:
                return func(self, *args, **kwargs)
            except ZaifApiError as e:
                logger.error(e)
                logger.error(traceback.format_exc())
                raise e
            except ZaifApiNonceError as e:
                logger.error(e)
                logger.error(traceback.format_exc())
                a = random.uniform(0.5, 1.0)
                time.sleep(a)
                continue
            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())
                time.sleep(_WAIT_SECOND)
                continue
    return _wrapper


class BotTradeApi(ZaifTradeApi):
    def __init__(self, key, secret):
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
    def buy(self, **kwargs):
        price = get_round_price(kwargs['currency_pair'],
                                kwargs['price'],
                                is_buy=True)
        kwargs['price'] = price
        kwargs['action'] = 'bid'
        return super().trade(**kwargs)

    @_with_retry
    def sell(self, **kwargs):
        price = get_round_price(kwargs['currency_pair'],
                                kwargs['price'],
                                is_buy=False)
        kwargs['price'] = price
        kwargs['action'] = 'asc'
        return super().trade(**kwargs)

    @_with_retry
    def trade(self, **kwargs):
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
        last_price = super().last_price(currency_pair)
        last_price['last_price'] = _price_adjustment(currency_pair,
                                                     last_price['last_price'])
        return last_price

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


# TODO: いずれ消したメソッド
def _price_adjustment(currency_pair, price):
    if currency_pair == 'btc_jpy':
        return int(price)
    else:
        return price
