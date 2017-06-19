import time

from zaifbot.price.ohlc_prices import OhlcPrices
from talib import abstract as ab
from zaifbot.bot_common.bot_const import PERIOD_SECS, LIMIT_COUNT, LIMIT_LENGTH
from .base import Indicator
from zaifbot.utils import truncate_time_at_period

__all__ = ['EMA', 'SMA']


class MA(Indicator):
    def __init__(self, currency_pair='btc_jpy', period='1d', length=LIMIT_LENGTH):
        self._currency_pair = currency_pair
        self._period = period
        self._length = min(length, LIMIT_LENGTH)

    def get_data(self, count):
        raise NotImplementedError

    # todo: priceから返却される値の数がおかしい？
    def _bring_prices(self, count, to_epoch_time):
        to_epoch_time = to_epoch_time or int(time.time())
        count = min(count, LIMIT_COUNT)
        end_time = truncate_time_at_period(to_epoch_time, self._period)
        tl_start_time = end_time - ((count + self._length) * PERIOD_SECS[self._period])
        return OhlcPrices(self._currency_pair, self._period, count, self._length).execute(tl_start_time, end_time)


class EMA(MA):
    def __init__(self, currency_pair='btc_jpy', period='1d', length=LIMIT_LENGTH):
        super().__init__(currency_pair, period, length)

    def get_data(self, count=LIMIT_COUNT, to_epoch_time=None):
        count = min(count, LIMIT_COUNT)

        ohlc_prices = self._bring_prices(count, to_epoch_time)
        if len(ohlc_prices.index) == 0:
            return {'success': 0, 'error': 'failed to get ohlc price'}

        ema = ab.EMA(ohlc_prices, timeperiod=self._length).dropna()
        ohlc_prices_result = \
            ohlc_prices.merge(ema.to_frame(), left_index=True, right_index=True) \
                .rename(columns={0: 'ema'}).to_dict(orient='records')
        # todo: 戻り値のフォーマットの修正
        return {'success': 1, 'return': {'ema': ohlc_prices_result}}


class SMA(MA):
    def __init__(self, currency_pair='btc_jpy', period='1d', length=LIMIT_LENGTH):
        super().__init__(currency_pair, period, length)

    def get_data(self, count=LIMIT_COUNT, to_epoch_time=None):
        count = min(count, LIMIT_COUNT)
        ohlc_prices = self._bring_prices(count, to_epoch_time)

        if len(ohlc_prices.index) == 0:
            return {'success': 0, 'error': 'failed to get ohlc price'}

        sma = ab.SMA(ohlc_prices, timeperiod=self._length).dropna()

        ohlc_prices_result = \
            ohlc_prices.merge(sma.to_frame(), left_index=True, right_index=True) \
                .rename(columns={0: 'sma'}).to_dict(orient='records')
        # todo: 戻り値のフォーマットの修正
        return {'success': 1, 'return': {'sma': ohlc_prices_result}}
