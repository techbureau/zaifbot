import pandas as pd
from zaifbot.ohlc_prices import OhlcPrices
from pandas import DataFrame as DF
from talib import abstract as ab
from .base import Indicator

_HIGH = 'high'
_LOW = 'low'
_CLOSE = 'close'
_TIME = 'time'

__all__ = ['MACD']


class MACD(Indicator):
    def __init__(self, currency_pair='btc_jpy', period='1d', short=12, long=26, signal=9):
        self._currency_pair = currency_pair
        self._period = period
        self._short = min(short, self.MAX_LENGTH)
        self._long = min(long, self.MAX_LENGTH)
        self._signal = min(signal, self.MAX_LENGTH)

    def request_data(self, count=100, to_epoch_time=None):
        count = min(count, self.MAX_COUNT)
        count_needed = count + self._long + self._signal - 2
        ohlc_prices = OhlcPrices(self._currency_pair, self._period)
        df = DF(ohlc_prices.fetch_data(count_needed, to_epoch_time))
        macd = ab.MACD(df, price=_CLOSE, fastperiod=self._short, slowperiod=self._long, signalperiod=self._signal)
        macd = pd.concat([df[_TIME], macd], axis=1).dropna()
        return macd.astype(object).to_dict(orient='records')
