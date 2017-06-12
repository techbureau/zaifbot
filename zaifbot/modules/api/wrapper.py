import traceback
import time
import random
from zaifbot.bot_common.logger import logger
from zaifapi.impl import ZaifTradeApi, ZaifPublicApi
from zaifapi.api_error import ZaifApiNonceError, ZaifApiError
from zaifbot.bot_common import get_keys

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
        def _make_dict(**items):
            return str(items)

        ret = super().trade(**kwargs)
        log_msg = _make_dict(id=ret['order_id'],
                             currency_pair=kwargs.get('currency_pair'),
                             action=kwargs.get('action'),
                             price=kwargs.get('price'),
                             acount=kwargs.get('amount'),
                             limit=kwargs.get('limit', 0.0),
                             received=ret['received'],
                             remains=ret['remains'],)
        logger.info('order succeeded : {}'.format(log_msg))

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
