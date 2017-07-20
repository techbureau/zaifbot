import pandas as pd
from pandas import DataFrame as DF
from talib import abstract as ab
from zaifbot.exchange.candle_sticks import CandleSticks
from zaifbot.exchange.period import Period
from zaifbot.utils import int_time
from .indicator import Indicator


class BBands(Indicator):
    def __init__(self, currency_pair='btc_jpy', period='1d', length=25):
        self._currency_pair = currency_pair
        self._period = Period(period)
        self._length = min(length, self.MAX_LENGTH)

    def request_data(self, count=100, lowbd=2, upbd=2, to_epoch_time=None):
        to_epoch_time = to_epoch_time or int_time()
        adjusted_count = self._get_adjusted_count(count)
        end_time = self._period.truncate_sec(to_epoch_time)

        candlesticks = DF(CandleSticks(self._currency_pair, self._period).request_data(adjusted_count, end_time))

        bbands = ab.BBANDS(candlesticks, timeperiod=self._length, nbdevup=upbd, nbdevdn=lowbd, matype=0).dropna()
        formatted_bbands = pd.concat([candlesticks['time'], bbands[['lowerband', 'upperband']]], axis=1).dropna().\
            astype(object).to_dict(orient='records')
        return formatted_bbands

    def _get_adjusted_count(self, count):
        count = min(count, self.MAX_COUNT)
        return self._length + count - 1
