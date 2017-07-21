import pandas as pd
from zaifbot.exchange.period import Period
from .indicator import Indicator


class BBANDS(Indicator):
    _NAME = 'bbands'

    def __init__(self, currency_pair='btc_jpy', period='1d', length=25):
        self._currency_pair = currency_pair
        self._period = Period(period)
        self._length = self._bounded_length(length)

    def name(self):
        return self._NAME

    def request_data(self, count=100, lowbd=2, upbd=2, to_epoch_time=None):
        adjusted_count = self._get_adjusted_count(count)
        candlesticks_df = self._get_candlesticks_df(self._currency_pair,
                                                    self._period,
                                                    adjusted_count,
                                                    to_epoch_time)
        bbands = self._execute_talib('bbands', candlesticks_df, timeperiod=self._length, nbdevup=upbd, nbdevdn=lowbd, matype=0).dropna()
        formatted_bbands = self._formatting(candlesticks_df['time'], bbands)
        return formatted_bbands

    def _get_adjusted_count(self, count):
        count = self._bounded_count(count)
        return self._length + count - 1

    @staticmethod
    def _formatting(time_df, bbands):
        bbands = bbands.dropna()
        formatted_bbands = pd.concat([time_df, bbands[['lowerband', 'upperband']]], axis=1).dropna().astype(object).to_dict(orient='records')
        return formatted_bbands
