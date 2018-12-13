import random
import time
import requests
import json
import inspect

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


class BotChartApi:
    _API_URL = 'https://zaif.jp/zaif_chart_api/v1/{}'

    def history(self, currency_pair, period, from_sec, to_sec):
        # ensure 'str' type
        currency_pair = str(currency_pair)
        period = str(period)

        self._validate_int(from_sec)
        self._validate_int(to_sec)

        resolution = self._period_to_resolution(period)
        params = {
            'symbol': currency_pair,
            'resolution': resolution,
            'from': from_sec,
            'to': to_sec
        }
        return self._execute_api(inspect.currentframe().f_code.co_name, params)

    def _execute_api(self, func_name, params=None):
        url = self._API_URL.format(func_name)
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception('return status code is {}'.format(response.status_code))
        ohlc_data = json.loads(json.loads(response.text))['ohlc_data']
        return list(map(self._time_digits_adjust, ohlc_data))

    @staticmethod
    def _period_to_resolution(period):
        conversion_table = {
            '1m': '1',
            '5m': '5',
            '15m': '15',
            '30m': '30',
            '1h': '60',
            '4h': '240',
            '8h': '480',
            '12h': '720',
            '1d': 'D',
        }
        resolution = conversion_table.get(period, None)
        if not resolution:
            raise ValueError('error: Unexpected period')
        return resolution

    @staticmethod
    def _validate_int(sec):
        if not isinstance(sec, int):
            raise TypeError("Only 'int' is acceptable")
        return

    # fixme: not good code
    @staticmethod
    def _time_digits_adjust(an_olhc_data):
        an_olhc_data['time'] = int(an_olhc_data['time'] / 1000)
        return an_olhc_data
