import pandas as pd
from zaifbot.bot_common.logger import logger
from pandas import DataFrame as DF
from talib import abstract as ab
from zaifbot.price.ohlc_prices import get_price_info

_HIGH = 'high'
_LOW = 'low'
_CLOSE = 'close'
_TIME = 'time'


__all__ = ['get_macd']


def get_macd(currency_pair='btc_jpy', period='1d', count=100, short=12, long=26, signal=9, to_epoch_time=None):
    try:
        count_needed = count + long + signal - 2
        df = DF(get_price_info(currency_pair, period, count_needed, to_epoch_time))
        macd = ab.MACD(df, price=_CLOSE, fastperiod=short, slowperiod=long, signalperiod=signal)
        macd = pd.concat([df[_TIME], macd], axis=1).dropna()
        return {'success': 1, 'return': {'MACDs':  macd.astype(object).to_dict(orient='records')}}
    except Exception as e:
        logger.error(e, exc_info=True)
        return {'success': 0, 'error': e}