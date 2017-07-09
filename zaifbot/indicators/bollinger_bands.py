import time

import pandas as pd
from pandas import DataFrame as DF
from talib import abstract as ab
from .indicator import Indicator
from .candle_sticks import CandleSticks
from zaifbot.common.period import Period


class BBands(Indicator):
    def __init__(self, currency_pair='btc_jpy', period='1d', length=25):
        self._currency_pair = currency_pair
        self._period = Period(period)
        self._length = min(length, self.MAX_LENGTH)

    def request_data(self, count=100, lowbd=2, upbd=2, to_epoch_time=None):
        to_epoch_time = to_epoch_time or int(time.time())
        count = self._calc_price_count(min(count, self.MAX_COUNT))
        end_time = self._period.truncate_sec(to_epoch_time)
        ohlcs = DF(CandleSticks(self._currency_pair, self._period).request_data(count, end_time))
        bbands = ab.BBANDS(ohlcs, timeperiod=self._length, nbdevup=upbd, nbdevdn=lowbd, matype=0).dropna()
        formatted_bbands = pd.concat([ohlcs['time'], bbands[['lowerband', 'upperband']]], axis=1).dropna().\
            astype(object).to_dict(orient='records')
        return formatted_bbands

    def _calc_price_count(self, count):
        return self._length + count - 1
