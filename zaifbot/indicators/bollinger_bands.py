import time

from zaifbot.utils import truncate_time_at_period
from zaifbot.price.ohlc_prices import OhlcPrices
from talib import abstract as ab
from zaifbot.bot_common.bot_const import PERIOD_SECS, LIMIT_COUNT, LIMIT_LENGTH
from .base import Indicator

__all__ = ['BBands']


class BBands(Indicator):
    def __init__(self, currency_pair='btc_jpy', period='1d', length=LIMIT_LENGTH):
        self._currency_pair = currency_pair
        self._period = period
        self._length = min(length, LIMIT_LENGTH)

    def get_data(self, count=LIMIT_COUNT, lowbd=2, upbd=2, to_epoch_time=None):
        prices = self._bring_prices(count, to_epoch_time)

        if len(prices.index) == 0:
            return {'success': 0, 'error': 'failed to get ohlc price'}
        bbands = ab.BBANDS(prices, timeperiod=self._length, nbdevup=upbd, nbdevdn=lowbd, matype=0)
        ohlc_prices_result = prices.merge(bbands, left_index=True, right_index=True)
        ohlc_prices_result = ohlc_prices_result[-count:][['time', 'lowerband', 'upperband']]
        return \
            {'success': 1, 'return': {'bollinger_bands': ohlc_prices_result.to_dict(orient='records')}}

    # もしかしたらこのメソッドOhlcPricesだけでこと足りる可能性がある。
    def _bring_prices(self, count, to_epoch_time):
        to_epoch_time = to_epoch_time or int(time.time())
        count = min(count, LIMIT_COUNT)
        end_time = truncate_time_at_period(to_epoch_time, self._period)
        start_time = end_time - ((count + self._length) * PERIOD_SECS[self._period])
        return OhlcPrices(self._currency_pair, self._period, count, self._length).execute(start_time, end_time)
