import pandas as pd
from zaifbot.exchange.currency_pairs import CurrencyPair
from zaifbot.exchange.period import Period
from .indicator import Indicator

_HIGH = 'high'
_LOW = 'low'
_CLOSE = 'close'
_TIME = 'time'


class RSI(Indicator):
    _NAME = 'rsi'

    def __init__(self, currency_pair='btc_jpy', period='1d', length=14):
        self._currency_pair = CurrencyPair(currency_pair)
        self._period = Period(period)
        self._length = self._bounded_length(length)

    def request_data(self, count=100, to_epoch_time=None):
        adjusted_count = self._adjust_count(count)
        candlesticks_df = self._get_candlesticks_df(self._currency_pair,
                                                    self._period,
                                                    adjusted_count,
                                                    to_epoch_time)

        rsi = self._execute_talib(candlesticks_df, price=_CLOSE, timeperiod=self._length).rename('rsi')
        formatted_rsi = self._formatting(candlesticks_df[_TIME], rsi)
        return formatted_rsi

    def _adjust_count(self, count):
        return self._bounded_count(count) + self._length

    @staticmethod
    def _formatting(time_df, rsi):
        rsi = pd.concat([time_df, rsi], axis=1).dropna()
        return rsi.astype(object).to_dict(orient='records')
