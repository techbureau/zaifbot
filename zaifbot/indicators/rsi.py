import pandas as pd
from zaifbot.bot_common.logger import logger
from pandas import DataFrame as DF
from talib import abstract as ab
from zaifbot.price.ohlc_prices import get_price_info

_HIGH = 'high'
_LOW = 'low'
_CLOSE = 'close'
_TIME = 'time'

__all__ = ['get_rsi']


def get_rsi(currency_pair='btc_jpy', period='1d', count=100, length=14, to_epoch_time=None):
    try:
        count_needed = count + length
        df = DF(get_price_info(currency_pair, period, count_needed, to_epoch_time))
        rsi = ab.RSI(df, price=_CLOSE, timeperiod=length).rename('rsi')
        rsi = pd.concat([df[_TIME], rsi], axis=1).dropna()
        return {'success': 1, 'return': {'RSIs': rsi.astype(object).to_dict(orient='records')}}
    except Exception as e:
        logger.error(e, exc_info=True)
        return {'success': 0, 'error': e}