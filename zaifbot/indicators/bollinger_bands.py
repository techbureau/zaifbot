import time

from zaifbot.indicators.moving_average import get_end_time
from zaifbot.price.ohlc_prices import OhlcPrices
from talib import abstract as ab
from zaifbot.bot_common.bot_const import PERIOD_SECS, LIMIT_COUNT, LIMIT_LENGTH
from .base import Indicator

__all__ = ['BBands']


class BBands(Indicator):
    def __init__(self, currency_pair='btc_jpy', period='1d', length=LIMIT_LENGTH):
        self._currency_pair = currency_pair
        self._period = period
        self._length = length

    def get_data(self, count=LIMIT_COUNT, lowbd=2, upbd=2, to_epoch_time=None):
        to_epoch_time = int(time.time()) if to_epoch_time is None else to_epoch_time
        count = min(count, LIMIT_COUNT)
        length = min(self._length, LIMIT_LENGTH)
        end_time = get_end_time(to_epoch_time, self._period)
        start_time = end_time - ((count + length) * PERIOD_SECS[self._period])
        ohlc_prices = OhlcPrices(self._currency_pair, self._period, count, length)
        ohlc_prices_result = ohlc_prices.execute(start_time, end_time)

        if len(ohlc_prices_result.index) == 0:
            return {'success': 0, 'error': 'failed to get ohlc price'}
        bbands = ab.BBANDS(ohlc_prices_result, timeperiod=length, nbdevup=upbd, nbdevdn=lowbd, matype=0)
        ohlc_prices_result = ohlc_prices_result.merge(bbands, left_index=True, right_index=True)
        ohlc_prices_result = ohlc_prices_result[-count:][['time', 'lowerband', 'upperband']]
        return \
            {'success': 1, 'return': {'bollinger_bands': ohlc_prices_result.to_dict(orient='records')}}
