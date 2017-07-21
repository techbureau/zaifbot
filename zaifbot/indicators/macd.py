import pandas as pd


from .indicator import Indicator

_HIGH = 'high'
_LOW = 'low'
_CLOSE = 'close'
_TIME = 'time'


class MACD(Indicator):
    def __init__(self, currency_pair='btc_jpy', period='1d', short=12, long=26, signal=9):
        self._currency_pair = currency_pair
        self._period = period
        self._short = self._bounded_length(short)
        self._long = self._bounded_length(long)
        self._signal = self._bounded_length(signal)

    def request_data(self, count=100, to_epoch_time=None):
        adjusted_count = self._get_adjusted_count(count)
        candlesticks_df = self._get_candlesticks_df(self._currency_pair,
                                                    self._period,
                                                    adjusted_count,
                                                    to_epoch_time)

        macd = self._execute_talib(candlesticks_df, price=_CLOSE, fastperiod=self._short, slowperiod=self._long, signalperiod=self._signal)

        formatted_macd = self._formatting(candlesticks_df[_TIME], macd)
        return formatted_macd

    def _get_adjusted_count(self, count):
        return self._bounded_count(count) + self._long + self._signal - 2
    
    @staticmethod
    def _formatting(time_df, macd):
        macd = pd.concat([time_df, macd], axis=1).dropna()
        return macd.astype(object).to_dict(orient='records')