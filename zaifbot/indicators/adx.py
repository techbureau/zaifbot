import pandas as pd
from zaifbot.bot_common.logger import logger
from pandas import DataFrame as DF
from talib import abstract as ab
from zaifbot.price.ohlc_prices import get_price_info

_HIGH = 'high'
_LOW = 'low'
_CLOSE = 'close'
_TIME = 'time'

__all__ = ['ADX']


class ADX:
    def __init__(self, currency_pair='btc_jpy', period='1d', length=14):
        self._currency_pair = currency_pair
        self._period = period
        self._length = length

    def get_data(self, count=100, to_epoch_time=None):
        try:
            count_needed = 2 * self._length - 1 + count
            df = DF(get_price_info(self._currency_pair, self._period, count_needed, to_epoch_time))
            adx = ab.ADX(df, timeperiod=self._length, prices=[_HIGH, _LOW, _CLOSE], output_names=['adx']).rename('adx')
            adx = pd.concat([df[_TIME], adx], axis=1).dropna()
            return {'success': 1, 'return': {'ADXs': adx.astype(object).to_dict(orient='records')}}
        except Exception as e:
            logger.error(e, exc_info=True)
            return {'success': 0, 'error': e}
